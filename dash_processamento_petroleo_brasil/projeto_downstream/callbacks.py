"""
callbacks.py
------------
O "Cérebro" da aplicação. Aqui definimos como o dashboard reage às interações do usuário.
A lógica foi dividida em dois callbacks distintos para maximizar a performance:
1. Filtra os dados pesados e salva na memória (Store).
2. Lê os dados da memória e desenha os gráficos (Plotly).
"""

from dash import Input, Output, State, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_manager import df_base, MIN_ANO, MAX_ANO

# =====================================================================
# FUNÇÕES UTILITÁRIAS
# =====================================================================
def figura_vazia(msg: str) -> go.Figure:
    """Gera um frame visualmente agradável avisando que não há dados no filtro selecionado."""
    return go.Figure().update_layout(
        title={"text": f"<i>{msg}</i>", "x": 0.5, "y": 0.5, "xanchor": "center", "yanchor": "middle"},
        xaxis={"visible": False}, yaxis={"visible": False},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": "#8E9BAE"}
    )

def fmt_br(valor) -> str:
    """Função resiliente para formatar números no padrão brasileiro (1.000,00) sem causar crash caso receba Nulos."""
    if pd.isna(valor) or valor == float('inf') or valor == float('-inf'): return "0,00"
    return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================================
# REGISTRO DE CALLBACKS
# =====================================================================
def registrar_callbacks():
    
    # --- CALLBACK 1: MOTOR DE FILTRAGEM (BACKEND) ---
    @callback(
        Output('store-dados', 'data'),
        [Input("filtro-ano-inicio", "value"), 
         Input("filtro-ano-fim", "value"), 
         Input("filtro-materia", "value"), 
         Input("filtro-estado", "value")]
    )
    def filtrar_dados(ano_inicio, ano_fim, materias, estados):
        """Aplica máscaras booleanas no Pandas (muito rápidas) e salva em JSON na Store."""
        if df_base.empty or not materias: return []
        
        # Tratamento defensivo: previne quebras se o usuário apagar o ano da caixa
        ano_inicio = ano_inicio if ano_inicio else df_base['ano'].min()
        ano_fim = ano_fim if ano_fim else df_base['ano'].max()
        
        # Se o usuário errar e botar ano inicial maior que o final, invertemos automaticamente
        if ano_inicio > ano_fim:
            ano_inicio, ano_fim = ano_fim, ano_inicio
            
        mask = (df_base['ano'] >= ano_inicio) & (df_base['ano'] <= ano_fim) & (df_base['materia_prima'].isin(materias))
        
        if estados:
            mask &= df_base['unidade_da_federacao'].isin(estados)
            
        # Retorna apenas as colunas vitais para não sobrecarregar a rede (I/O)
        cols_uteis = ['data', 'unidade_da_federacao', 'refinaria', 'materia_prima', 'processado']
        return df_base.loc[mask, cols_uteis].to_dict('records')

    # --- CALLBACK 2: RENDERIZAÇÃO GRÁFICA (FRONTEND) ---
    @callback(
        [Output("fig_linha", "figure"), Output("fig_tree", "figure"), Output("fig_rosca", "figure")],
        [Input('store-dados', 'data')],
        # State é usado para LER valores da tela sem disparar o callback quando eles mudam 
        # (quem dispara é o input da Store, logo após filtrar)
        [State("filtro-ano-inicio", "value"), State("filtro-ano-fim", "value")]
    )
    def atualizar_graficos(dados_em_memoria, ano_inicio, ano_fim):
        if not dados_em_memoria:
            return figura_vazia("Sem dados no período"), figura_vazia("Sem dados no período"), figura_vazia("Sem dados no período")

        df = pd.DataFrame(dados_em_memoria)
        
        # POLIMENTO DE DADOS PARA APRESENTAÇÃO
        # Normalização de texto e garantia da hierarquia visual na legenda/hover
        df['materia_prima'] = df['materia_prima'].str.title()
        ordem_materias = ["Petróleo Nacional", "Petróleo Importado", "Outras Cargas"]
        cores_map = {
            "Petróleo Nacional": "#831E70", 
            "Petróleo Importado": "#F38370", 
            "Outras Cargas": "#FBC28A"
        }

        # Criação de string inteligente para os títulos
        ano_inicio = ano_inicio if ano_inicio else MIN_ANO
        ano_fim = ano_fim if ano_fim else MAX_ANO
        str_periodo = f"({ano_inicio} - {ano_fim})"

        # ==========================================
        # 1. FIGURA DE LINHA (Série Temporal)
        # ==========================================
        df_linha = df.groupby(['data', 'materia_prima'], as_index=False, observed=True)['processado'].sum()
        df_linha["processado_br"] = df_linha["processado"].apply(fmt_br)

        fig_linha = px.line(
            df_linha, x='data', y='processado', color="materia_prima",
            custom_data=["processado_br"],
            category_orders={"materia_prima": ordem_materias},
            color_discrete_map=cores_map,
            title=f'Evolução Temporal do Processamento de Petróleo {str_periodo}',
            template='plotly_dark',
            labels={"materia_prima": "Matéria Prima:"}
        )
        fig_linha.update_layout(
            xaxis_title="Período", yaxis_title="Volume Processado (m³)",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", # Fundos transparentes para herdar do CSS
            margin={"r": 10, "t": 50, "l": 10, "b": 10},
            hoverlabel=dict(bgcolor="#111111", font_color="#F2F5FA", bordercolor="#283442"),
            xaxis=dict(
                showspikes=True, # Cria a linha guia do mouse (Mira)
                spikedash="dot",
                spikecolor="#111111"
            )
        )
        fig_linha.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Processado: %{customdata[0]} m³<extra></extra>")

        # ==========================================
        # 2. FIGURA TREEMAP (Share Regional)
        # ==========================================
        df_share = df.groupby(['unidade_da_federacao', 'refinaria'], as_index=False, observed=True)['processado'].sum()
        df_share = df_share[df_share['processado'] > 0]
        # Não aplicamos fmt_br aqui para permitir que o Plotly faça os cálculos de rool-up agregados dos Nós (Ex: São Paulo, Brasil).

        fig_tree = px.treemap(
            df_share, path=[px.Constant("Brasil"), 'unidade_da_federacao', 'refinaria'],
            values='processado',
            title=f"Concentração do Refino Nacional {str_periodo}",
            color='processado', color_continuous_scale='Sunsetdark',
            template='plotly_dark'
        )
        fig_tree.update_traces(
            root_color="lightgrey",
            texttemplate="<b>%{label}</b><br>%{value} m³",
            hovertemplate="<b>%{label}</b><br><b>Processado:</b> %{value} m³<br><b>Participação:</b> %{percentParent:.2%}<extra></extra>",
            marker=dict(line=dict(color='#060606', width=1)) # Borda suave para separar os retângulos
        )
        fig_tree.update_layout(
            separators=",.", # Força padrão PT-BR nas agregações dinâmicas do Plotly
            margin=dict(t=50, l=25, r=25, b=25),
            hoverlabel=dict(bgcolor="rgba(17,17,17,0.95)", font_color="white", font_size=13, bordercolor="#283442"),
            coloraxis_colorbar=dict(title="Vol. Process. (m³)", thickness=15),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )

        # ==========================================
        # 3. FIGURA ROSCA (Mix de Carga)
        # ==========================================
        df_rosca = df.groupby("materia_prima", as_index=False, observed=True)["processado"].sum()
        df_rosca = df_rosca[df_rosca['processado'] > 0]

        fig_rosca = px.pie(
            df_rosca, values='processado', names='materia_prima', hole=0.55,
            title=f'Tipo de Matéria Prima {str_periodo}',
            template='plotly_dark', color='materia_prima',
            category_orders={"materia_prima": ordem_materias},
            color_discrete_map=cores_map
        )
        fig_rosca.update_traces(
            textposition='outside', textinfo='percent+label',
            hovertemplate="<span style='color:white'><b>%{label}</b><br>Volume: %{value:,.2f} m³</span><extra></extra>",
            marker=dict(line=dict(color='#060606', width=1))
        )
        fig_rosca.update_layout(
            separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )

        return fig_linha, fig_tree, fig_rosca
"""
Dashboard Interativo: DOCHMO - Análise de ITBI (Fortaleza-CE)
Desenvolvido por: Douglas Chaves Moura

Arquitetura:
- Frontend: Dash, Dash Bootstrap Components (Cyborg Theme), Dash Mantine Components.
- Backend: Pandas (Vetorização) e Plotly Express/Graph Objects.
- State Management: Client-side storage (dcc.Store) para otimização de performance.
"""

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =====================================================================
# 1. CONFIGURAÇÃO GLOBAL E TEMATIZAÇÃO
# =====================================================================
# Inicializa o app com o grid do Bootstrap em Dark Mode (CYBORG)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], title="DOCHMO - Análise de ITBI")
server = app.server # Exposto para deploy em produção (ex: Gunicorn/Render)

# Paleta customizada (Mantine): Garante que os componentes de UI (Slider, Selects) 
# respeitem a identidade visual do projeto (Ciano/Teal)
custom_theme = {
    "colors": {
        "dochmo_teal": ["#e3f6f8", "#c6edf0", "#a9e3e9", "#8cdbe1", "#6fd2d9", "#52c9d2", "#2bbaca", "#2295a2", "#1a707a", "#114a51"]
    },
    "primaryColor": "dochmo_teal",
}

# =====================================================================
# 2. ENGENHARIA DE DADOS (CACHE EM MEMÓRIA)
# =====================================================================
def carregar_dados() -> pd.DataFrame:
    """
    Lê o dataset base, força tipagens corretas e higieniza valores anômalos.
    O uso de apply(pd.to_numeric) evita falhas silenciosas na renderização gráfica.
    """
    try:
        df = pd.read_excel("dataset_filtered.xlsx")
        cols_numericas = ['valor_m2', 'vl_base_calculo', 'area_edificada', 'latitude', 'longitude', 'exercicio']
        
        # Conversão vetorizada forçada (erros viram NaN)
        df[cols_numericas] = df[cols_numericas].apply(pd.to_numeric, errors='coerce')
        
        # Higienização contra crashes na engine em JavaScript do Plotly
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(subset=['valor_m2', 'latitude', 'longitude', 'area_edificada', 'exercicio'], inplace=True)
        
        return df[df['valor_m2'] > 0]
    
    except Exception as e:
        print(f"ATENÇÃO - Erro crítico ao carregar dataset base: {e}")
        # Retorna estrutura vazia segura para não quebrar a árvore de componentes
        return pd.DataFrame(columns=['exercicio', 'bairro', 'tipo_uso_imovel', 'padrao_construcao', 'valor_m2', 'latitude', 'longitude', 'area_edificada', 'vl_base_calculo'])

# Carga inicial estática (Executada apenas uma vez ao iniciar o servidor)
df_base = carregar_dados()
anos_disponiveis = sorted(df_base['exercicio'].unique()) if not df_base.empty else [2020, 2026]
min_ano, max_ano = int(min(anos_disponiveis)), int(max(anos_disponiveis))
padroes_disponiveis = sorted(df_base['padrao_construcao'].dropna().unique()) if not df_base.empty else ['Normal']
bairros_disponiveis = sorted(df_base['bairro'].dropna().unique()) if not df_base.empty else []

# =====================================================================
# 3. INTERFACE DE USUÁRIO (LAYOUT)
# =====================================================================

# --- MENU LATERAL (SM: 12 colunas mobile, LG: 2 colunas desktop) ---
sidebar = dbc.Col(
    [
        html.H2("DOCHMO", style={"fontFamily": "Times New Roman", "color": "#2BBACA"}, className="mt-3"),
        html.P(
            "Análise de transações imobiliárias: distribuição geográfica de valores e perfil de bairros (Fortaleza-CE).", 
            className="text-muted mb-3", style={"fontSize": "0.85rem", "textAlign": "justify", "color": "#ACC6C9"}
        ),
        html.Hr(style={"borderColor": "#222222"}),
        
        # Filtro 1: Ano (Slider contínuo)
        html.Label("Ano de Exercício:", className="mt-2 mb-2 fw-bold", style={"color": "#2BBACA"}),
        html.Div(
            dmc.Slider(
                id="filtro-ano", min=min_ano, max=max_ano, step=1, value=max_ano, 
                marks=[{"value": a, "label": str(a)} for a in range(min_ano, max_ano + 1)],
                size="sm", mb=35
            ), className="px-2" 
        ),

        # Filtro 2: Uso (Switches do Bootstrap)
        html.Label("Tipo de Uso do Imóvel:", className="mt-2 mb-1 fw-bold", style={"color": "#2BBACA"}),
        dbc.Checklist(
            id="filtro-uso",
            options=[{"label": " Residencial", "value": "Residencial"}, {"label": " Comercial", "value": "Comercial"}],
            value=["Residencial", "Comercial"], inline=False, switch=True, className="mb-3"
        ),
        
        # Filtro 3: Bairro (Select com busca)
        html.Label("Bairros:", className="mt-2 mb-1 fw-bold", style={"color": "#2BBACA"}),
        dmc.MultiSelect(
            id="filtro-bairro", data=bairros_disponiveis, value=[], 
            placeholder="Todos (digite para filtrar)...", searchable=True, clearable=True, size="xs", className="mb-4",
            styles={"input": {"maxHeight": "80px", "overflowY": "auto", "padding": "4px"}, "item": {"fontSize": "0.7rem"}}
        ),
        
        # Filtro 4: Padrão (Select com botões de macro-ação)
        html.Div([
            html.Label("Padrão de Construção:", className="fw-bold m-0", style={"color": "#2BBACA"}),
            html.Div([
                html.Span("Todos", id="btn-select-all", style={"cursor": "pointer", "fontSize": "0.75rem", "color": "#2BBACA", "marginRight": "15px", "textDecoration": "underline"}),
                html.Span("Limpar", id="btn-clear-all", style={"cursor": "pointer", "fontSize": "0.75rem", "color": "#888888", "textDecoration": "underline"}),
            ])
        ], className="d-flex justify-content-between align-items-end mb-2"),
        
        dmc.MultiSelect(
            id="filtro-padrao", data=padroes_disponiveis, value=padroes_disponiveis, 
            placeholder="Selecione os padrões...", searchable=True, clearable=False, size="xs", 
            styles={"input": {"maxHeight": "80px", "overflowY": "auto", "padding": "4px"}, "item": {"fontSize": "0.7rem"}}
        ), 

        # Footer Fixo
        html.Div(
            [
                html.Hr(style={"borderColor": "#222222", "marginBottom": "15px"}),
                html.Small(["Desenvolvido por: ", html.A("Douglas Moura", href="https://linkedin.com/in/douglas-chaves-moura-a545a835b", target="_blank", style={"color": "#66C5CC", "textDecoration": "none", "fontWeight": "bold"})], className="text-muted d-block mb-1"),
                html.Small(["Fonte: ", html.A("Dados Abertos Fortaleza", href="https://dados.fortaleza.ce.gov.br", target="_blank", style={"color": "#66C5CC", "textDecoration": "none"})], className="text-muted d-block")
            ], style={"position": "absolute", "bottom": "25px", "width": "82%"}
        )
    ],
    sm=12, md=3, lg=2, style={"backgroundColor": "#111111", "padding": "20px", "minHeight": "100vh", "borderRight": "1px solid #222222", "position": "relative"}
)

# --- ÁREA PRINCIPAL (Gráficos) ---
main_content = dbc.Col(
    [
        # dcc.Loading provê feedback visual (spinner) durante o processamento de callbacks
        dbc.Row(dbc.Col(dcc.Loading(type="circle", color="#2BBACA", children=dcc.Graph(id="mapa-imoveis", style={"height": "52vh", "marginTop": "15px"})))),
        dbc.Row([
            dbc.Col(dcc.Loading(type="circle", color="#2BBACA", children=dcc.Graph(id="grafico-boxplot", style={"height": "40vh", "marginTop": "15px"})), sm=12, md=6),
            dbc.Col(dcc.Loading(type="circle", color="#2BBACA", children=dcc.Graph(id="grafico-bairros", style={"height": "40vh", "marginTop": "15px"})), sm=12, md=6)
        ])
    ],
    sm=12, md=9, lg=10, style={"padding": "10px 25px"}
)

# Ponto de entrada do Layout
app.layout = dmc.MantineProvider(
    forceColorScheme="dark", theme=custom_theme,
    children=dbc.Container([ 
        dcc.Store(id='store-dados-filtrados'), # Arquitetura de Memória Local
        dbc.Row([sidebar, main_content])
    ], fluid=True, style={"backgroundColor": "#060606", "minHeight": "100vh", "overflowX": "hidden"})
)

# =====================================================================
# 4. FUNÇÕES DE UTILIDADE E CALLBACKS
# =====================================================================
def figura_vazia(mensagem: str) -> go.Figure:
    """Gera um frame escuro com aviso centralizado para DataFrames vazios."""
    return go.Figure().update_layout(
        title={"text": f"<i>{mensagem}</i>", "x": 0.5, "y": 0.5, "xanchor": "center", "yanchor": "middle"}, 
        xaxis={"visible": False}, yaxis={"visible": False}, paper_bgcolor="#060606", plot_bgcolor="#060606", font={"color": "#FFFFFF"}
    )

# --- CALLBACK 1: UX DOS BOTÕES DE SELEÇÃO RÁPIDA ---
@callback(
    Output("filtro-padrao", "value"),
    [Input("btn-select-all", "n_clicks"), Input("btn-clear-all", "n_clicks")], prevent_initial_call=True
)
def gerenciar_botoes_selecao(n_all, n_clear):
    """Controla os botões 'Todos' e 'Limpar' identificando qual input disparou o evento via ctx."""
    botao_clicado = ctx.triggered_id 
    if botao_clicado == "btn-select-all": return padroes_disponiveis 
    elif botao_clicado == "btn-clear-all": return [] 
    return no_update 

# --- CALLBACK 2: MOTOR DE FILTRAGEM DE DADOS ---
@callback(
    Output('store-dados-filtrados', 'data'),
    [Input("filtro-ano", "value"), Input("filtro-uso", "value"), Input("filtro-padrao", "value"), Input("filtro-bairro", "value")]
)
def processar_filtros(ano_selecionado, usos_selecionados, padroes_selecionados, bairros_selecionados):
    """
    Desacoplamento lógico: Este callback apenas processa os dados via máscaras booleanas 
    do Pandas (alta performance) e salva o resultado no Client-side (dcc.Store).
    """
    if not usos_selecionados: return []
    
    mask = (df_base['exercicio'] == ano_selecionado) & (df_base['tipo_uso_imovel'].isin(usos_selecionados))
    if padroes_selecionados: 
        mask &= df_base['padrao_construcao'].isin(padroes_selecionados)
        
    # Se o usuário especificou bairros, aplica o filtro; caso contrário, ignora (mostra todos)
    if bairros_selecionados and len(bairros_selecionados) > 0:
        mask &= df_base['bairro'].isin(bairros_selecionados)
    
    # Otimização de Payload: Transmite pela rede apenas as colunas que serão plotadas
    colunas_necessarias = ['bairro', 'tipo_uso_imovel', 'padrao_construcao', 'valor_m2', 'latitude', 'longitude', 'area_edificada', 'vl_base_calculo']
    return df_base[mask][colunas_necessarias].to_dict('records')

# --- CALLBACK 3: RENDERIZAÇÃO GRÁFICA ---
@callback(
    [Output("mapa-imoveis", "figure"), Output("grafico-boxplot", "figure"), Output("grafico-bairros", "figure")],
    Input('store-dados-filtrados', 'data'), State('filtro-ano', 'value'), prevent_initial_call=False
)
def atualizar_graficos(dados_em_memoria, ano_selecionado): 
    """
    Consome os dados filtrados em memória e gera as Figuras do Plotly.
    Possui tratamento interno para DataFrames vazios ou erros de cast.
    """
    if not dados_em_memoria: 
        return px.scatter_mapbox(lat=[-3.7319], lon=[-38.5267], zoom=10.5).update_layout(mapbox_style="carto-darkmatter", margin={"r": 0, "t": 0, "l": 0, "b": 0}), figura_vazia("Nenhum dado"), figura_vazia("Nenhum dado")

    df_filtrado = pd.DataFrame(dados_em_memoria)
    
    # Formatadores locais para injeção de Tooltips sem overhead global
    def formatar_moeda(valor):
        if pd.isna(valor) or valor == float('inf') or valor == float('-inf'): return "R$ 0,00"
        return f'R$ {float(valor):,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_area(valor):
        if pd.isna(valor) or valor == float('inf') or valor == float('-inf'): return "0,0"
        return f'{float(valor):,.1f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    
    try:
        # ==========================================
        # 1. MAPA DE TRANSAÇÕES
        # ==========================================
        # Amostragem defensiva: Previne o travamento do WebGL em queries massivas
        df_mapa = df_filtrado.sample(n=10000, random_state=42) if len(df_filtrado) > 10000 else df_filtrado.copy()
        
        # Preparação das strings de hover via List Comprehension (mais rápido que .apply)
        df_mapa["valor_m2_fmt"] = [formatar_moeda(x) for x in df_mapa["valor_m2"]]
        df_mapa["vl_base_calculo_fmt"] = [formatar_moeda(x) for x in df_mapa["vl_base_calculo"]]
        df_mapa["area_edificada_fmt"] = [formatar_area(x) for x in df_mapa["area_edificada"]]

        titulo_mapa = f"Mapa de Transações: Valor do M² por Região ({ano_selecionado})"

        # center={"lat", "lon"}: Foca dinamicamente no "centro de gravidade" dos dados filtrados
        fig_mapa = px.scatter_map(
            df_mapa, lat="latitude", lon="longitude", color="valor_m2", size="area_edificada", hover_name="bairro", 
            custom_data=["tipo_uso_imovel", "vl_base_calculo_fmt", "valor_m2_fmt", "area_edificada_fmt"], 
            color_continuous_scale="Teal", size_max=15, zoom=10.5, center={"lat": df_mapa["latitude"].mean(), "lon": df_mapa["longitude"].mean()}, 
            map_style="carto-darkmatter", title=titulo_mapa 
        )
        
        # sizemin=2 impede que pontos com áreas baixas desapareçam no zoom out
        fig_mapa.update_traces(
            marker=dict(sizemin=2), 
            hovertemplate="<b>%{hovertext}</b><br><br>Tipo de uso: %{customdata[0]}<br>Valor venal: %{customdata[1]}<br>Valor do m²: %{customdata[2]}<br>Área edificada: %{customdata[3]} m²<extra></extra>"
        )
        
        fig_mapa.update_layout(
            separators=",.", paper_bgcolor="#060606", plot_bgcolor="#060606", font={"color": "#FFFFFF"}, 
            margin={"r": 0, "t": 35, "l": 0, "b": 0}, coloraxis_colorbar=dict(title="Valor M² (R$)", thickness=15, len=0.85)
        )
        fig_mapa.update_coloraxes(cmin=df_mapa["area_edificada"].min(), cmax=df_mapa["area_edificada"].max(), colorscale="Teal")

        # ==========================================
        # 2. BOXPLOT DE DISPERSÃO
        # ==========================================
        # Remoção do Top 1% (Outliers de Luxo) para não colapsar a visualização da mediana interquartil
        limite = df_filtrado['valor_m2'].quantile(0.99)
        limite = limite if pd.notna(limite) and limite != float('inf') else float('inf')
        df_boxplot_data = df_filtrado[df_filtrado['valor_m2'] <= limite].copy()
        
        df_boxplot_data["valor_m2_fmt"] = [formatar_moeda(x) for x in df_boxplot_data["valor_m2"]]

        fig_boxplot = px.box(
            df_boxplot_data, x='padrao_construcao', y='valor_m2', color='tipo_uso_imovel', 
            points='outliers', custom_data=["valor_m2_fmt"], color_discrete_sequence=px.colors.qualitative.Pastel, 
            title='Dispersão do Valor do M²<br><sup>Sem Outliers Extremos</sup>', labels={'padrao_construcao': 'Padrão', 'tipo_uso_imovel': 'Uso:'}
        )
        fig_boxplot.update_traces(hovertemplate="<b>Padrão:</b> %{x}<br><b>Tipo:</b> %{fullData.name}<br><b>Valor do m²:</b> %{customdata[0]}<br><extra></extra>")
        
        fig_boxplot.update_layout(
            separators=",.", paper_bgcolor="#060606", plot_bgcolor="#111111", font={"color": "#FFFFFF"},
            margin={"r": 10, "t": 60, "l": 10, "b": 10}, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_boxplot.update_yaxes(tickformat=",.2f", title="Valor M² (R$)") 

        # ==========================================
        # 3. BARRAS HORIZONTAIS (TOP 10 BAIRROS)
        # ==========================================
        df_bairros = df_filtrado.groupby('bairro', as_index=False)['valor_m2'].mean()
        
        # O .nlargest() é assintoticamente mais rápido que .sort_values().head() para DataFrames grandes
        df_top10 = df_bairros.nlargest(10, 'valor_m2').copy()
        df_top10["valor_m2_fmt"] = [formatar_moeda(x) for x in df_top10["valor_m2"]]

        # --- TÍTULO DINÂMICO COM ANO E CONTAGEM ---
        qtd = len(df_top10)
        if qtd == 10:
            titulo_barras = f"Top 10 Bairros: Valor Médio M² ({ano_selecionado})"
        elif qtd > 1:
            titulo_barras = f"Ranking: {qtd} Bairros Selecionados ({ano_selecionado})"
        elif qtd == 1:
            titulo_barras = f"Valor Médio M² do Bairro Selecionado ({ano_selecionado})"
        else:
            titulo_barras = "Nenhum bairro com dados neste ano"

        fig_barras = px.bar(
            df_top10, x='valor_m2', y='bairro', orientation='h', color='valor_m2', 
            color_continuous_scale="Teal", title=titulo_barras, 
            labels={'valor_m2': 'Média Valor M² (R$)', 'bairro': 'Bairro'}, text='valor_m2_fmt' 
        )
        fig_barras.update_traces(textposition='inside', hovertemplate="<b>Bairro:</b> %{y}<br><b>Média M²:</b> %{text}<extra></extra>")
        
        # automargin=True evita cortes no eixo Y caso um bairro tenha nome muito longo
        fig_barras.update_layout(
            separators=",.", paper_bgcolor="#060606", plot_bgcolor="#060606", font={"color": "#FFFFFF"},
            margin={"r": 10, "t": 60, "l": 10, "b": 10}, yaxis={'categoryorder': 'total ascending', 'automargin': True}, coloraxis_showscale=False
        )

        return fig_mapa, fig_boxplot, fig_barras
        
    except Exception as e:
        print(f"ERRO DE RENDERIZAÇÃO: {e}")
        return px.scatter_mapbox(lat=[-3.7319], lon=[-38.5267], zoom=10).update_layout(mapbox_style="carto-darkmatter"), figura_vazia("Erro"), figura_vazia("Erro")
    
if __name__ == "__main__":
    app.run(debug=True)
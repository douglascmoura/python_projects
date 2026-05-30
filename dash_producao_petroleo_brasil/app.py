"""
Dashboard Interativo: DOCHMO - Produção Nacional de Petróleo
Desenvolvido por: Douglas Chaves Moura

Arquitetura:
- Frontend: Dash, Dash Bootstrap Components (LUX Theme), Dash Mantine Components.
- Estilização: CSS customizado via pasta estática (assets/style.css).
- Backend: Pandas para manipulação de dados em formato Parquet (Alta performance).
- State Management: dcc.Store para cache de dados no cliente (Client-side storage),
  evitando reprocessamento redundante nos gráficos.
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# =====================================================================
# 1. CONFIGURAÇÃO GLOBAL E TEMATIZAÇÃO (LIGHT MODE)
# =====================================================================
# Inicializa o app com o tema LUX (Bootstrap) e define o suporte ao idioma Pt-BR para o Plotly.
# O Dash automaticamente detecta e aplica qualquer arquivo .css presente na pasta /assets
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.LUX], 
    title="DOCHMO - Produção Nacional de Petróleo",
    external_scripts=["https://cdn.plot.ly/plotly-locale-pt-br-latest.js"],
    suppress_callback_exceptions=True
)
server = app.server # Exposto para ambientes de produção (WSGI/Gunicorn)

# Paleta de Cores de Dados (Sunset & Ocean) para consistência visual nos gráficos
COR_OFFSHORE_MAR = "#8B1F72"   # Roxo moderno
COR_ONSHORE_TERRA = "#F58B72"  # Sunset / Terracota
COR_MAPA_VAZIO = "#E2E8F0"     # Cinza bem claro para estados sem produção
COR_TEXTO_BACK = "#ADB5BD"     # Texto de países e oceanos mais discreto

# Paleta customizada (Mantine): Garante que os componentes de input interativos
# (NumberInput, MultiSelect) respeitem a identidade visual com tons quentes
custom_theme = {
    "primaryColor": "orange",
    "colors": {
        "orange": ["#fff4e6", "#ffe8cc", "#ffd8a8", "#ffc078", "#ffa94d", "#ff922b", "#fd7e14", "#f76707", "#e8590c", "#d9480f"]
    }
}

def fmt_br(valor):
    """
    Formatador numérico para o padrão brasileiro (ex: 1.234.567,89).
    Substitui a pontuação nativa do Python pelas convenções locais.
    """
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================================
# 2. ENGENHARIA DE DADOS (CACHE EM MEMÓRIA DO SERVIDOR)
# =====================================================================
def carregar_dados_petroleo() -> tuple[pd.DataFrame, dict]:
    """
    Lê o dataset base (Parquet para otimização de leitura) e o arquivo GeoJSON.
    Retorna uma tupla contendo o DataFrame e o dicionário de polígonos espaciais.
    Possui tratamento de exceções para evitar a quebra da árvore de inicialização.
    """
    try:
        caminho_dados = "producao_petroleo_filtered.parquet"
        df = pd.read_parquet(caminho_dados)
                
        # Tenta resolver o caminho do GeoJSON na pasta script, com fallback para o root
        caminho_geojson = os.path.join("script", "brazil_states.json")
        try:
            with open(caminho_geojson, "r", encoding="utf-8") as f:
                geojson = json.load(f)
        except Exception as e:
            if not os.path.exists(caminho_geojson):
                caminho_geojson = "brazil_states.json"
            with open(caminho_geojson, "r", encoding="latin-1") as f:
                geojson = json.load(f)
            
        return df, geojson
    except Exception as e:
        print(f"[CRITICAL ERROR] Falha no pipeline de dados: {e}")
        # Retorna estruturas vazias em caso de erro para manter o app rodando
        return pd.DataFrame(), {}

# Carga inicial estática: Executada apenas uma vez quando o servidor sobe.
# Previne acessos repetidos ao disco durante o uso concorrente por múltiplos usuários.
df_base, geojson_brasil = carregar_dados_petroleo()

# Definição de limites e domínios dinâmicos com base nos dados carregados
ANOS_DISPONIVEIS = sorted(df_base['ano'].unique()) if not df_base.empty else [1997, 2026]
MIN_ANO, MAX_ANO = int(min(ANOS_DISPONIVEIS)), int(max(ANOS_DISPONIVEIS))
UFS_DISPONIVEIS = sorted(df_base['unidade_da_federacao'].unique()) if not df_base.empty else []

# =====================================================================
# 3. INTERFACE DE USUÁRIO (LAYOUT E COMPONENTES)
# =====================================================================
def build_sidebar() -> dbc.Col:
    """
    Constrói a barra lateral (Sidebar) contendo os títulos e filtros da aplicação.
    As classes customizadas (ex: 'sidebar-title', 'sidebar-container') fazem 
    o hook direto com o arquivo assets/style.css.
    """
    return dbc.Col(
        [
            html.H2("DOCHMO", className="sidebar-title mt-3"),
            html.P("Análise volumétrica da extração de petróleo no Brasil: distribuição geográfica e série histórica.", className="sidebar-description mb-4"),
            html.Hr(className="sidebar-divider"),
            
            # Filtro 1: Período (Inputs Numéricos)
            html.Label("Período de Análise:", className="sidebar-label mb-1"),
            html.Div([
                dmc.NumberInput(id="filtro-ano-inicio", value=MIN_ANO, min=MIN_ANO, max=MAX_ANO, className="number-input-half", size="sm", label="Ano Inicial"),
                dmc.NumberInput(id="filtro-ano-fim", value=MAX_ANO, min=MIN_ANO, max=MAX_ANO, className="number-input-half", size="sm", label="Ano Final")
            ], className="filter-row"),

            # Filtro 2: Localização (Checklist Switch)
            html.Label("Localização da Extração:", className="sidebar-label mb-2"),
            dbc.Checklist(
                id="filtro-localizacao",
                options=[{"label": " Mar", "value": "MAR"}, {"label": " Terra", "value": "TERRA"}],
                value=["MAR", "TERRA"], inline=True, switch=True, className="mb-3",
                style={"display": "flex", "justifyContent": "center"}
            ),
            
            # Filtro 3: Unidade da Federação (Select Múltiplo)
            html.Label("Unidade da Federação:", className="sidebar-label mb-1"),
            html.Div(
                dmc.MultiSelect(
                    id="filtro-uf", data=UFS_DISPONIVEIS, value=[], 
                    placeholder="Todas (digite para filtrar)...", searchable=True, clearable=True, size="xs",
                    maxDropdownHeight=130, styles={"item": {"className": "multiselect-dropdown-item"}}
                ), 
                className="multiselect-container" 
            ),
            
            # Rodapé informativo com referências
            html.Div(
                [
                    html.Hr(className="sidebar-divider mb-1"),
                    html.Small(
                        [
                            "Desenvolvido por: ",
                            html.A("Douglas Moura", href="https://www.linkedin.com/in/douglas-chaves-moura-a545a835b", target="_blank", style={"textDecoration": "none", "fontWeight": "500"})
                        ],
                        className="text-muted d-block mb-1"
                    ),
                    html.Small(
                        [
                            "Fonte: ",
                            html.A("ANP / Dados Estatísticos", href="https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-estatisticos", target="_blank", style={"textDecoration": "none", "fontWeight": "500"})
                        ],
                        className="text-muted d-block mb-1"
                    )
                ],
                className="sidebar-footer"
            )
        ],
        sm=12, md=3, lg=2, className="sidebar-container"
    )

def build_main_content() -> dbc.Col:
    """
    Constrói a área principal da aplicação (Main Content) onde os gráficos são alocados.
    Utiliza dcc.Loading para fornecer feedback visual (spinner) enquanto os callbacks processam os dados.
    As classes 'chart-tall' e 'chart-standard' são controladas pelo style.css.
    """
    config_pt_br = {"locale": "pt-BR"}

    return dbc.Col(
        [
            dbc.Row(dbc.Col(dcc.Loading(type="circle", color="#D96C06", children=dcc.Graph(id="grafico-serie-temporal", className="chart-tall")))),
            dbc.Row([
                dbc.Col(dcc.Loading(type="circle", color="#D96C06", children=dcc.Graph(id="grafico-mapa-br", className="chart-standard")), sm=12, md=6),
                dbc.Col(dcc.Loading(type="circle", color="#D96C06", children=dcc.Graph(id="grafico-rosca", className="chart-standard")), sm=12, md=6)
            ])
        ],
        sm=12, md=9, lg=10, className="main-content-container"
    )

# Ponto de entrada do Layout principal
app.layout = dmc.MantineProvider(
    forceColorScheme="light", theme=custom_theme, # Força o tema claro nos componentes Mantine
    children=dbc.Container([ 
        dcc.Store(id='store-dados-agregados'), # Arquitetura de Memória Local para dados filtrados
        dbc.Row([build_sidebar(), build_main_content()])
    ], fluid=True, className="app-container")
)

# =====================================================================
# 4. CALLBACKS E REGRAS DE NEGÓCIO
# =====================================================================
def empty_figure(msg: str) -> go.Figure:
    """Gera um frame claro com aviso centralizado quando os filtros resultam em um DataFrame vazio."""
    return go.Figure().update_layout(
        title={"text": f"<i>{msg}</i>", "x": 0.5, "y": 0.5, "xanchor": "center", "yanchor": "middle"}, 
        xaxis={"visible": False}, yaxis={"visible": False}, 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": "#888888"}
    )

# --- CALLBACK 1: MOTOR DE FILTRAGEM DE DADOS (DATA LAYER) ---
@callback(
    Output('store-dados-agregados', 'data'),
    [Input("filtro-ano-inicio", "value"), Input("filtro-ano-fim", "value"), 
     Input("filtro-localizacao", "value"), Input("filtro-uf", "value")]
)
def processar_motor_dados(ano_inicio, ano_fim, localizacao, ufs):
    """
    Desacoplamento lógico: Este callback apenas processa os dados via máscaras booleanas 
    do Pandas (alta performance) e salva o resultado no Client-side (dcc.Store).
    """
    if df_base.empty: return None

    # Validação e normalização dos limites de ano
    ano_i = ano_inicio if ano_inicio is not None else MIN_ANO
    ano_f = ano_fim if ano_fim is not None else MAX_ANO
    mask = (df_base['ano'] >= ano_i) & (df_base['ano'] <= ano_f)
    
    # Filtro de Localização (Mar/Terra)
    if localizacao:
        locs_selecionadas = [str(loc).upper() for loc in localizacao]
        mask &= df_base['localizacao'].astype(str).str.upper().isin(locs_selecionadas)
    else: return None 
        
    # Filtro de Estados
    if ufs and isinstance(ufs, list) and len(ufs) > 0:
        mask &= df_base['unidade_da_federacao'].isin(ufs)
        
    df_filtrado = df_base[mask]
    if df_filtrado.empty: return None

    # Otimização de Payload: Realiza pré-agregações no servidor antes de enviar 
    # ao dcc.Store no front-end, reduzindo o tráfego de rede drasticamente.
    df_linha = df_filtrado.groupby(['ano', 'mes_num', 'localizacao'], as_index=False)['producao'].sum()
    df_linha = df_linha.sort_values(['ano', 'mes_num'])
    df_linha['data'] = df_linha['ano'].astype(str) + "-" + df_linha['mes_num'].astype(str).str.zfill(2)
    
    df_mapa = df_filtrado.groupby('unidade_da_federacao', as_index=False)['producao'].sum()
    df_rosca = df_filtrado.groupby('localizacao', as_index=False)['producao'].sum()
    
    return {
        "linha": df_linha[['data', 'localizacao', 'producao']].to_dict('records'), 
        "mapa": df_mapa.to_dict('records'), 
        "rosca": df_rosca.to_dict('records'),
        "filtros_aplicados": {"ano_i": ano_i, "ano_f": ano_f} 
    }

# --- CALLBACK 2: RENDERIZAÇÃO GRÁFICA (VIEW LAYER) ---
@callback(
    [Output("grafico-serie-temporal", "figure"), Output("grafico-mapa-br", "figure"), Output("grafico-rosca", "figure")],
    Input('store-dados-agregados', 'data'), prevent_initial_call=False
)
def renderizar_graficos(dados):
    """
    Consome os dados pré-agregados em memória e gera as Figuras do Plotly.
    Possui tratamento interno de consistência visual e tematização integrada.
    """
    if not dados: return empty_figure("Sem Dados"), empty_figure("Sem Dados"), empty_figure("Sem Dados")
        
    # Reconstrução dos DataFrames a partir do JSON recebido do browser
    df_linha = pd.DataFrame(dados['linha'])
    df_mapa = pd.DataFrame(dados['mapa'])
    df_rosca = pd.DataFrame(dados['rosca'])
    
    filtros = dados.get('filtros_aplicados', {"ano_i": MIN_ANO, "ano_f": MAX_ANO})
    texto_periodo = f"({filtros['ano_i']} - {filtros['ano_f']})"

    color_map_rosca = {
        "MAR": COR_OFFSHORE_MAR, "Mar": COR_OFFSHORE_MAR, "mar": COR_OFFSHORE_MAR,
        "TERRA": COR_ONSHORE_TERRA, "Terra": COR_ONSHORE_TERRA, "terra": COR_ONSHORE_TERRA
    }
    font_color_main = "#2B2D42" # Cor da fonte principal (Dark Slate)

    # =====================================================================
    # 1. GRÁFICO: EVOLUÇÃO TEMPORAL (LINHA)
    # =====================================================================
    fig_linha = px.line(
        df_linha, x='data', y='producao', color='localizacao',
        title=f'<b>Evolução Temporal da Produção de Petróleo {texto_periodo}</b>',
        labels={'producao': 'Volume Produzido (m³)', 'data': "Valor temporal", 'localizacao': 'Localização: '},
        template='plotly_white', color_discrete_map=color_map_rosca
    )
    fig_linha.update_layout(
        separators=",.", hovermode="x unified",
        # Tooltip escuro num tema claro cria um visual muito elegante
        hoverlabel=dict(bgcolor="#E2E8F0", bordercolor="#E2E8F0", font_size=14, font_family="Segoe UI", font_color="#2B2D42"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color_main),
        yaxis=dict(tickformat=",.2f", title="Volume Mensal (m³)", showgrid=True, gridcolor="#E2E8F0", zeroline=False, hoverformat="%B de %Y"),
        xaxis=dict(showspikes=True, spikethickness=1, spikedash="dot", spikemode="across", showgrid=False),
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=0.97, xanchor="right", x=0.97), margin=dict(l=10, r=10, t=50, b=10)
    )
    fig_linha.update_traces(line=dict(width=3), hovertemplate="%{fullData.name}: %{y:,.2f} m³<extra></extra>")

    # =====================================================================
    # 2. GRÁFICO: MAPA CHOROPLETH (BRASIL)
    # =====================================================================
    if geojson_brasil and not df_mapa.empty:
        df_mapa['unidade_da_federacao'] = df_mapa['unidade_da_federacao'].str.title().str.replace(" De ", " de ").str.replace(" Do ", " do ")
        
        # Merge para garantir que todos os estados apareçam, mesmo com produção 0
        todos_estados = [feature['properties']['name'] for feature in geojson_brasil.get('features', [])]
        if todos_estados:
            df_todos_estados = pd.DataFrame({'unidade_da_federacao': todos_estados})
            df_mapa = pd.merge(df_todos_estados, df_mapa, on='unidade_da_federacao', how='left').fillna(0)

        df_mapa['producao_hover'] = df_mapa['producao'].apply(fmt_br)
        
        # Escala de cores personalizada para transição suave do mapa
        colorscale_p = [
            [0.00, COR_MAPA_VAZIO], [0.001, "#F5DC94"], [0.25, "#F58B72"], 
            [0.60, "#E04672"], [1.00, "#8B1F72"]
        ]
        
        fig_mapa = px.choropleth(
            df_mapa, geojson=geojson_brasil, locations='unidade_da_federacao',
            featureidkey="properties.name", color='producao', custom_data=['producao_hover'],
            title=f'<b>Distribuição Espacial da Produção {texto_periodo}</b>', template='plotly_white'
        )
        
        # Adiciona camada extra de contexto geográfico (anotações de oceanos/países)
        fig_mapa.add_trace(go.Scattergeo(
            lon=[-28.239, -64.0, -57.5, -63.5, -75.0, -72.0, -66.0, -56.0, -71.0, -58.9, -55.9, -79.5],
            lat=[-1.828, -31.0, -23.0, -16.5, -9.0, 3.5, 7.0, -32.8, -30.0, 5.0, 4.0, -1.5],
            text=["OCEANO<br>ATLÂNTICO", "ARGENTINA", "PARAGUAI", "BOLÍVIA", "PERU", "COLÔMBIA", "VENEZUELA", "URUGUAI", "CHILE", "GUIANA", "SURINAME", "EQUADOR"],
            mode="text", textfont=dict(family="Arial", size=8.5, color=COR_TEXTO_BACK), showlegend=False
        ))
        
        # Configuração de base do mapa limitando visões desnecessárias
        fig_mapa.update_geos(
            fitbounds="locations", visible=False, showland=True, landcolor="#F4F6F8", 
            showocean=True, oceancolor="#E9ECEF", showcountries=True, countrycolor="#FFFFFF", 
            showcoastlines=True, coastlinecolor="#FFFFFF"
        )
        fig_mapa.update_traces(
            marker_line_width=1, marker_line_color="#FFFFFF", # Bordas brancas nos estados
            hovertemplate="<b>Estado:</b> %{location}<br><b>Produção Total:</b> %{customdata[0]}<extra></extra>",
            selector=dict(type='choropleth')
        )
        fig_mapa.update_coloraxes(colorscale=colorscale_p, cmin=0, cmax=df_mapa['producao'].max()) 
        fig_mapa.update_layout(
            separators=",.", margin=dict(r=0, t=55, l=0, b=0), font=dict(color=font_color_main),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="Volume (m³)", thickness=12, len=0.75, tickformat=",.0f")
        )
    else:
        fig_mapa = empty_figure("GeoJSON ou Dados Indisponíveis")

    # =====================================================================
    # 3. GRÁFICO: DONUT CHART (ROSCA)
    # =====================================================================
    fig_rosca = px.pie(
        df_rosca, values='producao', names='localizacao', hole=0.55,
        title=f'<b>Participação Absoluta: Terra vs Mar {texto_periodo}</b>',
        template='plotly_white', color='localizacao', color_discrete_map=color_map_rosca
    )
    fig_rosca.update_traces(
        textposition='outside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=1.5)), # Borda branca nas fatias
        hovertemplate="<b>Ambiente:</b> %{label}<br><b>Volume Acumulado:</b> %{value:,.2f} m³<extra></extra>"
    )
    fig_rosca.update_layout(
        separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color_main),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.97),
        margin=dict(l=10, r=10, t=55, b=10)
    )
    
    return fig_linha, fig_mapa, fig_rosca

if __name__ == "__main__":
    app.run(debug=True)
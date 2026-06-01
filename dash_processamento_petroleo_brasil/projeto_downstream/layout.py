"""
layout.py
---------
Módulo responsável por construir a interface do usuário (Frontend).
Utiliza o sistema de Grid do Bootstrap (Linhas e Colunas) para garantir que o 
dashboard seja totalmente responsivo em diferentes tamanhos de tela (desktop, tablet, mobile).
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from data_manager import MIN_ANO, MAX_ANO, MATERIAS_PRIMAS, ESTADOS

def criar_sidebar() -> dbc.Col:
    """
    Constrói a barra lateral (Sidebar) onde ficam os controles da aplicação.
    É encapsulada em uma coluna (dbc.Col) para facilitar o posicionamento no grid principal.
    """
    return dbc.Col(
        [
            # Cabeçalho da aplicação
            html.H2("DOCHMO", style={"fontFamily": "Roboto", "color": "#e3e3e3", "fontWeight": "bold"}),
            html.P("Análise do volume de processamento de petróleo e distribuição da matéria prima nas refinarias nacionais.", className="text-muted mb-4", style={"fontSize": "0.85rem"}),
            html.Hr(style={"borderColor": "var(--color-border)"}),
            
            # FILTRO 1: RANGE DE ANOS (UX Analítica)
            # Utilizamos dois NumberInputs (Mantine) em vez de um Slider. Isso melhora a UX 
            # quando o usuário precisa de precisão exata, evitando frustrações com o mouse.
            html.Label("Período de Análise:", className="fw-bold mb-2", style={"color": "var(--color-primary)"}),
            html.Div([
                dmc.NumberInput(id="filtro-ano-inicio", value=MIN_ANO, min=MIN_ANO, max=MAX_ANO, className="number-input-half", size="sm", label="Ano Inicial 🗓️"),
                dmc.NumberInput(id="filtro-ano-fim", value=MAX_ANO, min=MIN_ANO, max=MAX_ANO, className="number-input-half", size="sm", label="Ano Final 🗓️")
            ], style={ "display": "flex", "gap": "14px"}),

            # FILTRO 2: MATÉRIA PRIMA (Checklist)
            # Utilizamos o Checklist do Bootstrap configurado como 'switch' para dar uma cara mais moderna.
            html.Label("Matéria Prima:", className="mt-3 fw-bold mb-2", style={"color": "var(--color-primary)"}),
            dbc.Checklist(
                id="filtro-materia",
                options=[{"label": m.title(), "value": m} for m in MATERIAS_PRIMAS],
                value=MATERIAS_PRIMAS,
                inline=False, switch=True, className="mb-3 text-dark",
                style={"color": "var(--text-muted)"}
            ),

            # FILTRO 3: ESTADOS (MultiSelect)
            # Permite buscar digitando, essencial quando a lista de opções (27 UFs) é grande.
            html.Label("Estados (UF):", className="fw-bold mb-2", style={"color": "var(--color-primary)"}),
            dmc.MultiSelect(
                id="filtro-estado", data=ESTADOS, value=[],
                placeholder="Todos (digite para filtrar)...", searchable=True, clearable=True, size="sm",
                maxDropdownHeight=170
            ),
            
            # RODAPÉ FIXO NA SIDEBAR
            # Posicionamento absoluto no fundo da barra lateral para créditos e fontes.
            html.Div(
                [   
                    html.Small(
                        [
                            "Desenvolvido por: ",
                            html.A("Douglas Moura", href="https://www.linkedin.com/in/douglas-chaves-moura-a545a835b", target="_blank", style={"color": "var(--color-primary)"})
                        ],
                        className="text-muted d-block mb-1"
                    ),
                    html.Small(
                        [
                            "Fonte: ",
                            html.A("ANP / Dados Estatísticos", href="https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-estatisticos", target="_blank", style={"color": "var(--color-primary)"})
                        ],
                        className="text-muted d-block mb-1"
                    )
                ],
                style={"position": "absolute", "bottom": "10px", "font-size": "smaller"}
            )
        ],
        # Configuração de responsividade: ocupa 12 colunas no celular, 3 no tablet/desktop, e 2 em telas gigantes (xl).
        sm=12, md=3, lg=3, xl=2,
        style={"backgroundColor": "var(--color-bg-sidebar)", "padding": "25px", "minHeight": "100vh", "borderRight": "1px solid var(--color-border)", "zIndex": 100}
    )

def criar_layout() -> dbc.Container:
    """Monta a grade principal (Grid) do Dashboard."""
    return dbc.Container(
        [
            # ARQUITETURA DE PERFORMANCE: dcc.Store
            # Armazena os dados filtrados na memória do navegador do usuário (Client-side).
            # Impede que os mesmos cálculos ocorram múltiplas vezes para gráficos diferentes.
            dcc.Store(id='store-dados'), 
            
            dbc.Row(
                [
                    criar_sidebar(),
                    dbc.Col(
                        [
                            # LINHA SUPERIOR: Gráfico Temporal
                            # dcc.Loading cria a animação (spinner) enquanto os gráficos carregam, melhorando a UX.
                            dbc.Row(
                                dbc.Col(dcc.Loading(color="#eaeaea", type="cube", children=dcc.Graph(id="fig_linha", style={"height": "50vh"}))),
                                className="mb-3"
                            ),
                            # LINHA INFERIOR: Treemap e Rosca
                            dbc.Row(
                                [
                                    # Treemap ocupa 7 ou 8 colunas (dependendo da tela), Rosca ocupa o resto.
                                    dbc.Col(dcc.Loading(color="#eaeaea", type="cube", children=dcc.Graph(id="fig_tree", style={"height": "45vh"})), md=7, lg=8),
                                    dbc.Col(dcc.Loading(color="#eaeaea", type="cube", children=dcc.Graph(id="fig_rosca", style={"height": "45vh"})), md=5, lg=4)
                                ]
                            )
                        ],
                        # Área de gráficos ocupa o espaço restante do grid
                        sm=12, md=9, lg=9, xl=10, style={"padding": "10px"}
                    )
                ]
            )
        ],
        fluid=True, style={"padding": 0} # fluid=True remove margens laterais nativas do Bootstrap
    )
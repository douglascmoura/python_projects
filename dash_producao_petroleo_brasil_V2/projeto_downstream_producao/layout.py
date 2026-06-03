"""
layout.py
---------
Responsável apenas pela estruturação visual da aplicação (Front-End puro).
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html
from data_manager import MIN_ANO, MAX_ANO, UFS_DISPONIVEIS

def build_sidebar() -> dbc.Col:
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
                    id="filtro-uf",
                    data=[{"label": uf.title().replace(" De ", " de ").replace(" Do ", " do "), "value": uf} for uf in UFS_DISPONIVEIS],
                    value=[], 
                    placeholder="Todos (digite para filtrar)...",
                    searchable=True,
                    clearable=True,
                    size="sm",
                    maxDropdownHeight=160
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
                            html.A("Douglas Moura", href="https://www.linkedin.com/in/douglas-chaves-moura-a545a835b", target="_blank", style={"textDecoration": "none", "width": "82%", "fontSize": "0.80rem"})
                        ],
                        className="text-muted d-block mb-1"
                    ),
                    html.Small(
                        [
                            "Fonte: ",
                            html.A("ANP / Dados Estatísticos", href="https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-estatisticos", target="_blank", style={"textDecoration": "none", "width": "82%", "fontSize": "0.80rem"})
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
    return dbc.Col(
        [
            dbc.Row(dbc.Col(dcc.Loading(type="circle", color="#C46350", children=dcc.Graph(id="grafico-serie-temporal", className="chart-tall")))),
            dbc.Row([
                dbc.Col(dcc.Loading(type="circle", color="#C46350", children=dcc.Graph(id="grafico-mapa-br", className="chart-standard")), sm=12, md=5),
                dbc.Col(dcc.Loading(type="circle", color="#C46350", children=dcc.Graph(id="grafico-rosca", className="chart-standard")), sm=12, md=3),
                dbc.Col(dcc.Loading(type="circle", color="#C46350", children=dcc.Graph(id="grafico-barras-top3", className="chart-standard")), sm=12, md=4)
            ])
        ],
        sm=12, md=9, lg=10, className="main-content-container"
    )

def criar_layout():
    return dbc.Container([ 
        dcc.Store(id='store-dados-agregados'), 
        dbc.Row([build_sidebar(), build_main_content()])
    ], fluid=True, className="app-container")

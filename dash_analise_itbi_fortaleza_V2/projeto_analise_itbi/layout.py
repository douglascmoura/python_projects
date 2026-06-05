"""
layout.py
---------
Responsável apenas pela estruturação visual da aplicação (Front-End puro).
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html
from data_manager import MIN_ANO, MAX_ANO, PADROES_DISPONIVEIS, BAIRROS_DISPONIVEIS

def build_sidebar() -> dbc.Col:
    return dbc.Col(
        [
            html.H2("DOCHMO", className="sidebar-title mt-1 text-center"),
            html.P(
                "Análise de transações imobiliárias: distribuição geográfica de valores e perfil de bairros (Fortaleza-CE).", 
                className="sidebar-description mb-3"
            ),
            html.Hr(className="sidebar-divider"),
            
            # Filtro 1: Ano (Slider contínuo)
            html.Label("Ano de Exercício 🗓️", className="sidebar-label mt-2 mb-2"),
            html.Div(
                dmc.Slider(
                    id="filtro-ano", min=MIN_ANO, max=MAX_ANO, step=1, value=MAX_ANO, 
                    marks=[{"value": a, "label": str(a)} for a in range(MIN_ANO, MAX_ANO + 1)],
                    size="sm", mb=35, color="cyan"
                ), className="px-2" 
            ),

            # Filtro 2: Uso (Switches do Bootstrap)
            html.Label("Tipo de Uso do Imóvel 🏢", className="sidebar-label mt-2 mb-1"),
            dbc.Checklist(
                id="filtro-uso",
                options=[{"label": " Residencial", "value": "Residencial"}, {"label": " Comercial", "value": "Comercial"}],
                value=["Residencial", "Comercial"], inline=False, switch=True, className="mb-3 custom-switch"
            ),
            
            # Filtro 3: Bairro (Select com busca)
            html.Label("Bairros 📍", className="sidebar-label mt-2 mb-1"),
            html.Div(
                dmc.MultiSelect(
                    id="filtro-bairro", data=BAIRROS_DISPONIVEIS, value=[], 
                    placeholder="Todos (digite para filtrar)...", searchable=True, clearable=True, size="sm", className="mb-4",
                    maxDropdownHeight=160
                ),
                className="multiselect-container"
            ),
            
            # Filtro 4: Padrão (Select com botões de macro-ação)
            html.Div([
                html.Label("Padrão de Construção 🏗️", className="sidebar-label m-0"),
                html.Div([
                    html.Span("Todos", id="btn-select-all", className="btn-macro-action text-primary-accent", style={"marginRight": "10px"}),
                    html.Span("Limpar", id="btn-clear-all", className="btn-macro-action text-muted-accent"),
                ])
            ], className="d-flex justify-content-between align-items-end mb-2"),
            
            html.Div(
                dmc.MultiSelect(
                    id="filtro-padrao", data=PADROES_DISPONIVEIS, value=[], 
                    placeholder="Todos os padrões...", searchable=True, clearable=True, size="sm", 
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
                            html.A("Douglas Moura", href="https://linkedin.com/in/douglas-chaves-moura-a545a835b", target="_blank", style={"textDecoration": "none", "width": "82%", "fontSize": "0.80rem"})
                        ],
                        className="text-muted d-block mb-1"
                    ),
                    html.Small(
                        [
                            "Fonte: ",
                            html.A("Dados Abertos Fortaleza", href="https://dados.fortaleza.ce.gov.br", target="_blank", style={"textDecoration": "none", "width": "82%", "fontSize": "0.80rem"})
                        ],
                        className="text-muted d-block"
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
            # dcc.Loading provê feedback visual durante o processamento de callbacks
            dbc.Row(dbc.Col(dcc.Loading(type="circle", color="#2BBACA", children=dcc.Graph(id="mapa-imoveis", className="chart-tall")))),
            dbc.Row([
                dbc.Col(dcc.Loading(type="circle", color="#2BBACA", children=dcc.Graph(id="grafico-boxplot", className="chart-standard")), sm=12, md=6),
                dbc.Col(dcc.Loading(type="circle", color="#2BBACA", children=dcc.Graph(id="grafico-bairros", className="chart-standard")), sm=12, md=6)
            ], className="mt-3")
        ],
        sm=12, md=9, lg=10, className="main-content-container"
    )

def criar_layout():
    return dbc.Container([ 
        dcc.Store(id='store-dados-filtrados'), 
        dbc.Row([build_sidebar(), build_main_content()])
    ], fluid=True, className="app-container")

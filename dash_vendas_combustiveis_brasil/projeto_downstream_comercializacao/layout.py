"""
layout.py
---------
Módulo responsável por construir a interface do usuário (Frontend).
Utiliza o sistema de Grid do Bootstrap (Linhas e Colunas) para garantir
responsividade em diferentes tamanhos de tela.

Separação de responsabilidades:
  - layout.py → O QUE aparece na tela (estrutura e componentes)
  - callbacks.py → COMO a tela reage às interações
  - data_manager.py → De ONDE vêm os dados
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from data_manager import (
    MIN_ANO, MAX_ANO,
    PRODUTOS, ESTADOS, REGIOES,
)


def criar_sidebar() -> dbc.Col:
    """
    Constrói a barra lateral (Sidebar) com os controles de filtro da aplicação.
    Encapsulada em dbc.Col para posicionamento no grid Bootstrap responsivo.
    """
    return dbc.Col(
        [
            # ── Cabeçalho ──────────────────────────────────────────────────
            html.Div(className="sidebar-accent-line"),
            html.H2("DOCHMO", className="sidebar-logo mb-0", style={"display": "flex", "justifyContent": "center"}),
            html.P(
                "Análise da série histórica de vendas de derivados de petróleo e etanol no Brasil.",
                className="text-muted mt-2 mb-3",
                style={"fontSize": "0.80rem", "textAlign": "justify",
                       "color": "var(--color-text-muted)", "lineHeight": "1.5"}
            ),
            html.Hr(className="sidebar-divider mb-3"),

            # ── FILTRO 1: Período de Análise ────────────────────────────────
            # Dois NumberInputs (Mantine) em vez de Slider para precisão exata.
            html.Label("Período de Análise", className="filter-label mb-2 d-block"),
            html.Div(
                [
                    dmc.NumberInput(
                        id="filtro-ano-inicio",
                        value=MIN_ANO,
                        min=MIN_ANO,
                        max=MAX_ANO,
                        className="number-input-half",
                        size="sm",
                        label="Ano Inicial 🗓️",
                    ),
                    dmc.NumberInput(
                        id="filtro-ano-fim",
                        value=MAX_ANO,
                        min=MIN_ANO,
                        max=MAX_ANO,
                        className="number-input-half",
                        size="sm",
                        label="Ano Final 🗓️",
                    ),
                ],
                style={"display": "flex", "gap": "12px"},
            ),

            # ── FILTRO 2: Grande Região ─────────────────────────────────────
            html.Label("Grande Região", className="filter-label mt-3 mb-2 d-block"),
            dmc.MultiSelect(
                id="filtro-regiao",
                data=[{"label": r.title().replace("Região ", ""), "value": r} for r in REGIOES],
                value=[],
                placeholder="Todas as regiões...",
                searchable=True,
                clearable=True,
                size="sm",
                maxDropdownHeight=160,
                className="mb-2",
            ),

            # ── FILTRO 3: Combustível / Produto ────────────────────────────
            html.Label("Combustível", className="filter-label mt-3 mb-2 d-block"),
            dmc.MultiSelect(
                id="filtro-produto",
                data=[{"label": p.title(), "value": p} for p in PRODUTOS],
                value=[],
                placeholder="Todos os combustíveis...",
                searchable=True,
                clearable=True,
                size="sm",
                maxDropdownHeight=200,
                className="mb-2",
            ),

            # ── FILTRO 4: Estado (UF) ───────────────────────────────────────
            # MultiSelect com busca — essencial quando a lista tem 27 UFs.
            html.Label("Estado (UF)", className="filter-label mt-3 mb-2 d-block"),
            dmc.MultiSelect(
                id="filtro-uf",
                data=[{"label": uf.title(), "value": uf} for uf in ESTADOS],
                value=[],
                placeholder="Todos (digite para filtrar)...",
                searchable=True,
                clearable=True,
                size="sm",
                maxDropdownHeight=160,
            ),

            # ── Rodapé Fixo ─────────────────────────────────────────────────
            html.Div(
                [
                    html.Hr(style={"borderColor": "var(--color-border)", "marginBottom": "12px"}),
                    html.Small(
                        [
                            "Desenvolvido por: ",
                            html.A(
                                "Douglas Moura",
                                href="https://www.linkedin.com/in/douglas-chaves-moura-a545a835b",
                                target="_blank",
                                style={"color": "var(--color-accent)"},
                            ),
                        ],
                        className="text-muted d-block mb-1",
                    ),
                    html.Small(
                        [
                            "Fonte: ",
                            html.A(
                                "ANP / Dados Estatísticos",
                                href="https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-estatisticos",
                                target="_blank",
                                style={"color": "var(--color-accent)"},
                            ),
                        ],
                        className="text-muted d-block",
                    ),
                ],
                className="sidebar-footer",
                style={"position": "absolute", "bottom": "12px", "width": "82%"},
            ),
        ],
        # Responsividade: 12 colunas mobile, 3 tablet, 2 desktop grande
        sm=12, md=3, lg=3, xl=2,
        className="sidebar-container",
        style={
            "padding": "24px 18px",
            "minHeight": "100vh",
            "position": "relative",
        },
    )


def criar_area_graficos() -> dbc.Col:
    """
    Constrói a área principal de gráficos com três visualizações:
    1. Série Temporal (linha) — topo, largura total
    2. Mapa Cloroplético (UF) + Treemap (Região → UF) — linha inferior
    """
    return dbc.Col(
        [
            # ── LINHA 1: Série Temporal (topo, largura total) ───────────────
            dbc.Row(
                dbc.Col(
                    html.Div(
                        dcc.Loading(
                            color="#724C39",
                            type="cube",
                            children=dcc.Graph(
                                id="fig-linha",
                                style={"height": "44vh"},
                                config={"displayModeBar": False},
                            ),
                        ),
                        className="chart-panel",
                    ),
                ),
                className="mb-3",
            ),

            # ── LINHA 2: Mapa + Treemap (lado a lado) ──────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Loading(
                                color="#724C39",
                                type="cube",
                                children=dcc.Graph(
                                    id="fig-mapa",
                                    style={"height": "46vh"},
                                    config={"displayModeBar": False},
                                ),
                            ),
                            className="chart-panel",
                        ),
                        md=6, lg=6,
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Loading(
                                color="#724C39",
                                type="cube",
                                children=dcc.Graph(
                                    id="fig-treemap",
                                    style={"height": "46vh"},
                                    config={"displayModeBar": False},
                                ),
                            ),
                            className="chart-panel",
                        ),
                        md=6, lg=6,
                    ),
                ],
            ),
        ],
        sm=12, md=9, lg=9, xl=10,
        style={"padding": "12px 16px"},
    )


def criar_layout() -> dbc.Container:
    """Monta a grade principal (Grid) do Dashboard."""
    return dbc.Container(
        [
            # ARQUITETURA DE PERFORMANCE: dcc.Store
            # Armazena os dados filtrados na memória do navegador.
            # Impede que os mesmos cálculos ocorram múltiplas vezes
            # para gráficos diferentes (desacoplamento filtro ↔ renderização).
            dcc.Store(id="store-dados"),

            dbc.Row(
                [
                    criar_sidebar(),
                    criar_area_graficos(),
                ],
                className="g-0",  # Remove o gutter padrão do Bootstrap
            ),
        ],
        fluid=True,
        style={"padding": 0, "backgroundColor": "var(--color-bg-main)", "minHeight": "100vh"},
    )

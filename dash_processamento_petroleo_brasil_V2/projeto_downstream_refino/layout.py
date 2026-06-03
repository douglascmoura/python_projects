"""
layout.py
---------
Módulo responsável por construir a interface do usuário (Frontend).
Utiliza o sistema de Grid do Bootstrap (Linhas e Colunas) para garantir que o
dashboard seja totalmente responsivo em diferentes tamanhos de tela.

Separação de responsabilidades:
  - layout.py    → O QUE aparece na tela (estrutura e componentes)
  - callbacks.py → COMO a tela reage às interações
  - data_manager → De ONDE vêm os dados
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from data_manager import MIN_ANO, MAX_ANO, MATERIAS_PRIMAS, ESTADOS


def criar_sidebar() -> dbc.Col:
    """
    Constrói a barra lateral (Sidebar) onde ficam os controles da aplicação.
    Fundo azul-marinho escuro (#1B2A4A) com texto claro — contraste premium com o
    fundo gelo da área de gráficos.
    """
    return dbc.Col(
        [
            # ── Linha decorativa no topo (accent azure → transparent) ───────
            html.Div(className="sidebar-accent-line"),

            # ── Cabeçalho ──────────────────────────────────────────────────
            html.H2("DOCHMO", className="sidebar-logo mb-0"),
            html.P(
                "Análise do volume de processamento de petróleo e distribuição "
                "da matéria prima nas refinarias nacionais.",
                className="text-muted mt-2 mb-3",
                style={"fontSize": "0.80rem", "textAlign": "justify", "lineHeight": "1.5"},
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

            # ── FILTRO 2: Matéria Prima (MultiSelect) ──────────────────────
            # MultiSelect moderno substitui o Checklist antigo.
            # Permite busca por digitação e é consistente com os outros filtros.
            html.Label("Matéria Prima", className="filter-label mt-3 mb-2 d-block"),
            dmc.MultiSelect(
                id="filtro-materia",
                data=[{"label": m.title(), "value": m} for m in MATERIAS_PRIMAS],
                value=[],
                placeholder="Todas as matérias-primas...",
                searchable=True,
                clearable=True,
                size="sm",
                maxDropdownHeight=170,
                className="mb-2",
            ),

            # ── FILTRO 3: Estados (UF) ──────────────────────────────────────
            # MultiSelect com busca — essencial quando a lista tem 27 UFs.
            html.Label("Estado (UF)", className="filter-label mt-2 mb-2 d-block"),
            dmc.MultiSelect(
                id="filtro-estado",
                data=[{"label": e.title(), "value": e} for e in ESTADOS],
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
                    html.Hr(style={"borderColor": "rgba(173,255,255,0.12)", "marginBottom": "12px"}),
                    html.Small(
                        [
                            "Desenvolvido por: ",
                            html.A(
                                "Douglas Moura",
                                href="https://www.linkedin.com/in/douglas-chaves-moura-a545a835b",
                                target="_blank",
                                style={"color": "#ADFFFF"},
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
                                style={"color": "#ADFFFF"},
                            ),
                        ],
                        className="text-muted d-block",
                    ),
                ],
                className="sidebar-footer",
                style={"position": "absolute", "bottom": "12px", "width": "82%", "fontSize": "0.89rem"},
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
    2. Treemap (UF → Refinaria) + Rosca (Mix de Matéria Prima) — linha inferior
    """
    return dbc.Col(
        [
            # ── LINHA 1: Série Temporal (topo, largura total) ───────────────
            dbc.Row(
                dbc.Col(
                    html.Div(
                        dcc.Loading(
                            color="#007FFF",
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

            # ── LINHA 2: Treemap + Rosca (lado a lado) ─────────────────────
            dbc.Row(
                [
                    # Treemap ocupa 7/8 colunas — visualização hierárquica UF → Refinaria
                    dbc.Col(
                        html.Div(
                            dcc.Loading(
                                color="#007FFF",
                                type="cube",
                                children=dcc.Graph(
                                    id="fig-tree",
                                    style={"height": "46vh"},
                                    config={"displayModeBar": False},
                                ),
                            ),
                            className="chart-panel",
                        ),
                        md=7, lg=8,
                    ),
                    # Rosca ocupa o restante — mix percentual de matéria prima
                    dbc.Col(
                        html.Div(
                            dcc.Loading(
                                color="#007FFF",
                                type="cube",
                                children=dcc.Graph(
                                    id="fig-rosca",
                                    style={"height": "46vh"},
                                    config={"displayModeBar": False},
                                ),
                            ),
                            className="chart-panel",
                        ),
                        md=5, lg=4,
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
            # Armazena os dados filtrados na memória do navegador do usuário (Client-side).
            # Impede que os mesmos cálculos ocorram múltiplas vezes para gráficos diferentes.
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
        id="theme-root",
        style={"padding": 0, "backgroundColor": "var(--color-bg-main)", "minHeight": "100vh"},
    )
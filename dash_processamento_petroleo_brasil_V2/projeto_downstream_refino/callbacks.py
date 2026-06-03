"""
callbacks.py
------------
O "Cérebro" da aplicação. Define como o dashboard reage às interações do usuário.

Arquitetura de performance em 2 callbacks:
  1. FILTRO (Backend)  → Filtra o DataFrame pesado e salva o resultado compacto
                         na memória do navegador (dcc.Store). Executa uma vez.
  2. RENDER (Frontend) → Lê os dados compactos da Store e desenha os 3 gráficos.
                         Nunca retoca o DataFrame original.

Isso garante que o custo de filtragem não seja pago N vezes (uma por gráfico).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback

from data_manager import df_base, MIN_ANO, MAX_ANO, CORES_MATERIA_PRIMA


# =========================================================================
# FUNÇÕES UTILITÁRIAS
# =========================================================================

def figura_vazia(msg: str) -> go.Figure:
    """
    Gera um frame visualmente agradável avisando que não há dados no filtro selecionado.
    Adaptado ao tema claro: texto em azul-acinzentado sobre fundo transparente.
    """
    return go.Figure().update_layout(
        title={
            "text": f"<i>{msg}</i>",
            "x": 0.5, "y": 0.5,
            "xanchor": "center", "yanchor": "middle",
        },
        xaxis={"visible": False},
        yaxis={"visible": False},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#5E7A99", "size": 14},
    )


def fmt_br(valor) -> str:
    """
    Formata números no padrão brasileiro (1.000,00).
    Resiliente contra NaN, Inf e outros valores anômalos.
    """
    try:
        if pd.isna(valor) or valor in (float("inf"), float("-inf")):
            return "0,00"
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def fmt_suffix(valor) -> str:
    """
    Formata volume em notação compacta (k, M, B) para eixos e colorbars.
    Exemplo: 1.500.000.000 → '1,5B'
    """
    try:
        v = float(valor)
        if v >= 1_000_000_000:
            val = v / 1_000_000_000
            txt = f"{val:.1f}".replace(".", ",")
            return f"{txt.rstrip(',0').rstrip(',') if ',' in txt else txt}B"
        if v >= 1_000_000:
            val = v / 1_000_000
            txt = f"{val:.1f}".replace(".", ",")
            if txt.endswith(",0"):
                txt = txt[:-2]
            return f"{txt}M"
        if v >= 1_000:
            val = v / 1_000
            txt = f"{val:.1f}".replace(".", ",")
            if txt.endswith(",0"):
                txt = txt[:-2]
            return f"{txt}k"
        return f"{int(v)}"
    except Exception:
        return "0"


def calcular_ticks_colorbar(series):
    """
    Calcula ticks arredondados e elegantes ('nice numbers') baseados na amplitude
    da série de dados, evitando frações 'quebradas' e mantendo a notação compacta.
    """
    if series.empty:
        return [], []

    min_val = float(series.min())
    max_val = float(series.max())

    if abs(max_val - min_val) < 1.0:
        return [min_val], [fmt_suffix(min_val)]

    span = max_val - min_val
    rough_step = span / 4.0

    if rough_step <= 0:
        return [min_val, max_val], [fmt_suffix(min_val), fmt_suffix(max_val)]

    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude

    if normalized < 1.5:
        nice_step = 1.0
    elif normalized < 3.0:
        nice_step = 2.0
    elif normalized < 7.5:
        nice_step = 5.0
    else:
        nice_step = 10.0

    step = nice_step * magnitude
    nice_min = math.floor(min_val / step) * step
    nice_max = math.ceil(max_val / step) * step

    tick_vals = []
    curr = nice_min
    while curr <= nice_max + (step * 0.01):
        tick_vals.append(curr)
        curr += step

    if len(tick_vals) > 8:
        tick_vals = tick_vals[::2]

    tick_text = [fmt_suffix(v) for v in tick_vals]
    return tick_vals, tick_text


# =========================================================================
# CORES E ESCALAS — Paleta Azure (#007FFF) → Celeste (#ADFFFF)
# =========================================================================

# Escala contínua Azure → Celeste para gráficos com color_continuous_scale
ESCALA_AZURE_CELESTE = [
    [0.00, "#1B2A4A"],   # Azul-marinho — valores mínimos
    [0.30, "#007FFF"],   # Azure — valores intermediários
    [0.65, "#52C8FF"],   # Azul médio
    [1.00, "#ADFFFF"],   # Celeste neon — valores máximos
]

# Cores para hover label e linhas de grade (tema claro)
COR_HOVER_BG     = "rgba(255, 255, 255, 0.97)"
COR_HOVER_FONTE  = "#0F1E35"
COR_HOVER_BORDA  = "#D8E4F0"
COR_GRADE        = "#EBF1F8"
COR_FONTE_MAIN   = "#0F1E35"
COR_FONTE_MUTED  = "#5E7A99"


# =========================================================================
# REGISTRO DE CALLBACKS
# =========================================================================

def registrar_callbacks():

    # ─────────────────────────────────────────────────────────────────────
    # CALLBACK 1 — MOTOR DE FILTRAGEM (Backend)
    # Inputs: todos os controles da sidebar
    # Output: Store (JSON compacto dos dados filtrados) + placeholders dinâmicos
    # ─────────────────────────────────────────────────────────────────────
    @callback(
        [
            Output("store-dados",    "data"),
            Output("filtro-materia", "placeholder"),
            Output("filtro-estado",  "placeholder"),
        ],
        [
            Input("filtro-ano-inicio", "value"),
            Input("filtro-ano-fim",    "value"),
            Input("filtro-materia",    "value"),
            Input("filtro-estado",     "value"),
        ],
    )
    def filtrar_dados(ano_inicio, ano_fim, materias, estados):
        """
        Aplica máscaras booleanas no Pandas (vetorizadas, muito rápidas)
        e serializa apenas as colunas vitais para não sobrecarregar a rede.
        Também retorna placeholders dinâmicos que mostram a contagem de itens selecionados.
        """
        # Placeholders dinâmicos — mostram quantos itens foram selecionados
        if not materias:
            placeholder_mat = "Todas as matérias-primas..."
        else:
            placeholder_mat = f"{len(materias)} selecionada(s) 🔍"

        if not estados:
            placeholder_est = "Todos (digite para filtrar)..."
        else:
            placeholder_est = f"{len(estados)} selecionado(s) 🔍"

        # Guardrail: protege contra dataframe vazio
        if df_base.empty:
            return [], placeholder_mat, placeholder_est

        ano_inicio = int(ano_inicio) if ano_inicio else MIN_ANO
        ano_fim    = int(ano_fim)    if ano_fim    else MAX_ANO

        # Corrige silenciosamente se o usuário inverter os anos
        if ano_inicio > ano_fim:
            ano_inicio, ano_fim = ano_fim, ano_inicio

        # Filtragem por período
        mask = (df_base["ano"] >= ano_inicio) & (df_base["ano"] <= ano_fim)

        # Filtragem por matéria prima (vazio = todas)
        if materias:
            mask &= df_base["materia_prima"].isin(materias)

        # Filtragem por estado (vazio = todos)
        if estados:
            mask &= df_base["unidade_da_federacao"].isin(estados)

        # Transmite apenas as colunas necessárias para minimizar o payload
        cols = ["data", "unidade_da_federacao", "refinaria", "materia_prima", "processado"]
        records = df_base.loc[mask, cols].to_dict("records")
        return records, placeholder_mat, placeholder_est


    # ─────────────────────────────────────────────────────────────────────
    # CALLBACK 2 — RENDERIZAÇÃO GRÁFICA (Frontend)
    # Input: Store (dados já filtrados e em memória)
    # Outputs: os 3 gráficos Plotly
    # ─────────────────────────────────────────────────────────────────────
    @callback(
        [
            Output("fig-linha", "figure"),
            Output("fig-tree",  "figure"),
            Output("fig-rosca", "figure"),
        ],
        Input("store-dados", "data"),
        [
            State("filtro-ano-inicio", "value"),
            State("filtro-ano-fim",    "value"),
        ],
    )
    def atualizar_graficos(dados_em_memoria, ano_inicio, ano_fim):
        """
        Consome o JSON compacto da Store e gera os três objetos Figure do Plotly.
        State é usado para LER o período sem re-disparar o callback.
        """
        if not dados_em_memoria:
            msg = "Sem dados para os filtros selecionados"
            return figura_vazia(msg), figura_vazia(msg), figura_vazia(msg)

        df = pd.DataFrame(dados_em_memoria)
        df["processado"] = pd.to_numeric(df["processado"], errors="coerce").fillna(0)

        # Normalização para Title Case (apresentação)
        df["materia_prima_fmt"] = df["materia_prima"].str.title()

        # Ordem e cores mapeadas para Title Case
        ordem_materias = ["Petróleo Nacional", "Petróleo Importado", "Outras Cargas"]
        cores_fmt = {k.title(): v for k, v in CORES_MATERIA_PRIMA.items()}
        materias_presentes = [m for m in ordem_materias if m in df["materia_prima_fmt"].unique()]

        # String de período para títulos dinâmicos
        ano_i = ano_inicio if ano_inicio else MIN_ANO
        ano_f = ano_fim    if ano_fim    else MAX_ANO
        str_periodo = f"({ano_i} – {ano_f})"

        # ═══════════════════════════════════════════════════════════════
        # 1. SÉRIE TEMPORAL DE LINHA
        # ═══════════════════════════════════════════════════════════════
        fig_linha = _criar_fig_linha(df, materias_presentes, cores_fmt, str_periodo)

        # ═══════════════════════════════════════════════════════════════
        # 2. TREEMAP — Concentração por UF → Refinaria
        # ═══════════════════════════════════════════════════════════════
        fig_tree = _criar_fig_treemap(df, str_periodo)

        # ═══════════════════════════════════════════════════════════════
        # 3. ROSCA — Mix de Matéria Prima
        # ═══════════════════════════════════════════════════════════════
        fig_rosca = _criar_fig_rosca(df, materias_presentes, cores_fmt, str_periodo)

        return fig_linha, fig_tree, fig_rosca


# =========================================================================
# FUNÇÕES AUXILIARES DE RENDERIZAÇÃO (uma por gráfico)
# =========================================================================

def _criar_fig_linha(df, materias_presentes, cores_fmt, str_periodo) -> go.Figure:
    """Série temporal agrupada por matéria prima — tema claro."""
    df_linha = (
        df.groupby(["data", "materia_prima_fmt"], as_index=False, observed=True)["processado"]
        .sum()
    )
    df_linha["processado_br"] = df_linha["processado"].apply(fmt_br)

    fig = px.line(
        df_linha,
        x="data",
        y="processado",
        color="materia_prima_fmt",
        custom_data=["processado_br"],
        category_orders={"materia_prima_fmt": materias_presentes},
        color_discrete_map=cores_fmt,
        template="plotly_white",
        labels={"materia_prima_fmt": "Matéria Prima:"},
    )
    fig.update_layout(
        title=dict(
            text=f"Evolução Temporal do Processamento de Petróleo {str_periodo}",
            x=0.01, y=0.96,
            xanchor="left", yanchor="top",
            font=dict(size=16, color=COR_FONTE_MAIN),
        ),
        xaxis_title="Período",
        yaxis_title="Volume Processado (m³)",
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"r": 12, "t": 72, "l": 12, "b": 10},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font={"size": 10, "color": COR_FONTE_MUTED},
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=COR_HOVER_BG,
            font_color=COR_HOVER_FONTE,
            bordercolor=COR_HOVER_BORDA,
        ),
        xaxis=dict(gridcolor=COR_GRADE, showspikes=True, spikedash="dot", spikecolor=COR_HOVER_BORDA),
        yaxis=dict(gridcolor=COR_GRADE),
        font={"color": COR_FONTE_MAIN},
    )
    fig.update_traces(
        line=dict(width=2.5),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Processado: %{customdata[0]} m³"
            "<extra></extra>"
        ),
    )
    return fig


def _criar_fig_treemap(df, str_periodo) -> go.Figure:
    """Treemap hierárquico UF → Refinaria com escala Azure → Celeste."""
    df_share = (
        df.groupby(["unidade_da_federacao", "refinaria"], as_index=False, observed=True)["processado"]
        .sum()
    )
    df_share = df_share[df_share["processado"] > 0]

    # Title Case para apresentação
    df_share["uf_fmt"]       = df_share["unidade_da_federacao"].str.title()
    df_share["refinaria_fmt"] = df_share["refinaria"].str.title()

    fig = px.treemap(
        df_share,
        path=[px.Constant("Brasil 🇧🇷"), "uf_fmt", "refinaria_fmt"],
        values="processado",
        color="processado",
        color_continuous_scale=ESCALA_AZURE_CELESTE,
        title=f"Concentração do Refino Nacional {str_periodo}",
        template="plotly_white",
    )

    tick_vals, tick_text = calcular_ticks_colorbar(df_share["processado"])
    fig.update_traces(
        root_color="#F5F7FA",
        texttemplate="<b>%{label}</b><br>%{value:,.0f} m³",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "<b>Processado:</b> %{value:,.0f} m³<br>"
            "<b>Participação:</b> %{percentParent:.1%}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(color="#F5F7FA", width=1.2),
            pad=dict(t=28, l=4, r=4, b=4),
        ),
        textfont={"size": 11, "color": "#FFFFFF"},
    )
    fig.update_layout(
        separators=",.",
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"r": 8, "t": 48, "l": 8, "b": 8},
        coloraxis_colorbar=dict(
            title={"text": "Vol. Process. (m³)", "font": {"color": COR_FONTE_MUTED, "size": 11}},
            thickness=12,
            len=0.8,
            tickfont={"color": COR_FONTE_MUTED, "size": 10},
            tickvals=tick_vals,
            ticktext=tick_text,
        ),
        font={"color": COR_FONTE_MAIN},
        hoverlabel=dict(
            bgcolor=COR_HOVER_BG,
            font_color=COR_HOVER_FONTE,
            bordercolor=COR_HOVER_BORDA,
        ),
    )
    return fig


def _criar_fig_rosca(df, materias_presentes, cores_fmt, str_periodo) -> go.Figure:
    """Gráfico de rosca (donut) com mix percentual de matéria prima — Azure/Celeste."""
    df_rosca = (
        df.groupby("materia_prima_fmt", as_index=False, observed=True)["processado"]
        .sum()
    )
    df_rosca = df_rosca[df_rosca["processado"] > 0]

    fig = px.pie(
        df_rosca,
        values="processado",
        names="materia_prima_fmt",
        hole=0.55,
        title=f"Tipo de Matéria Prima {str_periodo}",
        template="plotly_white",
        color="materia_prima_fmt",
        category_orders={"materia_prima_fmt": materias_presentes},
        color_discrete_map=cores_fmt,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont=dict(color=COR_FONTE_MAIN, size=11),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Volume: %{value:,.2f} m³<br>"
            "Participação: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(line=dict(color="#F5F7FA", width=2)),
    )
    fig.update_layout(
        separators=",.",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        font={"color": COR_FONTE_MAIN},
        legend=dict(
            font={"size": 10, "color": COR_FONTE_MUTED},
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(font=dict(color=COR_FONTE_MAIN, size=15)),
        hoverlabel=dict(
            bgcolor=COR_HOVER_BG,
            font_color=COR_HOVER_FONTE,
            bordercolor=COR_HOVER_BORDA,
        ),
    )
    return fig
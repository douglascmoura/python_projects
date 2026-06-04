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

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback

from data_manager import (
    df_base, geojson_brasil, MIN_ANO, MAX_ANO, CORES_PRODUTO,
    REGIOES, PRODUTOS, ESTADOS,
)


# =========================================================================
# FUNÇÕES UTILITÁRIAS
# =========================================================================

def figura_vazia(msg: str) -> go.Figure:
    """
    Gera um frame escuro com aviso centralizado para filtros sem resultado.
    Evita que o usuário veja um frame em branco sem contexto.
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
        font={"color": "#808A93", "size": 14},
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


def fmt_m3(valor) -> str:
    """Formata volume em m³ com separadores BR e sufixo de unidade."""
    try:
        v = float(valor)
        if v >= 1_000_000:
            return f"{v / 1_000_000:.2f}M m³".replace(".", ",")
        if v >= 1_000:
            return f"{fmt_br(v)} m³"
        return f"{fmt_br(v)} m³"
    except Exception:
        return "0 m³"

def fmt_suffix(valor) -> str:
    """
    Formata volume em notação compacta (k, M, B) para eixos e colorbars.
    Exemplo: 1.500.000.000 -> '1,5B'
    """
    try:
        v = float(valor)
        if v >= 1_000_000_000:
            val = v / 1_000_000_000
            txt = f"{val:.1f}".replace(".", ",")
            if txt.endswith(",0"):
                txt = txt[:-2]
            return f"{txt}B"
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
    da série de dados, evitando frações 'quebradas' (como 840,5M) e mantendo
    a notação comercial brasileira com 'B' de bilhões.
    """
    if series.empty:
        return [], []
    
    min_val = float(series.min())
    max_val = float(series.max())
    
    if abs(max_val - min_val) < 1.0:
        return [min_val], [fmt_suffix(min_val)]
    
    import math
    span = max_val - min_val
    
    # Proporção aproximada para obter entre 4 e 6 divisões (5 ticks)
    rough_step = span / 4.0
    
    if rough_step <= 0:
        return [min_val, max_val], [fmt_suffix(min_val), fmt_suffix(max_val)]
        
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude
    
    # Seleciona intervalos limpos (multiplos de 1, 2, 5, 10 da ordem de magnitude)
    if normalized < 1.5:
        nice_step = 1.0
    elif normalized < 3.0:
        nice_step = 2.0
    elif normalized < 7.5:
        nice_step = 5.0
    else:
        nice_step = 10.0
        
    step = nice_step * magnitude
    
    # Arredonda o mínimo e máximo para os múltiplos limpos mais próximos
    nice_min = math.floor(min_val / step) * step
    nice_max = math.ceil(max_val / step) * step
    
    # Gera a sequência de ticks arredondados
    tick_vals = []
    curr = nice_min
    while curr <= nice_max + (step * 0.01):
        tick_vals.append(curr)
        curr += step
        
    # Se a imprecisão gerou ticks demais, ajustamos para a legibilidade
    if len(tick_vals) > 8:
        tick_vals = tick_vals[::2]
        
    tick_text = [fmt_suffix(v) for v in tick_vals]
    return tick_vals, tick_text

# =========================================================================
# REGISTRO DE CALLBACKS
# =========================================================================

def registrar_callbacks():

    # ─────────────────────────────────────────────────────────────────────
    # CALLBACK 1 — MOTOR DE FILTRAGEM (Backend)
    # Inputs: todos os controles da sidebar
    # Output: Store (JSON compacto dos dados filtrados)
    # ─────────────────────────────────────────────────────────────────────
    @callback(
        [
            Output("store-dados", "data"),
            Output("filtro-regiao", "placeholder"),
            Output("filtro-produto", "placeholder"),
            Output("filtro-uf", "placeholder"),
        ],
        [
            Input("filtro-ano-inicio", "value"),
            Input("filtro-ano-fim",    "value"),
            Input("filtro-regiao",     "value"),
            Input("filtro-produto",    "value"),
            Input("filtro-uf",         "value"),
        ],
    )
    def filtrar_dados(ano_inicio, ano_fim, regioes, produtos, ufs):
        """
        Aplica máscaras booleanas no Pandas (vetorizadas, muito rápidas)
        e serializa apenas as colunas vitais para não sobrecarregar a rede.
        """
        # Calcular placeholders dinâmicos baseados na seleção real (se vazia, significa todos)
        if not regioes:
            placeholder_reg = "Todas as regiões..."
        else:
            placeholder_reg = f"{len(regioes)} selecionadas 🔍"

        if not produtos:
            placeholder_prod = "Todos os combustíveis..."
        else:
            placeholder_prod = f"{len(produtos)} selecionados 🔍"

        if not ufs:
            placeholder_uf = "Todos os estados..."
        else:
            placeholder_uf = f"{len(ufs)} selecionados 🔍"

        # Guardrails defensivos: previne quebras se o dataframe estiver vazio
        if df_base.empty:
            return [], placeholder_reg, placeholder_prod, placeholder_uf

        ano_inicio = int(ano_inicio) if ano_inicio else MIN_ANO
        ano_fim    = int(ano_fim)    if ano_fim    else MAX_ANO

        # Se o usuário inverter os anos, corrigimos silenciosamente
        if ano_inicio > ano_fim:
            ano_inicio, ano_fim = ano_fim, ano_inicio

        # Começamos a máscara com a filtragem por período de anos
        mask = (df_base["ano"] >= ano_inicio) & (df_base["ano"] <= ano_fim)

        # Se o usuário selecionar regiões específicas, aplicamos o filtro (vazio = todas as regiões)
        if regioes:
            mask &= df_base["regiao"].isin(regioes)

        # Se o usuário selecionar produtos específicos, aplicamos o filtro (vazio = todos os combustíveis)
        if produtos:
            mask &= df_base["produto"].isin(produtos)

        # Se o usuário selecionar UFs específicas, aplicamos o filtro (vazio = todos os estados)
        if ufs:
            mask &= df_base["uf"].isin(ufs)

        # Transmite apenas as colunas necessárias para minimizar o payload
        cols = ["data", "ano", "regiao", "uf", "produto", "vendas"]
        records = df_base.loc[mask, cols].to_dict("records")
        return records, placeholder_reg, placeholder_prod, placeholder_uf

    # ─────────────────────────────────────────────────────────────────────
    # CALLBACK 2 — RENDERIZAÇÃO GRÁFICA (Frontend)
    # Input: Store (dados já filtrados e em memória)
    # Outputs: os 3 gráficos Plotly
    # ─────────────────────────────────────────────────────────────────────
    @callback(
        [
            Output("fig-linha",   "figure"),
            Output("fig-mapa",    "figure"),
            Output("fig-treemap", "figure"),
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
            msg = "Nenhum dado para os filtros selecionados"
            return figura_vazia(msg), figura_vazia(msg), figura_vazia(msg)

        df = pd.DataFrame(dados_em_memoria)
        df["data"]   = pd.to_datetime(df["data"])
        df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce").fillna(0)

        # String de período para títulos dinâmicos
        ano_i = ano_inicio if ano_inicio else MIN_ANO
        ano_f = ano_fim    if ano_fim    else MAX_ANO
        str_periodo = f"({ano_i} – {ano_f})"

        # Ordem de exibição padronizada na legenda
        ordem_produtos = [
            "ÓLEO DIESEL", "GASOLINA C", "GLP", "ETANOL HIDRATADO",
            "ÓLEO COMBUSTÍVEL", "QUEROSENE DE AVIAÇÃO",
            "QUEROSENE ILUMINANTE", "GASOLINA DE AVIAÇÃO",
        ]
        produtos_presentes = [p for p in ordem_produtos if p in df["produto"].unique()]

        # Normaliza os nomes para Title Case (apresentação)
        df["produto_fmt"] = df["produto"].str.title()
        cores_fmt = {k.title(): v for k, v in CORES_PRODUTO.items()}
        ordem_fmt = [p.title() for p in produtos_presentes]

        # ═══════════════════════════════════════════════════════════════
        # 1. SÉRIE TEMPORAL DE LINHA
        # ═══════════════════════════════════════════════════════════════
        df_linha = (
            df.groupby(["data", "produto_fmt"], as_index=False, observed=True)["vendas"]
            .sum()
        )
        df_linha["vendas_fmt"] = df_linha["vendas"].apply(fmt_br)

        fig_linha = px.line(
            df_linha,
            x="data",
            y="vendas",
            color="produto_fmt",
            custom_data=["vendas_fmt"],
            category_orders={"produto_fmt": ordem_fmt},
            color_discrete_map=cores_fmt,
            template="plotly_dark",
            labels={"produto_fmt": "Combustível:"},
        )
        fig_linha.update_layout(
            title=dict(
                text=f"Evolução das Vendas de Combustíveis no Brasil {str_periodo}",
                x=0.01,
                y=0.96,
                xanchor="left",
                yanchor="top",
                font=dict(size=16)
            ),
            xaxis_title="Período",
            yaxis_title="Volume Vendido (m³)",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#1A2830",
            margin={"r": 12, "t": 72, "l": 12, "b": 10},
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="right",
                x=1,
                font={"size": 10},
                bgcolor="rgba(0,0,0,0)"
            ),
            hoverlabel=dict(
                bgcolor="#162127",
                font_color="#EAEAEA",
                bordercolor="#2A3E4A",
            ),
            xaxis=dict(
                showspikes=True,
                spikedash="dot",
                spikecolor="#495056",
                spikethickness=1.5,
                gridcolor="#1A2830", #"#1E2D35",
            ),
            yaxis=dict(gridcolor="#1E2D35"),
            font={"color": "#EAEAEA"},
        )
        fig_linha.update_traces(
            line=dict(width=2),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Volume: %{customdata[0]} m³"
                "<extra></extra>"
            ),
        )

        # ═══════════════════════════════════════════════════════════════
        # 2. MAPA CLOROPLÉTICO POR UF
        # ═══════════════════════════════════════════════════════════════
        df_mapa = (
            df.groupby("uf", as_index=False, observed=True)["vendas"]
            .sum()
        )
        # df_mapa["vendas_fmt"] = df_mapa["vendas"].apply(fmt_br)

        # Configuração do mapa coroplético com GeoJSON local
        fig_mapa = px.choropleth_map(
            df_mapa,
            geojson=geojson_brasil,
            locations="uf",
            featureidkey="properties.uf_dataset",
            color="vendas",
            color_continuous_scale=[
                [0.0,  "#1E2D35"],
                [0.25, "#3A4A40"],
                [0.5,  "#724C39"],
                [0.75, "#9E6A4A"],
                [1.0,  "#EAEAEA"],
            ],
            custom_data=["vendas"],
            hover_name="uf",
            map_style="carto-darkmatter",
            zoom=2.8,
            center={"lat": -14.2, "lon": -51.9},
            title=f"Volume de Vendas por Estado {str_periodo}",
            opacity=0.85,
        )

        fig_mapa.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Volume: %{customdata[0]:,.2f} m³"
                "<extra></extra>"
            ),
            marker_line_color="#0C151A",
            marker_line_width=0.8
        )
        tick_vals_mapa, tick_text_mapa = calcular_ticks_colorbar(df_mapa["vendas"])
        fig_mapa.update_layout(
            separators=",.",
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r": 0, "t": 44, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title={"text": "Volume (m³)", "font": {"color": "#808A93", "size": 11}},
                thickness=12,
                len=0.8,
                tickfont={"color": "#808A93", "size": 10},
                # tickformat=",.2s",
                tickvals=tick_vals_mapa,
                ticktext=tick_text_mapa,
            ),
            font={"color": "#EAEAEA"},
        )

        # ═══════════════════════════════════════════════════════════════
        # 3. TREEMAP HIERÁRQUICO — Brasil → Região → UF
        # ═══════════════════════════════════════════════════════════════
        df_tree = (
            df.groupby(["regiao", "uf"], as_index=False, observed=True)["vendas"]
            .sum()
        )
        df_tree = df_tree[df_tree["vendas"] > 0]

        # Normaliza os nomes para Title Case
        df_tree["regiao_fmt"] = df_tree["regiao"].str.title()
        df_tree["uf_fmt"]     = df_tree["uf"].str.title()

        fig_tree = px.treemap(
            df_tree,
            path=[px.Constant("Brasil 🇧🇷"), "regiao_fmt", "uf_fmt"],
            values="vendas",
            color="vendas",
            color_continuous_scale=[
                [0.0,  "#1E2D35"],
                [0.3,  "#3A4A50"],
                [0.6,  "#724C39"],
                [0.85, "#9E6A4A"],
                [1.0,  "#EAEAEA"],
            ],
            title=f"Concentração Regional das Vendas {str_periodo}",
            template="plotly_dark",
        )
        fig_tree.update_traces(
            root_color="#0C151A",
            texttemplate="<b>%{label}</b><br>%{value:,.0f} m³",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "<b>Volume:</b> %{value:,.0f} m³<br>"
                "<b>Participação:</b> %{percentParent:.1%}"
                "<extra></extra>"
            ),
            marker=dict(
                line=dict(color="#0C151A", width=1.2),
                pad=dict(t=28, l=4, r=4, b=4),
            ),
            textfont={"size": 11},
        )
        tick_vals_tree, tick_text_tree = calcular_ticks_colorbar(df_tree["vendas"])
        fig_tree.update_layout(
            separators=",.",
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r": 8, "t": 48, "l": 8, "b": 8},
            coloraxis_colorbar=dict(
                title={"text": "Volume (m³)", "font": {"color": "#808A93", "size": 11}},
                thickness=12,
                len=0.8,
                tickfont={"color": "#808A93", "size": 10},
                # tickformat=",.2s",
                tickvals=tick_vals_tree,
                ticktext=tick_text_tree,
            ),
            font={"color": "#EAEAEA"},
            hoverlabel=dict(
                bgcolor="rgba(22, 33, 39, 0.95)",
                font_color="#EAEAEA",
                bordercolor="#2A3E4A",
            ),
        )

        return fig_linha, fig_mapa, fig_tree

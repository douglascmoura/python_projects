"""
callbacks.py
------------
O "Cérebro" da aplicação. Define como o dashboard reage às interações do usuário.
Implementa a lógica MVC isolada para o controle reativo.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, no_update
import math

from data_manager import df_base, PADROES_DISPONIVEIS, CORES_USO, MIN_ANO, MAX_ANO

# =========================================================================
# FUNÇÕES UTILITÁRIAS E NICE NUMBERS
# =========================================================================

def figura_vazia(mensagem: str) -> go.Figure:
    """Gera um frame visualmente agradável avisando que não há dados no filtro."""
    return go.Figure().update_layout(
        title={"text": f"<i>{mensagem}</i>", "x": 0.5, "y": 0.5, "xanchor": "center", "yanchor": "middle"}, 
        xaxis={"visible": False}, yaxis={"visible": False}, 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
        font={"color": "#5E7A99", "size": 14}
    )

def fmt_moeda(valor) -> str:
    """Formatação local com fallback seguro para string em hover."""
    try:
        if pd.isna(valor) or valor in (float('inf'), float('-inf')): return "R$ 0,00"
        return f'R$ {float(valor):,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def fmt_area(valor) -> str:
    try:
        if pd.isna(valor) or valor in (float('inf'), float('-inf')): return "0,0"
        return f'{float(valor):,.1f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,0"

def fmt_suffix(valor) -> str:
    """Formata valor em notação monetária completa sem centavos (R$ X.XXX)."""
    try:
        v = float(valor)
        return f'R$ {v:,.0f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0"

def calcular_ticks_colorbar(series):
    """Calcula ticks arredondados (nice numbers) para eixos lineares."""
    if series.empty: return [], []
    min_val, max_val = float(series.min()), float(series.max())
    if abs(max_val - min_val) < 1.0: return [min_val], [fmt_suffix(min_val)]
    
    span = max_val - min_val
    rough_step = span / 4.0
    if rough_step <= 0: return [min_val, max_val], [fmt_suffix(min_val), fmt_suffix(max_val)]
    
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude
    if normalized < 1.5: nice_step = 1.0
    elif normalized < 3.0: nice_step = 2.0
    elif normalized < 7.5: nice_step = 5.0
    else: nice_step = 10.0
    
    step = nice_step * magnitude
    nice_min = math.floor(min_val / step) * step
    nice_max = math.ceil(max_val / step) * step
    tick_vals = []
    curr = nice_min
    while curr <= nice_max + (step * 0.01):
        tick_vals.append(curr)
        curr += step
    if len(tick_vals) > 8: tick_vals = tick_vals[::2]
    return tick_vals, [fmt_suffix(v) for v in tick_vals]

# =========================================================================
# CORES E TEMA PREMIUM
# =========================================================================
COR_FONTE_MAIN   = "#E0E0E0"
COR_FONTE_MUTED  = "#8C8C8C"
COR_HOVER_BG     = "#141216"
COR_HOVER_BORDA  = "#2BBACA"
COR_GRADE        = "#222222"

ESCALA_TEAL = [
    [0.0, "#114a51"],
    [0.5, "#2BBACA"],
    [1.0, "#a9e3e9"]
]

# =========================================================================
# REGISTRO DE CALLBACKS
# =========================================================================
def registrar_callbacks():

    # --- CALLBACK 1: UX DOS BOTÕES DE SELEÇÃO RÁPIDA ---
    @callback(
        Output("filtro-padrao", "value"),
        [Input("btn-select-all", "n_clicks"), Input("btn-clear-all", "n_clicks")], 
        prevent_initial_call=True
    )
    def gerenciar_botoes_selecao(n_all, n_clear):
        botao_clicado = ctx.triggered_id 
        if botao_clicado == "btn-select-all": return PADROES_DISPONIVEIS 
        elif botao_clicado == "btn-clear-all": return [] 
        return no_update 

    # --- CALLBACK 2: MOTOR DE FILTRAGEM (Backend) ---
    @callback(
        [Output('store-dados-filtrados', 'data'), Output('filtro-bairro', 'placeholder'), Output('filtro-padrao', 'placeholder')],
        [Input("filtro-ano", "value"), Input("filtro-uso", "value"), Input("filtro-padrao", "value"), Input("filtro-bairro", "value")]
    )
    def processar_filtros(ano_selecionado, usos_selecionados, padroes_selecionados, bairros_selecionados):
        placeholder_bairro = "Todos (digite para filtrar)..."
        placeholder_padrao = "Todos os padrões..."
        
        if bairros_selecionados and len(bairros_selecionados) > 0:
            placeholder_bairro = f"{len(bairros_selecionados)} selecionados 🔍"
            
        if padroes_selecionados and len(padroes_selecionados) > 0:
            placeholder_padrao = f"{len(padroes_selecionados)} selecionados 🔍"

        if df_base.empty or not usos_selecionados:
            return [], placeholder_bairro, placeholder_padrao
        
        mask = (df_base['exercicio'] == ano_selecionado) & (df_base['tipo_uso_imovel'].isin(usos_selecionados))
        if padroes_selecionados: 
            mask &= df_base['padrao_construcao'].isin(padroes_selecionados)
            
        if bairros_selecionados and len(bairros_selecionados) > 0:
            mask &= df_base['bairro'].isin(bairros_selecionados)
        
        colunas_necessarias = ['bairro', 'tipo_uso_imovel', 'padrao_construcao', 'valor_m2', 'latitude', 'longitude', 'area_edificada', 'vl_base_calculo']
        return df_base[mask][colunas_necessarias].to_dict('records'), placeholder_bairro, placeholder_padrao

    # --- CALLBACK 3: RENDERIZAÇÃO GRÁFICA (Frontend) ---
    @callback(
        [Output("mapa-imoveis", "figure"), Output("grafico-boxplot", "figure"), Output("grafico-bairros", "figure")],
        Input('store-dados-filtrados', 'data'), State('filtro-ano', 'value'), prevent_initial_call=False
    )
    def atualizar_graficos(dados_em_memoria, ano_selecionado): 
        if not dados_em_memoria: 
            # Mapa vazio seguro
            fig_empty_map = px.scatter_mapbox(lat=[-3.7319], lon=[-38.5267], zoom=10.5).update_layout(mapbox_style="carto-darkmatter", margin={"r": 0, "t": 0, "l": 0, "b": 0})
            return fig_empty_map, figura_vazia("Sem dados"), figura_vazia("Sem dados")

        df_filtrado = pd.DataFrame(dados_em_memoria)
        
        try:
            # ==========================================
            # 1. MAPA DE TRANSAÇÕES
            # ==========================================
            df_mapa = df_filtrado.sample(n=10000, random_state=42) if len(df_filtrado) > 10000 else df_filtrado.copy()
            df_mapa["valor_m2_fmt"] = [fmt_moeda(x) for x in df_mapa["valor_m2"]]
            df_mapa["vl_base_calculo_fmt"] = [fmt_moeda(x) for x in df_mapa["vl_base_calculo"]]
            df_mapa["area_edificada_fmt"] = [fmt_area(x) for x in df_mapa["area_edificada"]]

            titulo_mapa = f"Mapa de Transações: Valor do M² por Região ({ano_selecionado})"
            
            # Normalização (Capping de outliers na escala de cor)
            color_min = df_mapa["valor_m2"].quantile(0.05)
            color_max = df_mapa["valor_m2"].quantile(0.95)

            fig_mapa = px.scatter_map(
                df_mapa, lat="latitude", lon="longitude", color="valor_m2", size="area_edificada", hover_name="bairro", 
                custom_data=["tipo_uso_imovel", "vl_base_calculo_fmt", "valor_m2_fmt", "area_edificada_fmt"], 
                color_continuous_scale=ESCALA_TEAL, range_color=[color_min, color_max], size_max=40, zoom=10.5, center={"lat": df_mapa["latitude"].mean(), "lon": df_mapa["longitude"].mean()}, 
                map_style="carto-darkmatter", title=f'<b>{titulo_mapa}</b>' 
            )
            
            fig_mapa.update_traces(
                marker=dict(sizemin=1), 
                hovertemplate="<b>%{hovertext}</b><br><br>Tipo de uso: %{customdata[0]}<br>Valor venal: %{customdata[1]}<br>Valor do m²: %{customdata[2]}<br>Área edificada: %{customdata[3]} m²<extra></extra>"
            )
            
            # Ticks nice numbers pro mapa respeitando o capping de cores
            tick_vals_mapa, tick_text_mapa = calcular_ticks_colorbar(pd.Series([color_min, color_max]))
            
            fig_mapa.update_layout(
                separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": COR_FONTE_MAIN}, 
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                title=dict(font=dict(size=14, color=COR_FONTE_MAIN)),
                coloraxis_colorbar=dict(
                    title={"text": "Valor M² (R$)", "font": {"size": 11, "color": COR_FONTE_MUTED}}, 
                    thickness=12, len=0.85,
                    tickvals=tick_vals_mapa, ticktext=tick_text_mapa, tickfont={"size": 10, "color": COR_FONTE_MAIN}
                ),
                hoverlabel=dict(bgcolor=COR_HOVER_BG, bordercolor=COR_HOVER_BORDA, font_size=14, font_family="Segoe UI", font_color=COR_FONTE_MAIN)
            )

            # ==========================================
            # 2. BOXPLOT DE DISPERSÃO
            # ==========================================
            limite = df_filtrado['valor_m2'].quantile(0.99)
            limite = limite if pd.notna(limite) and limite != float('inf') else float('inf')
            df_boxplot_data = df_filtrado[df_filtrado['valor_m2'] <= limite].copy()
            df_boxplot_data["valor_m2_fmt"] = [fmt_moeda(x) for x in df_boxplot_data["valor_m2"]]

            fig_boxplot = px.box(
                df_boxplot_data, x='padrao_construcao', y='valor_m2', color='tipo_uso_imovel', 
                points='outliers', custom_data=["valor_m2_fmt"], color_discrete_map=CORES_USO, 
                title=f'<b>Dispersão do Valor do M²</b><br><span style="font-size: 11px; color: {COR_FONTE_MUTED};">Sem Outliers Extremos</span>', 
                labels={'padrao_construcao': 'Padrão', 'tipo_uso_imovel': 'Uso:'}
            )
            fig_boxplot.update_traces(hovertemplate="<b>Padrão:</b> %{x}<br><b>Tipo:</b> %{fullData.name}<br><b>Valor do m²:</b> %{customdata[0]}<br><extra></extra>")
            
            tick_vals_box, tick_text_box = calcular_ticks_colorbar(df_boxplot_data['valor_m2'])
            
            fig_boxplot.update_layout(
                separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": COR_FONTE_MAIN},
                title=dict(font=dict(size=14, color=COR_FONTE_MAIN)),
                margin={"r": 10, "t": 60, "l": 10, "b": 10}, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
                yaxis=dict(
                    title="Valor M² (R$)", showgrid=True, gridcolor=COR_GRADE, zeroline=False, 
                    tickvals=tick_vals_box, ticktext=tick_text_box
                ),
                xaxis=dict(showgrid=False, title="", tickangle=-45),
                hoverlabel=dict(bgcolor=COR_HOVER_BG, bordercolor=COR_HOVER_BORDA, font_size=12, font_family="Segoe UI", font_color=COR_FONTE_MAIN)
            )

            # ==========================================
            # 3. BARRAS HORIZONTAIS (TOP 10 BAIRROS)
            # ==========================================
            df_bairros = df_filtrado.groupby('bairro', as_index=False)['valor_m2'].mean()
            df_top10 = df_bairros.nlargest(10, 'valor_m2').copy()
            df_top10["valor_m2_fmt"] = [fmt_moeda(x) for x in df_top10["valor_m2"]]

            qtd = len(df_top10)
            if qtd == 10:
                titulo_barras = f"<b>Top 10 Bairros: Média M²</b><br><span style='font-size: 11px; color: {COR_FONTE_MUTED};'>({ano_selecionado})</span>"
            elif qtd > 1:
                titulo_barras = f"<b>Ranking: {qtd} Bairros</b><br><span style='font-size: 11px; color: {COR_FONTE_MUTED};'>({ano_selecionado})</span>"
            elif qtd == 1:
                titulo_barras = f"<b>Média M² do Bairro</b><br><span style='font-size: 11px; color: {COR_FONTE_MUTED};'>({ano_selecionado})</span>"
            else:
                titulo_barras = f"<b>Sem dados no ano selecionado</b>"

            fig_barras = px.bar(
                df_top10, x='valor_m2', y='bairro', orientation='h', color='valor_m2', 
                color_continuous_scale=ESCALA_TEAL, title=titulo_barras, 
                labels={'valor_m2': 'Média Valor M² (R$)', 'bairro': 'Bairro'}, text='valor_m2_fmt' 
            )
            fig_barras.update_traces(textposition='inside', hovertemplate="<b>Bairro:</b> %{y}<br><b>Média M²:</b> %{text}<extra></extra>")
            
            tick_vals_bar, tick_text_bar = calcular_ticks_colorbar(df_top10['valor_m2'])
            
            fig_barras.update_layout(
                separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": COR_FONTE_MAIN},
                title=dict(font=dict(size=14, color=COR_FONTE_MAIN)),
                margin={"r": 10, "t": 60, "l": 10, "b": 10}, 
                yaxis={'categoryorder': 'total ascending', 'automargin': True, 'title': ''}, 
                xaxis=dict(showgrid=True, gridcolor=COR_GRADE, zeroline=False, title="", tickvals=tick_vals_bar, ticktext=tick_text_bar, tickangle=0),
                coloraxis_showscale=False,
                hoverlabel=dict(bgcolor=COR_HOVER_BG, bordercolor=COR_HOVER_BORDA, font_size=12, font_family="Segoe UI", font_color=COR_FONTE_MAIN)
            )

            return fig_mapa, fig_boxplot, fig_barras
            
        except Exception as e:
            print(f"ERRO DE RENDERIZAÇÃO: {e}")
            return px.scatter_mapbox(lat=[-3.7319], lon=[-38.5267], zoom=10).update_layout(mapbox_style="carto-darkmatter"), figura_vazia("Erro"), figura_vazia("Erro")

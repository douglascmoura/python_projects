"""
callbacks.py
------------
Regras de negócio e renderização dos gráficos para o Dashboard.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback

from data_manager import df_base, geojson_brasil, MIN_ANO, MAX_ANO, CORES_LOCALIZACAO

def empty_figure(msg: str) -> go.Figure:
    return go.Figure().update_layout(
        title={"text": f"<i>{msg}</i>", "x": 0.5, "y": 0.5, "xanchor": "center", "yanchor": "middle"}, 
        xaxis={"visible": False}, yaxis={"visible": False}, 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": "#7BA0C4"}
    )

def fmt_br(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_suffix(valor) -> str:
    try:
        v = float(valor)
        if v >= 1_000_000_000:
            val = v / 1_000_000_000
            txt = f"{val:.1f}".replace(".", ",")
            if txt.endswith(",0"): txt = txt[:-2]
            return f"{txt}B"
        if v >= 1_000_000:
            val = v / 1_000_000
            txt = f"{val:.1f}".replace(".", ",")
            if txt.endswith(",0"): txt = txt[:-2]
            return f"{txt}M"
        if v >= 1_000:
            val = v / 1_000
            txt = f"{val:.1f}".replace(".", ",")
            if txt.endswith(",0"): txt = txt[:-2]
            return f"{txt}k"
        return f"{int(v)}"
    except Exception:
        return "0"

def calcular_ticks_colorbar(series):
    if series.empty: return [], []
    min_val, max_val = float(series.min()), float(series.max())
    if abs(max_val - min_val) < 1.0: return [min_val], [fmt_suffix(min_val)]
    import math
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

def calcular_ticks_log_nice(series):
    if series.empty: return [], []
    series_clean = series.copy()
    series_clean[series_clean < 0] = 0
    
    # Se houver apenas 1 único valor positivo no mapa, fazemos ticks unitários (0 e o valor exato)
    series_positive = series_clean[series_clean > 0]
    if len(series_positive.unique()) == 1:
        val = float(series_positive.iloc[0])
        return [0, np.log10(val + 1)], ["0", fmt_suffix(val)]
        
    log_series = np.log10(series_clean + 1)
    
    # Executa o cálculo de nice numbers na escala logarítmica
    tick_vals_log, _ = calcular_ticks_colorbar(log_series)
    
    tick_text = []
    for v in tick_vals_log:
        if v == 0:
            orig_val = 0
        else:
            orig_val = 10**v
        tick_text.append(fmt_suffix(orig_val))
        
    return tick_vals_log, tick_text

def registrar_callbacks():
    @callback(
        [Output('store-dados-agregados', 'data'), Output('filtro-uf', 'placeholder')],
        [Input("filtro-ano-inicio", "value"), Input("filtro-ano-fim", "value"), 
         Input("filtro-localizacao", "value"), Input("filtro-uf", "value")]
    )
    def processar_motor_dados(ano_inicio, ano_fim, localizacao, ufs):
        placeholder_uf = "Todos (digite para filtrar)..."
        if ufs and len(ufs) > 0:
            placeholder_uf = f"{len(ufs)} selecionados 🔍"

        if df_base.empty: return None, placeholder_uf

        ano_i = ano_inicio if ano_inicio is not None else MIN_ANO
        ano_f = ano_fim if ano_fim is not None else MAX_ANO
        mask = (df_base['ano'] >= ano_i) & (df_base['ano'] <= ano_f)
        
        if localizacao:
            locs_selecionadas = [str(loc).upper() for loc in localizacao]
            mask &= df_base['localizacao'].astype(str).str.upper().isin(locs_selecionadas)
        else: return None, placeholder_uf
            
        if ufs and isinstance(ufs, list) and len(ufs) > 0:
            mask &= df_base['unidade_da_federacao'].isin(ufs)
            
        df_filtrado = df_base[mask]
        if df_filtrado.empty: return None, placeholder_uf

        df_linha = df_filtrado.groupby(['ano', 'mes_num', 'localizacao'], as_index=False)['producao'].sum()
        df_linha = df_linha.sort_values(['ano', 'mes_num'])
        df_linha['data'] = df_linha['ano'].astype(str) + "-" + df_linha['mes_num'].astype(str).str.zfill(2)
        
        df_mapa = df_filtrado.groupby('unidade_da_federacao', as_index=False)['producao'].sum()
        df_rosca = df_filtrado.groupby('localizacao', as_index=False)['producao'].sum()
        
        dados_dict = {
            "linha": df_linha[['data', 'localizacao', 'producao']].to_dict('records'), 
            "mapa": df_mapa.to_dict('records'), 
            "rosca": df_rosca.to_dict('records'),
            "filtros_aplicados": {"ano_i": ano_i, "ano_f": ano_f} 
        }
        return dados_dict, placeholder_uf

    @callback(
        [Output("grafico-serie-temporal", "figure"), Output("grafico-mapa-br", "figure"), Output("grafico-rosca", "figure"), Output("grafico-barras-top3", "figure")],
        Input('store-dados-agregados', 'data'), prevent_initial_call=False
    )
    def renderizar_graficos(dados):
        if not dados: return empty_figure("Sem Dados"), empty_figure("Sem Dados"), empty_figure("Sem Dados"), empty_figure("Sem Dados")
            
        df_linha = pd.DataFrame(dados['linha'])
        df_mapa = pd.DataFrame(dados['mapa'])
        df_rosca = pd.DataFrame(dados['rosca'])
        
        filtros = dados.get('filtros_aplicados', {"ano_i": MIN_ANO, "ano_f": MAX_ANO})
        texto_periodo = f"({filtros['ano_i']} - {filtros['ano_f']})"
        font_color_main = "#E0E0E0" # Baseado na CSS Premium
        hover_bg = "#141216"
        hover_border = "#2B1B35"
        
        # 1. LINHA
        tick_vals_linha, tick_text_linha = calcular_ticks_colorbar(df_linha['producao'])
        fig_linha = px.line(
            df_linha, x='data', y='producao', color='localizacao',
            title=f'<b>Evolução Temporal da Produção {texto_periodo}</b>',
            labels={'producao': 'Volume Produzido (m³)', 'data': "Valor temporal", 'localizacao': 'Localização: '},
            template='plotly_dark', color_discrete_map=CORES_LOCALIZACAO
        )
        fig_linha.update_layout(
            separators=",.", hovermode="x unified",
            hoverlabel=dict(bgcolor=hover_bg, bordercolor=hover_border, font_size=14, font_family="Segoe UI", font_color=font_color_main),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#141216", font=dict(color=font_color_main),
            title=dict(font=dict(size=14, color=font_color_main)),
            yaxis=dict(title="Volume Mensal (m³)", showgrid=True, gridcolor="#F5F7FA", zeroline=False, hoverformat="%B de %Y", tickvals=tick_vals_linha, ticktext=tick_text_linha),
            xaxis=dict(showspikes=True, spikethickness=1, spikedash="dot", spikemode="across", showgrid=False),
            xaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=0.97, xanchor="right", x=0.97), margin=dict(l=10, r=10, t=50, b=10)
        )
        fig_linha.update_traces(line=dict(width=3), hovertemplate="%{fullData.name}: %{y:,.2f} m³<extra></extra>")

        # 2. MAPA CHOROPLETH_MAP (Darkmatter) com normalização logarítmica
        if geojson_brasil and not df_mapa.empty:
            df_mapa['unidade_da_federacao'] = df_mapa['unidade_da_federacao'].str.title().str.replace(" De ", " de ").str.replace(" Do ", " do ")
            todos_estados = [feature['properties']['name'] for feature in geojson_brasil.get('features', [])]
            if todos_estados:
                df_todos_estados = pd.DataFrame({'unidade_da_federacao': todos_estados})
                df_mapa = pd.merge(df_todos_estados, df_mapa, on='unidade_da_federacao', how='left').fillna(0)
            df_mapa['producao_hover'] = df_mapa['producao'].apply(fmt_br)
            df_mapa['producao_log'] = np.log10(df_mapa['producao'] + 1)
            
            fig_mapa = px.choropleth_map(
                df_mapa, geojson=geojson_brasil, locations='unidade_da_federacao',
                featureidkey="properties.name", color='producao_log', custom_data=['producao_hover'],
                hover_name='unidade_da_federacao',
                title=f'<b>Distribuição Espacial da Produção {texto_periodo}</b>',
                color_continuous_scale=[[0.0, "#2B1B35"], [0.33, "#583345"], [0.66, "#C46350"], [1.0, "#F9D6BA"]],
                map_style="carto-darkmatter", zoom=3.0, center={"lat": -14.2, "lon": -51.9},
                opacity=0.85
            )
            fig_mapa.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>Volume: %{customdata[0]} m³<extra></extra>",
                marker_line_width=0.8, marker_line_color="#583345"
            )
            
            tick_vals_mapa, tick_text_mapa = calcular_ticks_log_nice(df_mapa["producao"])
            fig_mapa.update_layout(
                separators=",.", margin=dict(r=0, t=55, l=0, b=0), font=dict(color=font_color_main),
                title=dict(font=dict(size=14, color=font_color_main)),
                hoverlabel=dict(bgcolor=hover_bg, bordercolor=hover_border, font_size=14, font_family="Segoe UI", font_color=font_color_main),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_colorbar=dict(
                    title={"text": "Volume (m³)", "font": {"size": 11, "color": font_color_main}},
                    thickness=12,
                    len=0.75, 
                    tickvals=tick_vals_mapa,
                    ticktext=tick_text_mapa,
                    tickfont={"size": 10, "color": font_color_main}
                )
            )
        else:
            fig_mapa = empty_figure("GeoJSON ou Dados Indisponíveis")

        # 3. ROSCA com porcentagens outside e domain reduzido para evitar cortes/sobreposições
        fig_rosca = px.pie(
            df_rosca, values='producao', names='localizacao', hole=0.55,
            title=f'<b>Ambiente: Terra vs Mar</b><br><span style="font-size: 12px; color: #8C8C8C;">{texto_periodo}</span>',
            template='plotly_dark', color='localizacao', color_discrete_map=CORES_LOCALIZACAO
        )
        fig_rosca.update_traces(
            textposition='outside', textinfo='percent', marker=dict(line=dict(color='#2B1B35', width=1.5)),
            domain=dict(x=[0.15, 0.85], y=[0.1, 0.8]),
            hovertemplate="<b>Ambiente:</b> %{label}<br><b>Volume Acumulado:</b> %{value:,.2f} m³<extra></extra>"
        )
        fig_rosca.update_layout(
            separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color_main),
            title=dict(font=dict(size=13, color=font_color_main)),
            hoverlabel=dict(bgcolor=hover_bg, bordercolor=hover_border, font_size=11, font_family="Segoe UI", font_color=font_color_main),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=15, r=15, t=65, b=15)
        )
        
        # 4. BARRAS VERTICAIS (TOP 3 ESTADOS)
        df_top3 = pd.DataFrame()
        if not df_mapa.empty:
            df_top3 = df_mapa[df_mapa['producao'] > 0].nlargest(3, 'producao').copy()
            df_top3['unidade_da_federacao'] = df_top3['unidade_da_federacao'].str.title().str.replace(" De ", " de ").str.replace(" Do ", " do ")
            df_top3['producao_hover'] = df_top3['producao'].apply(fmt_br)
            
        qtd = len(df_top3)
        if qtd >= 3:
            titulo_barras = f"<b>Top 3 Estados Produtores {texto_periodo}</b>"
        elif qtd > 1:
            titulo_barras = f"<b>Ranking: {qtd} Estados Produtores {texto_periodo}</b>"
        elif qtd == 1:
            titulo_barras = f"<b>Produção do Estado Selecionado {texto_periodo}</b>"
        else:
            titulo_barras = f"<b>Nenhum Estado Produtor {texto_periodo}</b>"
            # titulo_barras = f"<b>Nenhum Estado Produtor</b><br><span style='font-size: 11px; color: #8C8C8C;'>{texto_periodo}</span>"

        if not df_top3.empty:
            fig_barras = px.bar(
                df_top3, x='unidade_da_federacao', y='producao',
                color='producao',
                color_continuous_scale=[[0.0, "#583345"], [0.5, "#C46350"], [1.0, "#F9D6BA"]],
                title=titulo_barras,
                labels={'producao': 'Volume (m³)', 'unidade_da_federacao': 'Estado'},
                text='producao_hover',
                template='plotly_dark'
            )
            fig_barras.update_traces(
                textposition='outside',
                hovertemplate="<b>Estado:</b> %{x}<br><b>Volume Acumulado:</b> %{text} m³<extra></extra>"
            )
            tick_vals_bar, tick_text_bar = calcular_ticks_colorbar(df_top3['producao'])
            fig_barras.update_layout(
                separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color_main),
                title=dict(font=dict(size=13, color=font_color_main)),
                hoverlabel=dict(bgcolor=hover_bg, bordercolor=hover_border, font_size=11, font_family="Segoe UI", font_color=font_color_main),
                xaxis={'categoryorder': 'total descending', 'title': '', 'tickangle': -30},
                yaxis=dict(
                    showgrid=True, gridcolor='#2B1B35', title='',
                    tickvals=tick_vals_bar, ticktext=tick_text_bar
                ),
                coloraxis_showscale=False,
                margin=dict(l=15, r=15, t=65, b=15)
            )
        else:
            fig_barras = empty_figure("Sem Dados")
            
        return fig_linha, fig_mapa, fig_rosca, fig_barras

"""
3_👨🏽_players
----------
Página de drill-down (detalhamento) do atleta.
Usa hierarquia de seletores em cascata (Ano -> Clube -> Jogador) e renderiza KPIs com st.metric.
"""

import streamlit as st
import pandas as pd
import requests
import base64

st.set_page_config(page_title="Players", page_icon="👨🏽", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "JOGADORES 👨🏽"; margin-left: 20px; margin-top: 20px; font-size: 24px;
            font-weight: bold; display: block; margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True,
)

# Funções de Carga (Mesma arquitetura resiliente do teams.py)
@st.cache_data
def load_data(year):
    year_str = str(year)[-2:]
    df_data = pd.read_csv(f"datasets/CLEAN_FIFA{year_str}_official_data.csv", index_col=0)
    df_data = df_data[df_data["Value(£)"] > 0].sort_values(by="Overall", ascending=False)
    return df_data

@st.cache_data
def load_image_64(url):
    if not isinstance(url, str) or not url.startswith("http"): return ""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            return "data:image/png;base64," + base64.b64encode(response.content).decode()
    except Exception:
        pass
    return None

# ==========================================
# SINCRONIZAÇÃO DE ESTADO
# ==========================================
anos_disponiveis = [2023, 2022, 2021, 2020, 2019, 2018, 2017]
ano_padrao = st.session_state.get("ano", 2023)
index_padrao = anos_disponiveis.index(ano_padrao)

ano_selecionado = st.sidebar.selectbox("Selecione o Ano do FIFA", anos_disponiveis, index=index_padrao)

if "ano" not in st.session_state or st.session_state["ano"] != ano_selecionado:
    st.session_state["ano"] = ano_selecionado
    st.session_state["data"] = load_data(ano_selecionado)

df_data = st.session_state["data"]

# ==========================================
# FILTROS EM CASCATA (Cascade Dropdowns)
# ==========================================
# 1º Nível: Clube
clubes = df_data["Club"].unique()
club = st.sidebar.selectbox("Clube", clubes)

# 2º Nível: Jogadores filtrados EXCLUSIVAMENTE pelo Clube selecionado acima
df_players = df_data[(df_data["Club"] == club)]
players = df_players["Name"].unique()
player = st.sidebar.selectbox("Jogador", players)

# ==========================================
# RENDERIZAÇÃO DO PERFIL (UI)
# ==========================================
# .iloc[0] transforma o DataFrame filtrado de 1 linha em uma Pandas Series (facilita o acesso aos valores)
player_stats = df_data[df_data["Name"] == player].iloc[0]

# Renderização resiliente da foto
foto_jogador = load_image_64(player_stats["Photo"])
if foto_jogador:
    st.image(foto_jogador)
else:
    st.markdown("📷 *Foto do jogador indisponível.*")
    
st.title(player_stats["Name"])
st.markdown(f"**Clube:** {player_stats['Club']}")
st.markdown(f"**Posição:** {player_stats['Position']}")

# Uso de st.columns para criar um grid horizontal de informações, aproveitando o layout "wide"
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"**Idade:** {player_stats['Age']}")
col2.markdown(f"**Altura:** {player_stats['Height(cm.)'] / 100:.2f} m")
col3.markdown(f"**Peso:** {player_stats['Weight(lbs.)'] * 0.453:.2f} kg") # Conversão de Libras para KG

st.divider()

# Barra de progresso visual para o Rating
st.subheader(f"Overall {player_stats['Overall']}")
st.progress(int(player_stats["Overall"]))

# Componente 'metric' é excelente analiticamente pois destaca KPIs e aceita formatações numéricas complexas
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Valor de mercado", value=f"£ {player_stats['Value(£)']:,}")
col2.metric(label="Remuneração semanal", value=f"£ {player_stats['Wage(£)']:,}")
col3.metric(label="Cláusula de rescisão", value=f"£ {player_stats['Release Clause(£)']:,}")
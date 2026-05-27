import streamlit as st
import pandas as pd
import requests
import base64

st.set_page_config(
    page_title="Players",
    page_icon="👨🏽",
    layout="wide"
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "JOGADORES 👨🏽";
            margin-left: 20px;
            margin-top: 20px;
            font-size: 24px;
            font-weight: bold;
            display: block;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data(year):
    year_str = str(year)[-2:]
    caminho_arquivo = f"datasets/CLEAN_FIFA{year_str}_official_data.csv"
    df_data = pd.read_csv(caminho_arquivo, index_col=0)
    # df_data = df_data[df_data["Contract Valid Until"] >= year]
    df_data = df_data[df_data["Value(£)"] > 0]
    df_data = df_data.sort_values(by="Overall", ascending=False)
    return df_data

@st.cache_data
def load_image_64(url):
    if not isinstance(url, str) or not url.startswith("http"):
        return ""
    
    try:
        # Correção do Mozilla e adição de um cabeçalho mais completo
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # Adicionado um timeout de 3 segundos para o app não ficar travado esperando links mortos
        response = requests.get(url, headers=headers, timeout=3)
        
        # Só converte se o servidor responder que a imagem existe (Status 200)
        if response.status_code == 200:
            return "data:image/png;base64," + base64.b64encode(response.content).decode()
    except Exception:
        # Se houver erro de conexão, timeout ou link inexistente, ignora e continua
        pass
        
    return None # Retorna vazio para o Streamlit exibir uma célula limpa ou ícone de erro padrão

# --- LÓGICA DE FILTRO DE ANO ---
anos_disponiveis = [2023, 2022, 2021, 2020, 2019, 2018, 2017]
ano_padrao = st.session_state.get("ano", 2023)
index_padrao = anos_disponiveis.index(ano_padrao)

ano_selecionado = st.sidebar.selectbox("Selecione o Ano do FIFA", anos_disponiveis, index=index_padrao)

if "ano" not in st.session_state or st.session_state["ano"] != ano_selecionado:
    st.session_state["ano"] = ano_selecionado
    st.session_state["data"] = load_data(ano_selecionado)

df_data = st.session_state["data"]
# -------------------------------

clubes = df_data["Club"].unique()
club = st.sidebar.selectbox("Clube", clubes)

df_players = df_data[(df_data["Club"] == club)]
players = df_players["Name"].unique()
player = st.sidebar.selectbox("Jogador", players)

# player_stats = df_data[df_data["Name"] == player].iloc[0]
# st.image(load_image_64(player_stats["Photo"]))
# st.title(player_stats["Name"])

player_stats = df_data[df_data["Name"] == player].iloc[0]
foto_jogador = load_image_64(player_stats["Photo"])
# Só renderiza se a foto for baixada com sucesso
if foto_jogador:
    st.image(foto_jogador)
else:
    st.markdown("📷 *Foto do jogador indisponível.*")
st.title(player_stats["Name"])

st.markdown(f"**Clube:** {player_stats['Club']}")
st.markdown(f"**Posição:** {player_stats['Position']}")

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"**Idade:** {player_stats['Age']}")
col2.markdown(f"**Altura:** {player_stats['Height(cm.)'] / 100:.2f} m")
col3.markdown(f"**Peso:** {player_stats['Weight(lbs.)'] * 0.453:.2f} kg")
st.divider()

st.subheader(f"Overall {player_stats['Overall']}")
st.progress(int(player_stats["Overall"]))

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Valor de mercado", value=f"£ {player_stats['Value(£)']:,}")
col2.metric(label="Remuneração semanal", value=f"£ {player_stats['Wage(£)']:,}")
col3.metric(label="Cláusula de rescisão", value=f"£ {player_stats['Release Clause(£)']:,}")
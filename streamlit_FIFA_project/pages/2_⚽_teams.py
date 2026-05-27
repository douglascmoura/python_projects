import streamlit as st
import pandas as pd
import requests
import base64

st.set_page_config(
    page_title="Teams",
    page_icon="⚽",
    layout="wide"
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "CLUBES ⚽";
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

def preprocess_row(url):
    if isinstance(url, str) and url.startswith("http"):
        return load_image_64(url)
    return url

# --- LÓGICA DE FILTRO DE ANO ---
anos_disponiveis = [2023, 2022, 2021, 2020, 2019, 2018, 2017]
ano_padrao = st.session_state.get("ano", 2023)
index_padrao = anos_disponiveis.index(ano_padrao)

ano_selecionado = st.sidebar.selectbox("Selecione o Ano do FIFA", anos_disponiveis, index=index_padrao)

# Se o ano mudar nesta página, atualiza o session_state
if "ano" not in st.session_state or st.session_state["ano"] != ano_selecionado:
    st.session_state["ano"] = ano_selecionado
    st.session_state["data"] = load_data(ano_selecionado)

df_data = st.session_state["data"]
# -------------------------------

clubes = df_data["Club"].unique()
club = st.sidebar.selectbox("Clube", clubes)

df_filtered = df_data[(df_data["Club"] == club)].set_index("Name")
df_filtered["Photo"] = df_filtered["Photo"].apply(preprocess_row)
df_filtered["Flag"] = df_filtered["Flag"].apply(preprocess_row)
df_filtered["Club Logo"] = df_filtered["Club Logo"].apply(preprocess_row)

logo_clube = df_filtered.iloc[0]["Club Logo"]

# st.image(df_filtered.iloc[0]["Club Logo"])
# st.markdown(f"## {club}")

# Só tenta renderizar a imagem se ela existir (não for None)
if logo_clube:
    st.image(logo_clube)
else:
    st.markdown("📷 *Logo indisponível para este ano.*")
st.markdown(f"## {club}")

columns = ["Age", "Photo", "Flag", "Overall", 'Value(£)', 'Wage(£)', 'Joined', 
           'Height(cm.)', 'Weight(lbs.)', 'Contract Valid Until', 'Release Clause(£)']

st.dataframe(df_filtered[columns],
             column_config={
                 "Overall": st.column_config.ProgressColumn(
                     "Overall", format="%d", min_value=0, max_value=100
                 ),
                 "Wage(£)": st.column_config.ProgressColumn("Weekly Wage", format="£%f", 
                                                    min_value=0, max_value=df_filtered["Wage(£)"].max()),
                "Photo": st.column_config.ImageColumn(),
                "Flag": st.column_config.ImageColumn("Country"),
             })
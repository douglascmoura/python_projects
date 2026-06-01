"""
2_⚽_teams
--------
Página dedicada à visualização do plantel de clubes específicos.
Renderiza tabelas ricas (DataFrames customizados) contendo imagens em base64 e barras de progresso.
"""

import streamlit as st
import pandas as pd
import requests
import base64

st.set_page_config(page_title="Teams", page_icon="⚽", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "CLUBES ⚽"; margin-left: 20px; margin-top: 20px; font-size: 24px;
            font-weight: bold; display: block; margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True,
)

# Funções de carga replicadas e em cache (caso o usuário acesse esta página diretamente via URL)
@st.cache_data
def load_data(year):
    year_str = str(year)[-2:]
    df_data = pd.read_csv(f"datasets/CLEAN_FIFA{year_str}_official_data.csv", index_col=0)
    df_data = df_data[df_data["Value(£)"] > 0].sort_values(by="Overall", ascending=False)
    return df_data

@st.cache_data
def load_image_64(url):
    """
    Função de Engenharia de Resiliência:
    Faz o download de imagens da web e converte para base64 para evitar quebras por políticas de segurança 
    do navegador (CORS) ao renderizar imagens dentro de tabelas do Streamlit.
    """
    if not isinstance(url, str) or not url.startswith("http"):
        return ""
    
    try:
        # Mascara o bot do Python como se fosse um navegador real para evitar bloqueios do servidor (HTTP 403 Forbidden)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
        
        # timeout=3 previne que o aplicativo congele eternamente esperando uma imagem de um servidor lento ou fora do ar
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            return "data:image/png;base64," + base64.b64encode(response.content).decode()
    except Exception:
        pass # Silencia o erro para não quebrar a UI
        
    return None

def preprocess_row(url):
    """Função auxiliar para aplicar vetorizadamente no DataFrame."""
    if isinstance(url, str) and url.startswith("http"):
        return load_image_64(url)
    return url

# ==========================================
# LÓGICA DE SINCRONIZAÇÃO DE ESTADO
# ==========================================
anos_disponiveis = [2023, 2022, 2021, 2020, 2019, 2018, 2017]

# Pega o ano da Home (se existir). Caso contrário, assume 2023 como fallback de segurança.
ano_padrao = st.session_state.get("ano", 2023)
index_padrao = anos_disponiveis.index(ano_padrao)

# Seletor sincronizado
ano_selecionado = st.sidebar.selectbox("Selecione o Ano do FIFA", anos_disponiveis, index=index_padrao)

# Mutação de Estado: Se o usuário mudar o ano AQUI, atualizamos a memória global para afetar as outras páginas.
if "ano" not in st.session_state or st.session_state["ano"] != ano_selecionado:
    st.session_state["ano"] = ano_selecionado
    st.session_state["data"] = load_data(ano_selecionado)

df_data = st.session_state["data"]

# ==========================================
# LÓGICA DE FILTRAGEM (Clube)
# ==========================================
clubes = df_data["Club"].unique()
club = st.sidebar.selectbox("Clube", clubes)

# .set_index("Name") remove o ID numérico e coloca o nome do jogador como coluna principal (fixa) na tabela
df_filtered = df_data[(df_data["Club"] == club)].set_index("Name")

# Converte URLs para Imagens Base64
df_filtered["Photo"] = df_filtered["Photo"].apply(preprocess_row)
df_filtered["Flag"] = df_filtered["Flag"].apply(preprocess_row)
df_filtered["Club Logo"] = df_filtered["Club Logo"].apply(preprocess_row)

logo_clube = df_filtered.iloc[0]["Club Logo"]

# Tratamento de UX: Proteção contra logotipos ausentes/quebrados na API
if logo_clube:
    st.image(logo_clube)
else:
    st.markdown("📷 *Logo indisponível para este ano.*")
    
st.markdown(f"## {club}")

# ==========================================
# RENDERIZAÇÃO DA TABELA (DataGrid Avançado)
# ==========================================
columns = ["Age", "Photo", "Flag", "Overall", 'Value(£)', 'Wage(£)', 'Joined', 
           'Height(cm.)', 'Weight(lbs.)', 'Contract Valid Until', 'Release Clause(£)']

# O st.dataframe com column_config permite injetar componentes ricos (Barras, Imagens, Formatações) dentro do grid
st.dataframe(
    df_filtered[columns],
    column_config={
        "Overall": st.column_config.ProgressColumn("Overall", format="%d", min_value=0, max_value=100),
        "Wage(£)": st.column_config.ProgressColumn("Weekly Wage", format="£%f", min_value=0, max_value=df_filtered["Wage(£)"].max()),
        "Photo": st.column_config.ImageColumn(),
        "Flag": st.column_config.ImageColumn("Country"),
    }
)
import streamlit as st
import webbrowser
import pandas as pd

st.set_page_config(
    page_title="Home",
    page_icon="🏡",
    layout="wide"
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "FIFA Analytics 📊🔎"; 
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
# st.sidebar.title("⚽ FIFA Analytics")
# st.sidebar.markdown("Explore os dados de 2017 a 2023!")
# st.sidebar.divider() 

# Função para carregar dados dinamicamente com base no ano
@st.cache_data
def load_data(year):
    # Formata o ano para pegar apenas os dois últimos dígitos (ex: 2023 -> "23")
    year_str = str(year)[-2:]
    caminho_arquivo = f"datasets/CLEAN_FIFA{year_str}_official_data.csv"
    
    df_data = pd.read_csv(caminho_arquivo, index_col=0)
    # Filtra contratos válidos com base no ano selecionado
    df_data = df_data[df_data["Contract Valid Until"] >= year]
    df_data = df_data[df_data["Value(£)"] > 0]
    df_data = df_data.sort_values(by="Overall", ascending=False)
    return df_data

# Filtro de Ano na Barra Lateral
anos_disponiveis = [2023, 2022, 2021, 2020, 2019, 2018, 2017]
ano_selecionado = st.sidebar.selectbox("Selecione o Ano do FIFA", anos_disponiveis)

# Salva o ano e os dados no session_state para compartilhar com as outras páginas
st.session_state["ano"] = ano_selecionado
st.session_state["data"] = load_data(ano_selecionado)


st.markdown("# Explorando o FIFA Official Dataset! ⚽🎮📊")
st.sidebar.markdown("Desenvolvido por [Douglas Chaves Moura](https://www.linkedin.com/in/douglas-chaves-moura-a545a835b) junto à **Asimov Academy**.")

btn = st.button("Acesse os dados no Kaggle")
if btn:
    webbrowser.open_new_tab("https://www.kaggle.com/datasets/kevwesophia/fifa23-official-datasetclean-data")

st.markdown(
    '''
    **Seja bem-vindo** à plataforma onde a paixão pelo futebol se cruza com o poder da Estatística! 🏟️✨

    Este web app foi desenhado para te dar uma visão geral sobre um conjunto de dados de futebol da EA Esports FC. Ele navega por mais de 122 mil registros que cobrem a evolução do futebol mundial entre os anos de 2017 a 2023.
    
    🔍 **O que você pode explorar aqui?**
    Através dos menus laterais, você consegue analisar detalhadamente:

    - 👤 **Perfil e Dados Demográficos**: Quem são, de onde vêm e como se distribuem os atletas profissionalmente.
    - 💪 **Características Físicas e Técnicas**: A relação entre altura, peso, posições em campo e habilidades específicas.
    - 📈 **Métricas de Desempenho e Potencial**: Compara os *ratings* atuais (Overall).
    - 💰 **Economia do Futebol**: Explora os valores de mercado, salários semanais e cláusulas de rescisão milionárias.
    - 🏢 **Análise de Clubes**: Descobre quais as equipes mais valiosas, as mais equilibradas e como os plantéis mudaram ao longo do tempo.
    '''
)
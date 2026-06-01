"""
1_🏡_home
-------
Página inicial do Web App multipage (Streamlit).
Responsável por apresentar o projeto e inicializar o estado global da aplicação (session_state),
carregando os dados base que serão consumidos pelas outras páginas (Teams e Players).
"""

import streamlit as st
import webbrowser
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
# st.set_page_config DEVE ser o primeiro comando Streamlit executado no script.
st.set_page_config(
    page_title="Home",
    page_icon="🏡",
    layout="wide" # Utiliza toda a largura da tela, ideal para dashboards analíticos
)

# 2. INJEÇÃO DE CSS CUSTOMIZADO
# Hack de UI: O Streamlit nativamente não permite mudar o título acima do menu de páginas facilmente.
# Aqui injetamos um pseudo-elemento CSS (::before) na classe do menu lateral para criar um cabeçalho fixo.
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

# 3. CAMADA DE DADOS E CACHE (Performance)
# O decorador @st.cache_data memoriza o DataFrame retornado. Se o usuário selecionar um ano 
# já carregado anteriormente, o Streamlit pula a leitura do CSV e retorna o dado da memória instantaneamente.
@st.cache_data
def load_data(year):
    """Carrega, higieniza e filtra o dataset oficial do FIFA com base no ano selecionado."""
    # Formata o ano para pegar apenas os dois últimos dígitos (ex: 2023 -> "23") para casar com o nome do arquivo
    year_str = str(year)[-2:]
    caminho_arquivo = f"datasets/CLEAN_FIFA{year_str}_official_data.csv"
    
    df_data = pd.read_csv(caminho_arquivo, index_col=0)
    
    # Filtros de negócio: Apenas contratos válidos e jogadores com valor de mercado real
    df_data = df_data[df_data["Contract Valid Until"] >= year]
    df_data = df_data[df_data["Value(£)"] > 0]
    
    # Ordenação prévia para garantir que os melhores jogadores sempre apareçam primeiro nas tabelas
    df_data = df_data.sort_values(by="Overall", ascending=False)
    return df_data

# 4. INTERFACE DO USUÁRIO (Sidebar)
anos_disponiveis = [2023, 2022, 2021, 2020, 2019, 2018, 2017]
ano_selecionado = st.sidebar.selectbox("Selecione o Ano do FIFA", anos_disponiveis)

# 5. GERENCIAMENTO DE ESTADO (State Management)
# Salvamos as variáveis no session_state para que as páginas 'teams.py' e 'players.py' 
# acessem os dados sem precisar ler o CSV ou perguntar o ano novamente.
st.session_state["ano"] = ano_selecionado
st.session_state["data"] = load_data(ano_selecionado)

# 6. CONTEÚDO PRINCIPAL (Apresentação)
st.markdown("# Explorando o FIFA Official Dataset! ⚽🎮📊")
st.sidebar.markdown("Desenvolvido por [Douglas Chaves Moura](https://www.linkedin.com/in/douglas-chaves-moura-a545a835b) junto à **Asimov Academy**.")

# Interação com link externo (Kaggle)
btn = st.button("Acesse os dados no Kaggle")
if btn:
    webbrowser.open_new_tab("https://www.kaggle.com/datasets/kevwesophia/fifa23-official-datasetclean-data")

# Texto descritivo da aplicação
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
<a name="topo"></a>
<h1 align="center">🐍 Python Projects & Data Apps</h1>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Plotly_Dash-008DE4?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly Dash"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Jupyter_Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter Notebook"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="Scikit-Learn"/></a>
  <a href="https://douglas-moura-portfolio.pages.dev"><img src="https://img.shields.io/badge/Portfolio-Douglas_Chaves_Moura-0A1630?style=for-the-badge&logo=googlepubsub&logoColor=white" alt="Portfolio"/></a>
</p>

Este repositório é uma coletânea centralizada e modular dos projetos, aplicações web e scripts desenvolvidos em **Python** por mim, Douglas Chaves Moura (**DOCHMO**). 

O acervo abrange desde a lógica de programação e algoritmos fundamentais em terminal até a construção de dashboards analíticos corporativos de alta densidade (**Plotly / Dash**), web apps interativos multipáginas (**Streamlit**) e pipelines preditivos de **Machine Learning & Data Science**.

---

## 📊 Projetos em Destaque & Categorias

O repositório está organizado em 11 módulos principais divididos por domínio de aplicação:

| Categoria | Projeto / Pasta | Descrição & Recursos | Stack Técnica |
| :--- | :--- | :--- | :--- |
| 🌐 **Data Apps** | **[`dash_analise_itbi_fortaleza_V2`](./dash_analise_itbi_fortaleza_V2)** *(e V1)* | Dashboard analítico geoterritorial sobre arrecadação e transações imobiliárias do ITBI em Fortaleza (ceará). | Python, Dash, Plotly, Bootstrap |
| 🌐 **Data Apps** | **[`dash_producao_petroleo_brasil_V2`](./dash_producao_petroleo_brasil_V2)** *(e V1)* | Painel de Business Intelligence para análise temporal da produção de petróleo e gás natural no Brasil (ANP Upstream). | Python, Dash, Plotly, Pandas |
| 🌐 **Data Apps** | **[`dash_processamento_petroleo_brasil_V2`](./dash_processamento_petroleo_brasil_V2)** *(e V1)* | Dashboard analítico da capacidade de refino e carga de processamento de petróleo nas refinarias nacionais (ANP Downstream). | Python, Dash, Plotly, Pandas |
| 🌐 **Data Apps** | **[`dash_vendas_combustiveis_brasil`](./dash_vendas_combustiveis_brasil)** | Painel interativo de inteligência comercial sobre distribuição e vendas de combustíveis pelos estados brasileiros. | Python, Dash, Plotly, Bootstrap |
| 🌐 **Data Apps** | **[`streamlit_FIFA_project`](./streamlit_FIFA_project)** | Web App analítico multipágina em Streamlit para exploração interativa de métricas, salários e estatísticas de jogadores do FIFA. | Python, Streamlit, Pandas, Matplotlib |
| 🤖 **Machine Learning** | **[`titanic_machine_learning`](./titanic_machine_learning)** | Pipeline completo de Análise Exploratória (EDA), Feature Engineering e modelagem preditiva de sobrevivência no dataset Titanic. | Python, Jupyter, Scikit-Learn, XGBoost |
| 💻 **Lógica & CLI** | **[`calc_project`](./calc_project)** | Calculadora matemática interativa via terminal para operações fundamentais. | Python puro, Lógica Estruturada |
| 💻 **Lógica & CLI** | **[`games_project`](./games_project)** | Algoritmos e jogos clássicos rodando via linha de comando (*Jogo da Velha* e *Pedra, Papel e Tesoura*). | Python puro, Programação Orientada a Objetos |

---

## 📂 Estrutura do Repositório

```text
python_projects/
├── README.md                                 # Documentação principal do repositório
├── calc_project/                             # Calculadora matemática interativa CLI (calculadora.py)
├── games_project/                            # Jogos clássicos em terminal
│   ├── jogo_da_velha.py                      # Algoritmo e lógica do Jogo da Velha
│   └── pedra_papel_tesoura.py                # Algoritmo e lógica de Pedra, Papel e Tesoura
├── streamlit_FIFA_project/                   # Web App multipágina interativo em Streamlit
│   ├── 1_🏡_home.py                         # Página inicial da aplicação FIFA Analytics
│   ├── pages/                                # Páginas adicionais de estatísticas e atletas
│   └── datasets/                             # Bases de dados tratadas do FIFA
├── dash_analise_itbi_fortaleza/              # Dashboard de análise de ITBI em Fortaleza (Versão 1.0)
├── dash_analise_itbi_fortaleza_V2/           # Dashboard geoterritorial de ITBI em Fortaleza (Versão 2.0 com GIF)
├── dash_producao_petroleo_brasil/            # Dashboard de produção de petróleo no Brasil (Versão 1.0)
├── dash_producao_petroleo_brasil_V2/         # Dashboard de produção de petróleo ANP Upstream (Versão 2.0 com GIF)
├── dash_processamento_petroleo_brasil/       # Dashboard de refino de petróleo no Brasil (Versão 1.0)
├── dash_processamento_petroleo_brasil_V2/    # Dashboard de processamento e carga de refino ANP (Versão 2.0 com GIF)
├── dash_vendas_combustiveis_brasil/          # Dashboard comercial de vendas de combustíveis (com GIF)
└── titanic_machine_learning/                 # Notebook de Machine Learning e EDA do Titanic
    ├── analise_titanic_ml.ipynb              # Notebook Jupyter com análises e modelos
    ├── train.csv                             # Base de dados de treino
    └── test.csv                              # Base de dados de teste
```

---

## 🛠️ Tecnologias & Ecossistema Python

O desenvolvimento dos projetos utiliza as principais bibliotecas do ecossistema de Ciência de Dados e Engenharia de Software em Python:

* **Manipulação & Análise de Dados:** `Pandas`, `NumPy`, `PyArrow / Parquet`.
* **Visualização de Dados & Dashboards:** `Plotly`, `Dash`, `Dash Bootstrap Components`, `Streamlit`, `Matplotlib`, `Seaborn`.
* **Machine Learning & Modelagem:** `Scikit-Learn`, `XGBoost`, `Jupyter Notebook`.
* **Interface & Desenvolvimento:** `HTML5/CSS3` (para temas customizados no Dash/Streamlit), `Python 3.10+`.

---

## ✍🏽 Autor

<table align="center">
  <tr>
    <td align="center" width="150px">
      <img src="https://github.com/douglascmoura.png" width="110px;" style="border-radius:50%;" alt="Douglas Moura"/><br />
      <sub><b>Douglas Chaves Moura</b></sub>
    </td>
    <td>
      <p>Estatístico, pesquisador e cientista de dados idealizador do ecossistema <b>DOCHMO</b>. Atua no desenvolvimento de soluções quantitativas avançadas, engenharia de dados em Python, aplicações analíticas interativas (Dashboards/Streamlit) e aprendizado de máquina.</p>
      <p align="left">
        <a href="https://github.com/douglascmoura"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
        <a href="https://www.linkedin.com/in/douglas-chaves-moura/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
        <a href="mailto:douglascmoura21@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>
        <a href="https://douglas-moura-portfolio.pages.dev/"><img src="https://img.shields.io/badge/Website-0A1630?style=for-the-badge&logo=googlepubsub&logoColor=white" alt="Website"/></a>
      </p>
    </td>
  </tr>
</table>

<p align="right"><a href="#topo">🔼 Voltar ao topo</a></p>
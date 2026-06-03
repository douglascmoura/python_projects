# 🛢️ Dashboard Interativo: Processamento Nacional de Petróleo

Este projeto é uma aplicação web analítica *full-stack* desenvolvida em **Python** utilizando o framework **Dash**. O foco da aplicação é monitorar, filtrar e analisar visualmente o volume de processamento de petróleo e a distribuição da matéria-prima nas refinarias do Brasil.

O grande diferencial deste projeto é a sua **Arquitetura Modular**, que separa rigorosamente o layout (Frontend), as regras de negócio/estado (Backend/Callbacks) e a ingestão de dados (Data Management), garantindo alta manutenibilidade e escalabilidade.

---

## 🎯 Funcionalidades e Visualizações

A interface apresenta um design *Dark Mode* elegante (Tema CYBORG do Bootstrap), oferecendo uma experiência analítica imersiva com os seguintes gráficos dinâmicos:
* **Série Temporal (Evolução do Processamento):** Gráfico de linhas focado em *UX Analítica*, equipado com linhas de guia transversais (*Spike Lines*) para facilitar a leitura exata dos volumes ao longo dos meses.
* **Share Regional (Treemap):** Visualização hierárquica em blocos (`px.treemap`) que mapeia a concentração do refino do nível Nacional até a granularidade por Unidade da Federação e Refinaria específica.
* **Mix de Carga (Donut Chart):** Gráfico de rosca evidenciando a proporção de insumos utilizados (Petróleo Nacional vs. Importado vs. Outras Cargas).
* **Filtros de Alta Precisão:** Componentes interativos utilizando a biblioteca `dash_mantine_components` (ex: Inputs Numéricos para os anos e Selects múltiplos com busca para os Estados).

---

## ⚙️ Engenharia de Dados e Performance

A aplicação foi projetada para rodar de forma leve e responsiva, implementando táticas agressivas de otimização de performance:
* **Arquitetura Singleton e Parquet:** Os dados são lidos em formato `.parquet` apenas uma vez no módulo `data_manager.py`. 
* **Otimização de Memória RAM (Categorical Casting):** Colunas textuais de baixa cardinalidade (como estados e matérias-primas) são convertidas para o tipo `category` do Pandas na ingestão, aliviando o peso do *DataFrame* no servidor e acelerando os filtros condicionais.
* **Client-Side Cache:** O componente `dcc.Store` salva os dados já filtrados no navegador do usuário, impedindo que o servidor repita cálculos pesados a cada novo gráfico renderizado.

---

## 📂 Estrutura do Projeto (Arquitetura Modular)

A base de código segue o princípio de Separação de Responsabilidades (SoC):

```text
├── dataset/
│   ├── metadados_processamento_petroleo.pdf      # Dicionário de dados e documentação oficial
│   └── processamento_petroleo_brasil.xlsx        # Base bruta original (Dados da ANP)
├── projeto_downstream_refino/
│   ├── assets/
│   │    └── style.css                            # Estilizações customizadas (Classes e Layout)
│   ├── processamento_petroleo_filtered.parquet   # Base Otimizada de Dados
│   ├── data_manager.py                           # Módulo de Ingestão, Tipagem e Constantes Globais
│   ├── layout.py                                 # Módulo de Frontend (Sidebar, Grid e Componentes)
│   ├── callbacks.py                              # Módulo de Backend (Reatividade e Gráficos Plotly)
│   ├── app.py                                    # Entry-point (Servidor web e Acoplamento)
├── script/
│    └── script_processamento_petroleo.ipynb      # Análise Exploratória de Dados
└── README.md                                     # Este documento
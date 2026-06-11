# 🏙️ Dashboard Interativo: Análise de ITBI (Fortaleza-CE)

Este projeto é uma aplicação web analítica desenvolvida em **Python** utilizando o framework **Dash**. O objetivo é mapear, filtrar e analisar visualmente as transações imobiliárias e a distribuição do Imposto sobre a Transmissão de Bens Imóveis (ITBI) na cidade de Fortaleza-CE.

---

## 🎯 Funcionalidades da Aplicação

O Dashboard oferece uma interface interativa (Dark Mode) que permite ao usuário explorar os dados em tempo real através de:
* **Filtros Dinâmicos:** Controles para Ano de Exercício, Tipo de Uso (Residencial/Comercial), Bairros e Padrão de Construção.
* **Mapa de Transações (Spatial Analytics):** Visualização georreferenciada via Plotly Mapbox, focando no Valor do M² e na Área Edificada.
* **Análise de Dispersão (Boxplot):** Gráficos para entender a variabilidade dos preços por padrão construtivo, com remoção estatística de outliers extremos para melhor legibilidade interquartil.
* **Ranking de Bairros:** Gráfico de barras horizontais destacando o Top 10 bairros com maior valorização média por metro quadrado.

---

## ⚙️ Arquitetura e Otimização de Performance

A aplicação foi projetada com foco em engenharia de software e performance de renderização:
* **State Management (Client-Side Storage):** Utilização do `dcc.Store` para manter os dados filtrados na memória do navegador do usuário, evitando consultas repetitivas ao backend e acelerando a renderização dos gráficos simultâneos.
* **Vetorização com Pandas:** Processamento rápido de máscaras booleanas no motor de filtragem.
* **UI/UX Consistente:** Combinação de `dash_bootstrap_components` (Tema Cyborg) e `dash_mantine_components` para componentes de interface elegantes e responsivos.

---

## 📂 Estrutura do Projeto

O diretório está organizado separando a base bruta, as rotinas de limpeza de dados e a aplicação web:

```text
├── dataset/
│   └── dados_abertos_itbi_transacoes_imobiliarias.xlsx  # Base bruta (Dados Abertos)
│   └── dataset_filtered.xlsx                            # Base higienizada consumida pelo Dashboard
├── projeto_analise_itbi/
│   ├── assets/
│   │     └── style.css                                  # Estilizações customizadas (Classes e Layout)
│   ├── data_manager.py                                  # Módulo de Ingestão, Tipagem e Constantes Globais
│   ├── layout.py                                        # Módulo de Frontend (Sidebar, Grid e Componentes)
│   ├── callbacks.py                                     # Módulo de Backend (Reatividade e Gráficos Plotly)
│   └── app.py                                           # Entry-point (Servidor web e Acoplamento)
├── scripts/
│   ├── analise_exploratoria_itbi.ipynb                  # Notebook de EDA e descobertas iniciais
│   └── script_filter.ipynb                              # ETL: Tratamento e exportação da base limpa
└── README.md                                            # Este documento
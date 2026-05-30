# 🛢️ Dashboard Interativo: Produção Nacional de Petróleo (Brasil)

Este projeto é uma aplicação web analítica desenvolvida em **Python** utilizando o framework **Dash**. O objetivo é fornecer uma interface interativa e de alta performance para a exploração da série histórica e da distribuição geográfica da extração de petróleo no Brasil (Mar vs. Terra).

---

## 🎯 Funcionalidades e Visualizações

A aplicação apresenta uma interface *Light Mode* (Tema LUX do Bootstrap) com paletas de cores quentes e modernas, oferecendo as seguintes visualizações dinâmicas:
* **Evolução Temporal:** Gráfico de linhas (`px.line`) detalhando o volume mensal de produção ao longo dos anos, segmentado por ambiente de extração.
* **Spatial Analytics (Mapa Choropleth):** Mapeamento georreferenciado da produção por Estado utilizando malhas GeoJSON customizadas, permitindo a rápida identificação dos maiores polos produtores.
* **Participação Absoluta (Donut Chart):** Gráfico de rosca evidenciando a proporção exata do volume extraído em operações *Offshore* (Mar) versus *Onshore* (Terra).
* **Filtros Dinâmicos:** Controles interativos por Período (Ano), Localização e Unidade da Federação.

---

## ⚙️ Arquitetura e Engenharia de Performance

Para garantir fluidez e escalabilidade, o projeto implementa técnicas avançadas de otimização:
* **Armazenamento em Parquet:** O backend consome os dados em formato `.parquet` ao invés de `.csv` ou `.xlsx`, reduzindo drasticamente o tempo de I/O (leitura de disco) e o consumo de memória RAM no servidor.
* **State Management (Client-Side Storage):** Utilização do componente `dcc.Store` para manter os dados pré-agregados em cache no navegador do usuário. Isso evita o reprocessamento redundante de dados a cada interação com os gráficos.
* **UI/UX Customizada:** Integração do `dash_bootstrap_components` com `dash_mantine_components`, além de estilização CSS nativa via pasta `/assets` para tipografia e responsividade.

---

## 📂 Estrutura do Projeto

O diretório está organizado separando os arquivos estáticos, as rotinas de tratamento (ETL) e os dados de alta performance:

```text
├── assets/
│   └── style.css                             # Estilizações customizadas (Classes e Layout)
├── dataset/
│   ├── metadados_producao_petroleo.pdf       # Dicionário de dados e documentação oficial
│   └── producao_petroleo.xlsx                # Base bruta original (Dados da ANP)
├── script/
│   ├── brazil_states.json                    # Malha espacial (GeoJSON) dos estados brasileiros
│   └── script_producao_petroleo.ipynb        # Notebook de ETL (Limpeza e exportação para Parquet)
├── producao_petroleo_filtered.parquet        # Base de dados otimizada e vetorizada para o App
├── app.py                                    # Script principal (Servidor web e Callbacks)
└── README.md                                 # Este documento
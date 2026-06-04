# ⛽ Dashboard Interativo: Vendas Históricas de Combustíveis no Brasil

Este projeto é uma aplicação web analítica desenvolvida em **Python** utilizando o framework **Dash**. O objetivo é monitorar, filtrar e analisar visualmente a evolução e a concentração regional das vendas de derivados de petróleo e etanol no Brasil entre os anos de 1990 e 2025.

O projeto adota uma **Arquitetura Modular** rigorosa que separa o layout (Frontend), a reatividade e geração gráfica (Backend/Callbacks) e a ingestão de dados (Data Management), garantindo alto desempenho, fácil manutenibilidade e escalabilidade.

---

## 🎯 Funcionalidades e Visualizações

A interface apresenta um design *Dark Mode* elegante com uma identidade visual inspirada nos tons *Pedra & Terra* (utilizando carvão profundo `#0C151A` e marrom terracota `#724C39`), oferecendo uma experiência analítica imersiva com as seguintes visualizações:
* **Evolução Temporal (Gráfico de Linha):** Série temporal que monitora a evolução das vendas de combustíveis, equipada com cursor de hover unificado no eixo X e linhas de mira transversais transparentes adaptadas ao fundo escuro.
* **Distribuição Territorial (Mapa Cloroplético):** Mapeamento georreferenciado interativo via Plotly Mapbox integrado com limites estaduais (GeoJSON local) e preenchimento de gradientes de venda de alta legibilidade.
* **Concentração Setorial (Treemap Hierárquico):** Visualização em blocos que revela a partilha e participação das vendas desde a escala Nacional, passando por Grandes Regiões até o nível de cada Unidade da Federação (UF).

---

## ⚙️ Engenharia de Dados e Performance

A aplicação foi projetada focando em eficiência operacional e renderização responsiva:
* **Ingestão Otimizada com Parquet:** Carga inicial dos dados no formato `.parquet` otimizado no módulo `data_manager.py`, reduzindo drasticamente o consumo de memória RAM do servidor.
* **Client-Side Cache (`dcc.Store`):** Compartilhamento de dados filtrados salvos na memória do navegador do usuário. O backend processa os filtros uma única vez e todos os gráficos consomem o cache, eliminando concorrência de requisições repetidas.
* **Controles Focados em Foco Terracota:** Substituição global do tom de destaque azul padrão do Mantine via injeção de tema (`MantineProvider`) e sobrescrita de atributos de foco por teclado (`[data-combobox-active]`, `[data-hovered]`) em marrom terracota.

---

## 📂 Estrutura do Projeto (Arquitetura Modular)

O projeto segue estritamente o princípio de Separação de Responsabilidades (SoC), organizado da seguinte forma:

```text
├── dataset/
│   ├── metadados_vendas_derivados_petroleo_etanol.pdf  # Dicionário de dados e documentação oficial
│   └── vendas_combustiveis_brasil.xlsx                 # Base bruta original (Dados da ANP)
├── projeto_downstream_comercializacao/
│   ├── assets/
│   │    ├── brazil_states.geojson                      # Coordenadas geográficas das UFs para renderização do mapa
│   │    └── style.css                                  # Estilizações customizadas e design do checklist Mantine
│   ├── app.py                                          # Script de inicialização (Entry-point do servidor e tema)
│   ├── callbacks.py                                    # Módulo de backend (Lógica de filtragem, cálculos e gráficos Plotly)
│   ├── data_manager.py                                 # Módulo de ingestão de dados, tipagem e constantes
│   ├── layout.py                                       # Módulo de frontend (Sidebar, Grid, Componentes e Inputs)
│   ├── vendas_combustiveis_filtered.parquet            # Base otimizada
├── script/
│   └── script_vendas_combustiveis_brasil.ipynb         # Notebook de ETL (Limpeza e exportação para Parquet)
│            
└── README.md                                           # Este documento

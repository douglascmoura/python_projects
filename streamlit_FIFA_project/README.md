# ⚽ FIFA Analytics 📊🔎

**Seja bem-vindo** à plataforma onde a paixão pelo futebol se cruza com o poder da Estatística! 🏟️✨

Este web app foi desenhado para te dar uma visão geral sobre um conjunto de dados de futebol da EA Esports FC. Ele navega por mais de 122 mil registros que cobrem a evolução do futebol mundial entre os anos de 2017 a 2023.

---

## 🔍 O que você pode explorar aqui?

Através dos menus laterais, você consegue analisar detalhadamente:

- 👤 **Perfil e Dados Demográficos**: Quem são, de onde vêm e como se distribuem os atletas profissionalmente.
- 💪 **Características Físicas e Técnicas**: A relação entre altura, peso, posições em campo e habilidades específicas.
- 📈 **Métricas de Desempenho e Potencial**: Compara os *ratings* atuais (Overall).
- 💰 **Economia do Futebol**: Explora os valores de mercado, salários semanais e cláusulas de rescisão milionárias.
- 🏢 **Análise de Clubes**: Descobre quais as equipes mais valiosas, as mais equilibradas e como os plantéis mudaram ao longo do tempo.

---

## 📂 Estrutura do Projeto

Abaixo, um resumo de como os arquivos e as páginas do dashboard estão organizados:

```text
├── datasets/
│   └── CLEAN_FIFA...csv                # Bases de dados oficiais tratadas (2017 a 2023)
├── pages/
│   ├── 2_⚽_teams.py                  # Página de análise focada nos Clubes
│   └── 3_👨🏽_players.py                # Página de análise focada nos Jogadores
├── 1_🏡_home.py                       # Script principal (Home e carregamento de dados)
└── README.md                           # Este documento
```
"""
app.py
------
Ponto de entrada principal da aplicação Dash.
Sua única responsabilidade é inicializar o servidor, acoplar o layout
e registrar os callbacks. Mantemos este arquivo limpo para facilitar
o deploy e a escalabilidade (separação de responsabilidades).

Para executar:
    python app.py

Acesse em: http://localhost:8050
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from layout import criar_layout
from callbacks import registrar_callbacks

# =========================================================================
# 1. INICIALIZAÇÃO DA APLICAÇÃO
# =========================================================================
# Bootstrap CYBORG como base global de reset CSS e grid responsivo.
# O tema escuro do Cyborg garante compatibilidade com nosso CSS customizado.
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="DOCHMO — Vendas de Combustíveis no Brasil",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": (
            "Dashboard interativo da série histórica de vendas de combustíveis "
            "no Brasil (1990–2025). Dados da ANP — Agência Nacional do Petróleo."
        )},
    ],
)

# Exposição de 'server' para deploys em nuvem (Gunicorn, Render, Heroku)
server = app.server

# =========================================================================
# 2. ACOPLAMENTO DO FRONTEND (LAYOUT)
# =========================================================================
# dmc.MantineProvider força o modo escuro e aplica a paleta customizada
# terracota para todos os componentes Mantine (evitando a cor azul padrão).
custom_theme = {
    "colors": {
        "terracota": [
            "#f8f2ee",  # 0
            "#ebe0d8",  # 1
            "#decdbf",  # 2
            "#d0b8a7",  # 3
            "#c1a18c",  # 4
            "#ad8973",  # 5
            "#936a54",  # 6
            "#724c39",  # 7 (primary)
            "#5f3d2c",  # 8
            "#4b2f21",  # 9
        ]
    },
    "primaryColor": "terracota",
}

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme=custom_theme,
    children=criar_layout(),
)

# =========================================================================
# 3. ACOPLAMENTO DO BACKEND (LÓGICA REATIVA)
# =========================================================================
registrar_callbacks()

# =========================================================================
# 4. EXECUÇÃO DO SERVIDOR LOCAL
# =========================================================================
if __name__ == "__main__":
    # debug=True ativa Hot-Reloading e mostra erros diretamente no navegador.
    # Desative em produção (debug=False).
    app.run(debug=True, port=8051)

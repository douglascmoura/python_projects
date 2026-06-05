"""
app.py
------
Ponto de entrada principal da aplicação Dash para Análise de ITBI Fortaleza.
Arquitetura Modular MVC + Tema Premium.
"""

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from layout import criar_layout
from callbacks import registrar_callbacks

# 1. INICIALIZAÇÃO DA APLICAÇÃO
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="DOCHMO - Análise ITBI",
    external_scripts=["https://cdn.plot.ly/plotly-locale-pt-br-latest.js"],
    suppress_callback_exceptions=True
)

server = app.server

# Tema Customizado Mantine para Teal/Ciano
custom_theme = {
    "colors": {
        "dochmo_teal": ["#e3f6f8", "#c6edf0", "#a9e3e9", "#8cdbe1", "#6fd2d9", "#52c9d2", "#2bbaca", "#2295a2", "#1a707a", "#114a51"]
    },
    "primaryColor": "dochmo_teal",
}

# 2. ACOPLAMENTO DO FRONTEND (LAYOUT)
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme=custom_theme,
    children=criar_layout()
)

# 3. ACOPLAMENTO DO BACKEND (LÓGICA REATIVA)
registrar_callbacks()

# 4. EXECUÇÃO DO SERVIDOR LOCAL
if __name__ == "__main__":
    app.run(debug=True, port=8050)

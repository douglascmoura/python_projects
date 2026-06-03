"""
app.py
------
Ponto de entrada principal da aplicação Dash para Produção de Petróleo.
"""

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from layout import criar_layout
from callbacks import registrar_callbacks

# 1. INICIALIZAÇÃO DA APLICAÇÃO
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    title="DOCHMO - Produção Nacional de Petróleo",
    external_scripts=["https://cdn.plot.ly/plotly-locale-pt-br-latest.js"],
    suppress_callback_exceptions=True
)

server = app.server

# 2. ACOPLAMENTO DO FRONTEND (LAYOUT)
# O dmc.MantineProvider garante estilos dark para MultiSelect e NumberInput
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    children=criar_layout()
)

# 3. ACOPLAMENTO DO BACKEND (LÓGICA REATIVA)
registrar_callbacks()

# 4. EXECUÇÃO DO SERVIDOR LOCAL
if __name__ == "__main__":
    app.run(debug=True, port=8050)

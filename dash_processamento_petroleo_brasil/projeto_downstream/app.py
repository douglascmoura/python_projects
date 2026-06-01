"""
app.py
------
Ponto de entrada principal da aplicação Dash.
Sua única responsabilidade é inicializar o servidor, acoplar o layout e registrar os callbacks.
Mantemos este arquivo limpo para facilitar o deploy e a escalabilidade (separação de responsabilidades).
"""

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from layout import criar_layout
from callbacks import registrar_callbacks

# 1. INICIALIZAÇÃO DA APLICAÇÃO
# Utilizamos o tema CYBORG do Bootstrap nativo como base global de reset CSS e tipografia.
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.CYBORG],
    title="DOCHMO - Processamento Nacional de Petróleo"    
)

# Exposição da variável 'server' necessária para deploys em nuvem (ex: Gunicorn, Render, Heroku)
server = app.server

# 2. ACOPLAMENTO DO FRONTEND (LAYOUT)
# O dmc.MantineProvider "abraça" a aplicação para garantir que os componentes interativos avançados 
# (como NumberInput e MultiSelect) apliquem corretamente seus estilos e scripts do modo escuro.
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    children=criar_layout()
)

# 3. ACOPLAMENTO DO BACKEND (LÓGICA REATIVA)
# Chamamos a função que ativa os "ouvintes" (callbacks) de eventos do painel.
registrar_callbacks()

# 4. EXECUÇÃO DO SERVIDOR LOCAL
if __name__ == "__main__":
    # debug=True ativa o Hot-Reloading (atualiza a página sozinho ao salvar o código) 
    # e mostra os erros diretamente no navegador.
    app.run(debug=True, port=8050)
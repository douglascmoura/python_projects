"""
data_manager.py
---------------
Responsável por carregar, armazenar e disponibilizar os dados globais da aplicação.
"""
import pandas as pd
import json
from pathlib import Path

def carregar_dados():
    caminho_base = Path(__file__).resolve().parent
    
    # Produção
    parquet_path = caminho_base / "dataset" / "producao_petroleo_filtered.parquet"
    if parquet_path.exists():
        df_base = pd.read_parquet(parquet_path)
    else:
        df_base = pd.DataFrame()
        print(f"[ERRO] Dataset não encontrado em {parquet_path}")

    # GeoJSON
    geojson_path = caminho_base / "dataset" / "brazil_states.json"
    geojson_brasil = {}
    if geojson_path.exists():
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                geojson_brasil = json.load(f)
        except Exception:
            with open(geojson_path, "r", encoding="latin-1") as f:
                geojson_brasil = json.load(f)
    else:
        print(f"[ERRO] GeoJSON não encontrado em {geojson_path}")
        
    return df_base, geojson_brasil

# Executado uma única vez ao iniciar o servidor
df_base, geojson_brasil = carregar_dados()

# Extração de domínios para os filtros (Sidebar)
if not df_base.empty:
    ANOS_DISPONIVEIS = sorted(df_base['ano'].unique())
    MIN_ANO = int(min(ANOS_DISPONIVEIS))
    MAX_ANO = 2025 # Limite final definido pelo usuário
    UFS_DISPONIVEIS = sorted(df_base['unidade_da_federacao'].unique())
else:
    MIN_ANO, MAX_ANO = 1997, 2025
    UFS_DISPONIVEIS = []

# Paleta de Cores de Dados - Tema Premium Dark Sunset
CORES_LOCALIZACAO = {
    "MAR": "#C46350",   # Neon Laranja/Sunset
    "TERRA": "#F9D6BA", # Neon Amarelo/Rosa Claro
    "Mar": "#C46350",
    "Terra": "#F9D6BA",
    "mar": "#C46350",
    "terra": "#F9D6BA"
}

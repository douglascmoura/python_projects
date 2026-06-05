import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Configuração do caminho do dataset (relativo ao local deste script)
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "dataset" / "dataset_filtered.xlsx"

def carregar_dados() -> pd.DataFrame:
    """
    Lê o dataset base, força tipagens corretas e higieniza valores anômalos.
    O uso de apply(pd.to_numeric) evita falhas silenciosas na renderização gráfica.
    """
    try:
        df = pd.read_excel(DATASET_PATH)
        cols_numericas = ['valor_m2', 'vl_base_calculo', 'area_edificada', 'latitude', 'longitude', 'exercicio']
        
        # Conversão vetorizada forçada (erros viram NaN)
        df[cols_numericas] = df[cols_numericas].apply(pd.to_numeric, errors='coerce')
        
        # Higienização contra crashes na engine em JavaScript do Plotly
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(subset=['valor_m2', 'latitude', 'longitude', 'area_edificada', 'exercicio'], inplace=True)
        
        return df[df['valor_m2'] > 0]
    
    except Exception as e:
        print(f"ATENÇÃO - Erro crítico ao carregar dataset base: {e}")
        # Retorna estrutura vazia segura para não quebrar a árvore de componentes
        return pd.DataFrame(columns=[
            'exercicio', 'bairro', 'tipo_uso_imovel', 'padrao_construcao', 
            'valor_m2', 'latitude', 'longitude', 'area_edificada', 'vl_base_calculo'
        ])

# Carga inicial estática (Executada apenas uma vez ao iniciar o servidor)
df_base = carregar_dados()

# Variáveis globais otimizadas em memória
anos_disponiveis = sorted(df_base['exercicio'].unique()) if not df_base.empty else [2020, 2026]
MIN_ANO, MAX_ANO = int(min(anos_disponiveis)), int(max(anos_disponiveis))
PADROES_DISPONIVEIS = sorted(df_base['padrao_construcao'].dropna().unique()) if not df_base.empty else ['Normal']
BAIRROS_DISPONIVEIS = sorted(df_base['bairro'].dropna().unique()) if not df_base.empty else []

# Cores de Uso do Imóvel para consistência
CORES_USO = {
    "Residencial": "#00B4D8", # Azul
    "Comercial": "#E5A93B"    # Dourado
}

"""
data_manager.py
---------------
Módulo responsável pela leitura, tipagem e otimização de memória do dataset.
Funciona como um "Singleton", ou seja, os dados são carregados apenas UMA VEZ na memória
quando a aplicação sobe, otimizando drasticamente a performance para os múltiplos usuários.
"""

import pandas as pd
from pathlib import Path


def carregar_dados() -> pd.DataFrame:
    """
    Lê o arquivo .parquet de forma segura e aplica tipagem para reduzir o uso de memória (RAM).
    """
    try:
        # resolve().parent garante que o código ache o arquivo de dados independentemente
        # de onde o terminal (prompt/cmd) foi aberto.
        DIRETORIO_ATUAL = Path(__file__).resolve().parent
        caminho = DIRETORIO_ATUAL / "processamento_petroleo_filtered.parquet"

        # Read Parquet é nativamente mais rápido e consome menos memória que read_csv ou excel
        df = pd.read_parquet(caminho)

        # OTIMIZAÇÃO DE MEMÓRIA: Converter strings repetitivas para 'category' reduz o
        # peso do DataFrame e acelera muito as filtragens no backend.
        cols_cat = ['unidade_da_federacao', 'refinaria', 'materia_prima']
        df[cols_cat] = df[cols_cat].astype('category')

        # Garante que as datas operem com métodos temporais do Pandas nativamente
        df['data'] = pd.to_datetime(df['data'])

        return df

    except Exception as e:
        print(f"Erro Crítico na Ingestão: {e}")
        # Retorna dataframe vazio estruturado para evitar o crash (tela de erro fatal) na interface
        return pd.DataFrame()


# -------------------------------------------------------------------------
# VARIÁVEIS GLOBAIS ESTÁTICAS (Pré-computadas na inicialização)
# -------------------------------------------------------------------------
df_base = carregar_dados()

# Extraímos as opções dos filtros dinamicamente com base nos dados reais disponíveis
ANOS_DISPONIVEIS = sorted(df_base['ano'].unique()) if not df_base.empty else [1990, 2026]
MIN_ANO, MAX_ANO = int(min(ANOS_DISPONIVEIS)), int(max(ANOS_DISPONIVEIS))

# .cat.categories é extremamente rápido para extrair valores únicos de colunas categóricas
MATERIAS_PRIMAS = df_base['materia_prima'].cat.categories.tolist() if not df_base.empty else []
ESTADOS = df_base['unidade_da_federacao'].cat.categories.tolist() if not df_base.empty else []

# Paleta Azure → Celeste para consistência visual em todos os gráficos
# Baseada nas decisões de design: Azure (#007FFF) + Celeste (#ADFFFF)
CORES_MATERIA_PRIMA = {
    "PETRÓLEO NACIONAL":  "#007FFF",   # Azure — protagonista, maior volume
    "PETRÓLEO IMPORTADO": "#ADFFFF",   # Celeste — contrastante e vibrante
    "OUTRAS CARGAS":      "#52C8FF",   # Azul médio — terceiro elemento
}
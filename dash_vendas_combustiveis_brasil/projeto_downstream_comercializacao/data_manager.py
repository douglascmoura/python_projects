"""
data_manager.py
---------------
Módulo responsável pela leitura, tipagem e otimização de memória do dataset.
Funciona como um "Singleton": os dados são carregados apenas UMA VEZ na memória
quando a aplicação sobe, otimizando a performance para múltiplos usuários.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import pandas as pd

# =========================================================================
# DIRETÓRIO BASE (resolve independente de onde o terminal foi aberto)
# =========================================================================
DIRETORIO_ATUAL = Path(__file__).resolve().parent


# =========================================================================
# MAPEAMENTO: Nome por extenso do GeoJSON → UF em caixa alta do dataset
# =========================================================================
MAPA_UF_GEOJSON = {
    "Acre": "ACRE",
    "Alagoas": "ALAGOAS",
    "Amapá": "AMAPÁ",
    "Amazonas": "AMAZONAS",
    "Bahia": "BAHIA",
    "Ceará": "CEARÁ",
    "Distrito Federal": "DISTRITO FEDERAL",
    "Espírito Santo": "ESPÍRITO SANTO",
    "Goiás": "GOIÁS",
    "Maranhão": "MARANHÃO",
    "Mato Grosso": "MATO GROSSO",
    "Mato Grosso do Sul": "MATO GROSSO DO SUL",
    "Minas Gerais": "MINAS GERAIS",
    "Pará": "PARÁ",
    "Paraíba": "PARAÍBA",
    "Paraná": "PARANÁ",
    "Pernambuco": "PERNAMBUCO",
    "Piauí": "PIAUÍ",
    "Rio de Janeiro": "RIO DE JANEIRO",
    "Rio Grande do Norte": "RIO GRANDE DO NORTE",
    "Rio Grande do Sul": "RIO GRANDE DO SUL",
    "Rondônia": "RONDÔNIA",
    "Roraima": "RORAIMA",
    "Santa Catarina": "SANTA CATARINA",
    "São Paulo": "SÃO PAULO",
    "Sergipe": "SERGIPE",
    "Tocantins": "TOCANTINS",
}


def carregar_geojson() -> dict:
    """
    Lê o GeoJSON dos estados brasileiros e normaliza as propriedades
    para que o campo 'name' corresponda ao dataset do ANP (caixa alta com acentos).
    """
    try:
        caminho_geo = DIRETORIO_ATUAL / "assets" / "brazil_states.geojson"
        with open(caminho_geo, "r", encoding="utf-8") as f:
            geo = json.load(f)

        # Normaliza o campo 'name' para coincidir com os valores do dataset
        for feature in geo["features"]:
            nome_original = feature["properties"].get("name", "")
            feature["properties"]["uf_dataset"] = MAPA_UF_GEOJSON.get(
                nome_original, nome_original.upper()
            )

        return geo

    except Exception as e:
        print(f"Erro ao carregar GeoJSON: {e}")
        return {}


def carregar_dados() -> pd.DataFrame:
    """
    Lê o arquivo .parquet de forma segura e aplica tipagem para reduzir
    o uso de memória (RAM) e acelerar filtragens.
    """
    try:
        caminho = DIRETORIO_ATUAL / "vendas_combustiveis_filtered.parquet"
        df = pd.read_parquet(caminho)

        # OTIMIZAÇÃO: Converter strings repetitivas para 'category'
        # reduz o peso do DataFrame e acelera muito as filtragens.
        cols_cat = ["regiao", "uf", "produto"]
        df[cols_cat] = df[cols_cat].astype("category")

        # Garante que as datas operem com métodos temporais do Pandas
        df["data"] = pd.to_datetime(df["data"])

        # Garante que vendas sejam numéricas (segurança)
        df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce").fillna(0)

        return df

    except Exception as e:
        print(f"Erro Crítico na Ingestão: {e}")
        # Retorna DataFrame vazio estruturado para evitar crash na interface
        return pd.DataFrame(columns=["ano", "mes", "regiao", "uf", "produto", "vendas", "data"])


# =========================================================================
# VARIÁVEIS GLOBAIS ESTÁTICAS (Pré-computadas na inicialização)
# =========================================================================
df_base = carregar_dados()
geojson_brasil = carregar_geojson()

# Extração dinâmica dos filtros a partir dos dados reais
MIN_ANO = int(df_base["ano"].min()) if not df_base.empty else 1990
MAX_ANO = int(df_base["ano"].max()) if not df_base.empty else 2025

# .cat.categories é muito rápido para extrair únicos de colunas categóricas
PRODUTOS = sorted(df_base["produto"].cat.categories.tolist()) if not df_base.empty else []
ESTADOS = sorted(df_base["uf"].cat.categories.tolist()) if not df_base.empty else []
REGIOES = sorted(df_base["regiao"].cat.categories.tolist()) if not df_base.empty else []

# =========================================================================
# PALETA DE CORES — 8 COMBUSTÍVEIS
# Consistência visual garantida em todos os gráficos da aplicação.
# =========================================================================
CORES_PRODUTO = {
    "ÓLEO DIESEL":          "#724C39",  # Accent principal — terracota quente
    "GASOLINA C":           "#9E7E6A",  # Marrom claro
    "GLP":                  "#808A93",  # Cinza aço
    "ETANOL HIDRATADO":     "#5A8A5A",  # Verde escuro (biocombustível)
    "ÓLEO COMBUSTÍVEL":     "#A06848",  # Âmbar oxidado
    "QUEROSENE DE AVIAÇÃO": "#4A6880",  # Azul petróleo
    "QUEROSENE ILUMINANTE": "#6A7080",  # Cinza azulado
    "GASOLINA DE AVIAÇÃO":  "#7A5570",  # Violeta acinzentado
}

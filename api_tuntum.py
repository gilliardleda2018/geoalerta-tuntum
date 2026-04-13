from pathlib import Path
import json
import numpy as np

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import geopandas as gpd

app = FastAPI(
    title="API - Modelo IA de Enchentes em Tuntum",
    description="API para consumo dos dados do modelo espacial e da IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "resultado_ia_tuntum.csv"
GPKG_PATH = BASE_DIR / "saida" / "score_enchente_tuntum.gpkg"
BAIRROS_PATH = BASE_DIR / "dados" / "bairros_tuntum.geojson"


def load_csv() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {CSV_PATH}")
    return pd.read_csv(CSV_PATH)


def load_gdf() -> gpd.GeoDataFrame:
    if not GPKG_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {GPKG_PATH}")
    gdf = gpd.read_file(GPKG_PATH)
    if gdf.crs is None:
        gdf = gdf.set_crs(31983)
    return gdf


def load_bairros() -> gpd.GeoDataFrame:
    if not BAIRROS_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {BAIRROS_PATH}")

    bairros = gpd.read_file(BAIRROS_PATH)

    if bairros.crs is None:
        raise ValueError("A camada de bairros está sem CRS definido.")

    possiveis = [
        "bairro", "BAIRRO", "nome", "NOME",
        "nm_bairro", "NM_BAIRRO", "name", "Name"
    ]

    nome_col = None
    for c in possiveis:
        if c in bairros.columns:
            nome_col = c
            break

    if nome_col is None:
        raise ValueError(
            f"Não encontrei a coluna do bairro. Colunas disponíveis: {list(bairros.columns)}"
        )

    bairros = bairros.rename(columns={nome_col: "bairro"}).copy()
    bairros["bairro"] = bairros["bairro"].astype(str).str.strip()

    return bairros[["bairro", "geometry"]]


def clean_records(df: pd.DataFrame):
    df = df.copy()
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def aggregate_bairros() -> gpd.GeoDataFrame:
    gdf = load_gdf()
    df = load_csv()
    bairros = load_bairros()

    keep_cols = [
        c for c in ["cell_id", "score_0_10", "chuva_proxy", "risco_previsto"]
        if c in df.columns
    ]
    df = df[keep_cols].copy()

    cells = gdf.merge(df, on=["cell_id", "score_0_10"], how="left")

    bairros = bairros.to_crs(cells.crs)

    joined = gpd.sjoin(
        cells[[
            "cell_id",
            "score_0_10",
            "risco_previsto",
            "chuva_proxy",
            "dist_water_m",
            "elev_mean",
            "slope_mean",
            "geometry"
        ]],
        bairros[["bairro", "geometry"]],
        how="inner",
        predicate="intersects"
    )

    if joined.empty:
        raise ValueError("Nenhuma célula intersectou os bairros.")

    agg = joined.groupby("bairro", as_index=False).agg(
        score_medio=("score_0_10", "mean"),
        score_maximo=("score_0_10", "max"),
        dist_media_agua_m=("dist_water_m", "mean"),
        elev_media=("elev_mean", "mean"),
        slope_media=("slope_mean", "mean"),
        qtd_celulas=("cell_id", "nunique"),
        qtd_altas=("risco_previsto", lambda s: int((s.astype(str) == "Alta").sum())),
        qtd_muito_altas=("risco_previsto", lambda s: int((s.astype(str) == "Muito Alta").sum())),
    )

    agg["percentual_critico"] = (
        (agg["qtd_altas"] + agg["qtd_muito_altas"]) / agg["qtd_celulas"] * 100
    ).round(2)

    def classificar(score):
        if score < 4:
            return "Baixa"
        elif score < 6:
            return "Moderada"
        elif score < 8:
            return "Alta"
        return "Muito Alta"

    agg["classe_bairro"] = agg["score_medio"].apply(classificar)

    bairros_agg = bairros.merge(agg, on="bairro", how="left").copy()
    bairros_agg = bairros_agg.dropna(subset=["score_medio"]).copy()

    bairros_agg = bairros_agg.replace([np.inf, -np.inf], np.nan)

    return bairros_agg


@app.get("/")
def home():
    return {
        "mensagem": "API do modelo IA de enchentes em Tuntum ativa",
        "endpoints_principais": [
            "/api/resumo",
            "/api/riscos",
            "/api/top-criticas",
            "/api/geojson-risco",
            "/api/geojson-risco/{classe}",
            "/api/bairros-resumo",
            "/api/geojson-bairros"
        ]
    }


@app.get("/api/resumo")
def resumo():
    df = load_csv()
    return {
        "total_celulas": int(len(df)),
        "maior_score": float(df["score_0_10"].max()),
        "media_score": float(df["score_0_10"].mean()),
        "risco_dominante": str(df["risco_previsto"].mode().iloc[0])
    }


@app.get("/api/riscos")
def listar_riscos(limit: int = Query(100, ge=1, le=5000)):
    df = load_csv()
    df = df.sort_values("score_0_10", ascending=False).head(limit)
    return clean_records(df)


@app.get("/api/top-criticas")
def top_criticas(qtd: int = Query(10, ge=1, le=100)):
    df = load_csv()
    top = df.sort_values("score_0_10", ascending=False).head(qtd)
    return clean_records(top)


@app.get("/api/riscos/{classe}")
def filtrar_por_risco(classe: str):
    df = load_csv()
    filtrado = df[df["risco_previsto"].astype(str).str.lower() == classe.lower()]
    return clean_records(filtrado)


@app.get("/api/geojson-risco")
def geojson_risco(limit: int = Query(5000, ge=1, le=50000)):
    gdf = load_gdf()
    df = load_csv()

    keep_cols = [
        c for c in ["cell_id", "score_0_10", "chuva_proxy", "risco_previsto"]
        if c in df.columns
    ]
    df = df[keep_cols].copy()

    merged = gdf.merge(df, on=["cell_id", "score_0_10"], how="left")
    merged = merged.to_crs(4326)

    if len(merged) > limit:
        merged = merged.sort_values("score_0_10", ascending=False).head(limit)

    return json.loads(merged.to_json())


@app.get("/api/geojson-risco/{classe}")
def geojson_risco_classe(classe: str, limit: int = Query(5000, ge=1, le=50000)):
    gdf = load_gdf()
    df = load_csv()

    keep_cols = [
        c for c in ["cell_id", "score_0_10", "chuva_proxy", "risco_previsto"]
        if c in df.columns
    ]
    df = df[keep_cols].copy()
    df = df[df["risco_previsto"].astype(str).str.lower() == classe.lower()]

    merged = gdf.merge(df, on=["cell_id", "score_0_10"], how="inner")
    merged = merged.to_crs(4326)

    if len(merged) > limit:
        merged = merged.sort_values("score_0_10", ascending=False).head(limit)

    return json.loads(merged.to_json())


@app.get("/api/bairros-resumo")
def bairros_resumo(limit: int = Query(100, ge=1, le=500)):
    bairros_agg = aggregate_bairros()
    df = bairros_agg.drop(columns="geometry").sort_values("score_medio", ascending=False).head(limit)
    return clean_records(df)


@app.get("/api/geojson-bairros")
def geojson_bairros(limit: int = Query(100, ge=1, le=500)):
    bairros_agg = aggregate_bairros()
    bairros_agg = bairros_agg.sort_values("score_medio", ascending=False).head(limit)
    bairros_agg = bairros_agg.to_crs(4326)
    return json.loads(bairros_agg.to_json())
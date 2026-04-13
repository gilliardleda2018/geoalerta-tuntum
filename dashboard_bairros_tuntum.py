#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from pathlib import Path
import json
import warnings

import branca.colormap as cm
import folium
import geopandas as gpd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Dashboard por Bairro - Enchentes Tuntum/MA", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GPKG = BASE_DIR / "saida" / "score_enchente_tuntum.gpkg"
BAIRRO_CANDIDATES = [
    BASE_DIR / "dados" / "bairros_tuntum.geojson",
    BASE_DIR / "dados" / "bairros_tuntum.gpkg",
    BASE_DIR / "dados" / "bairros_tuntum.shp",
]
COLUNAS_NOME_BAIRRO = [
    "bairro","BAIRRO","nome","NOME","nm_bairro","NM_BAIRRO",
    "name","Name","bairro_nome","Bairro"
]

@st.cache_data
def load_cells(gpkg_path: str):
    gdf = gpd.read_file(gpkg_path)
    if gdf.crs is None:
        gdf = gdf.set_crs(31983)
    return gdf

def find_bairro_file():
    for p in BAIRRO_CANDIDATES:
        if p.exists():
            return p
    return None

@st.cache_data
def load_bairros(bairro_path: str):
    gdf = gpd.read_file(bairro_path)
    if gdf.crs is None:
        raise ValueError("A camada de bairros está sem CRS definido.")
    nome_col = None
    for c in COLUNAS_NOME_BAIRRO:
        if c in gdf.columns:
            nome_col = c
            break
    if nome_col is None:
        raise ValueError(f"Não encontrei uma coluna de nome do bairro. Colunas disponíveis: {list(gdf.columns)}")
    gdf = gdf.rename(columns={nome_col: "bairro"}).copy()
    gdf["bairro"] = gdf["bairro"].astype(str).str.strip()
    return gdf[["bairro", "geometry"]]

def aggregate_by_bairro(cells, bairros):
    cells_local = cells.copy()
    bairros_local = bairros.to_crs(cells_local.crs).copy()

    joined = gpd.sjoin(
        cells_local[["cell_id","score_0_10","classe","dist_water_m","elev_mean","slope_mean","geometry"]],
        bairros_local[["bairro","geometry"]],
        how="inner",
        predicate="intersects"
    )

    if joined.empty:
        raise ValueError("Nenhuma célula intersectou os bairros. Verifique o CRS e a área da camada.")

    agg = joined.groupby("bairro", as_index=False).agg(
        score_medio=("score_0_10", "mean"),
        score_maximo=("score_0_10", "max"),
        score_minimo=("score_0_10", "min"),
        dist_media_agua_m=("dist_water_m", "mean"),
        elev_media=("elev_mean", "mean"),
        slope_media=("slope_mean", "mean"),
        qtd_celulas=("cell_id", "nunique"),
        qtd_celulas_altas=("classe", lambda s: int((s.astype(str) == "Alta").sum())),
        qtd_celulas_muito_altas=("classe", lambda s: int((s.astype(str) == "Muito Alta").sum()))
    )

    agg["percentual_alta_ou_mais"] = (
        (agg["qtd_celulas_altas"] + agg["qtd_celulas_muito_altas"]) / agg["qtd_celulas"] * 100
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
    bairros_agg = bairros_local.merge(agg, on="bairro", how="left").copy()
    bairros_agg = bairros_agg.dropna(subset=["score_medio"]).copy()
    return bairros_agg

def make_bairro_map(gdf_bairros, metric_col):
    gdf_wgs = gdf_bairros.to_crs(4326).copy()
    center = gdf_wgs.geometry.unary_union.centroid
    fmap = folium.Map(location=[center.y, center.x], zoom_start=12, tiles="CartoDB positron")

    vmin = float(gdf_wgs[metric_col].min())
    vmax = float(gdf_wgs[metric_col].max())

    colormap = cm.LinearColormap(
        colors=["#2E8B57", "#FFD166", "#F4A261", "#D62828"],
        vmin=vmin, vmax=vmax,
        caption=metric_col.replace("_", " ").title()
    )

    def style_function(feature):
        value = feature["properties"].get(metric_col, 0)
        return {"fillColor": colormap(value), "color": "#333333", "weight": 1.0, "fillOpacity": 0.75}

    tooltip_fields = [c for c in ["bairro","score_medio","score_maximo","classe_bairro","qtd_celulas","percentual_alta_ou_mais","dist_media_agua_m"] if c in gdf_wgs.columns]
    aliases = {
        "bairro": "Bairro",
        "score_medio": "Score médio",
        "score_maximo": "Score máximo",
        "classe_bairro": "Classe",
        "qtd_celulas": "Qtd. células",
        "percentual_alta_ou_mais": "% alta ou mais",
        "dist_media_agua_m": "Dist. média da água (m)"
    }

    folium.GeoJson(
        data=json.loads(gdf_wgs.to_json()),
        name="Bairros",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=[aliases.get(f, f) for f in tooltip_fields], localize=True)
    ).add_to(fmap)

    colormap.add_to(fmap)
    folium.LayerControl().add_to(fmap)
    return fmap

def main():
    st.title("🗺️ Dashboard por Bairro - Vulnerabilidade a Enchentes em Tuntum/MA")
    st.caption("Agregação das células do modelo espacial para visualização por bairro.")

    with st.sidebar:
        st.header("Arquivos")
        gpkg_path = st.text_input("Arquivo das células (.gpkg)", value=str(DEFAULT_GPKG))
        detected_bairro_file = find_bairro_file()
        bairro_default = str(detected_bairro_file) if detected_bairro_file else ""
        bairro_path = st.text_input("Camada de bairros (.geojson/.gpkg/.shp)", value=bairro_default)

    if not Path(gpkg_path).exists():
        st.error("Não encontrei o GeoPackage das células. Verifique o caminho.")
        st.stop()

    if not bairro_path or not Path(bairro_path).exists():
        st.error("Não encontrei a camada de bairros. Coloque um arquivo como dados\\bairros_tuntum.geojson ou informe o caminho correto.")
        st.info("Esse dashboard precisa de uma camada oficial de bairros para mostrar o nome do bairro em vez do número da célula.")
        st.stop()

    try:
        cells = load_cells(gpkg_path)
        bairros = load_bairros(bairro_path)
        bairros_agg = aggregate_by_bairro(cells, bairros)
    except Exception as e:
        st.error(f"Erro ao processar os bairros: {e}")
        st.stop()

    if bairros_agg.empty:
        st.error("Nenhum bairro com dados agregados foi encontrado.")
        st.stop()

    metric_col = st.selectbox("Métrica exibida no mapa e no ranking", ["score_medio", "score_maximo", "percentual_alta_ou_mais"], index=0)
    classe_options = ["Todas"] + sorted(bairros_agg["classe_bairro"].dropna().astype(str).unique().tolist())
    selected_class = st.selectbox("Filtrar por classe do bairro", classe_options)

    dff = bairros_agg.copy()
    if selected_class != "Todas":
        dff = dff[dff["classe_bairro"].astype(str) == selected_class].copy()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Maior score médio", f"{dff['score_medio'].max():.2f}")
    k2.metric("Maior score máximo", f"{dff['score_maximo'].max():.2f}")
    k3.metric("Qtd. bairros", f"{len(dff)}")
    k4.metric("% alta ou mais (máx.)", f"{dff['percentual_alta_ou_mais'].max():.2f}%")

    c1, c2 = st.columns(2)
    with c1:
        ranking = dff.sort_values(metric_col, ascending=False).drop(columns="geometry")
        fig_bar = px.bar(ranking, x="bairro", y=metric_col, color="classe_bairro",
                         title=f"Ranking de bairros por {metric_col}",
                         labels={"bairro": "Bairro", metric_col: metric_col.replace("_", " ").title()})
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        class_count = dff["classe_bairro"].astype(str).value_counts().reset_index()
        class_count.columns = ["classe_bairro", "quantidade"]
        fig_pie = px.pie(class_count, names="classe_bairro", values="quantidade", title="Distribuição dos bairros por classe")
        st.plotly_chart(fig_pie, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_scatter = px.scatter(
            dff.drop(columns="geometry"),
            x="dist_media_agua_m", y="score_medio", size="qtd_celulas",
            color="classe_bairro", hover_data=["bairro","score_maximo","percentual_alta_ou_mais"],
            title="Score médio x Distância média da água"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        fig_hist = px.histogram(dff.drop(columns="geometry"), x="score_medio", nbins=15, color="classe_bairro",
                                title="Distribuição do score médio por bairro")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("📍 Mapa interativo por bairro")
    fmap = make_bairro_map(dff, metric_col)
    st_folium(fmap, width=None, height=680)

    st.subheader("📋 Tabela consolidada por bairro")
    show_cols = ["bairro","score_medio","score_maximo","classe_bairro","qtd_celulas","qtd_celulas_altas","qtd_celulas_muito_altas","percentual_alta_ou_mais","dist_media_agua_m","elev_media","slope_media"]
    st.dataframe(dff[show_cols].sort_values(metric_col, ascending=False), use_container_width=True, hide_index=True)

    csv_out = dff.drop(columns="geometry").sort_values(metric_col, ascending=False).to_csv(index=False).encode("utf-8")
    st.download_button("Baixar tabela por bairro em CSV", data=csv_out, file_name="score_por_bairro_tuntum.csv", mime="text/csv")

if __name__ == "__main__":
    main()

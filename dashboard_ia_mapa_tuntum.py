#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard IA + Mapa - Tuntum", layout="wide")

BASE = Path(__file__).resolve().parent
GPKG_PATH = BASE / "saida" / "score_enchente_tuntum.gpkg"
CSV_IA_PATH = BASE / "resultado_ia_tuntum.csv"

@st.cache_data
def load_data():
    if not GPKG_PATH.exists():
        raise FileNotFoundError(f"Não encontrei: {GPKG_PATH}")
    if not CSV_IA_PATH.exists():
        raise FileNotFoundError(f"Não encontrei: {CSV_IA_PATH}")

    gdf = gpd.read_file(GPKG_PATH)
    if gdf.crs is None:
        gdf = gdf.set_crs(31983)

    df_ia = pd.read_csv(CSV_IA_PATH)
    keep_cols = [c for c in ["cell_id", "score_0_10", "chuva_proxy", "risco_previsto"] if c in df_ia.columns]
    df_ia = df_ia[keep_cols].copy()

    merged = gdf.merge(df_ia, on=["cell_id", "score_0_10"], how="left")
    return merged

def make_map(gdf_plot):
    gdf_wgs = gdf_plot.to_crs(4326).copy()
    center = gdf_wgs.geometry.unary_union.centroid

    fmap = folium.Map(location=[center.y, center.x], zoom_start=12, tiles="CartoDB positron")

    color_map = {
        "Baixa": "#2E8B57",
        "Moderada": "#FFD166",
        "Alta": "#F4A261",
        "Muito Alta": "#D62828"
    }

    def style_function(feature):
        risco = feature["properties"].get("risco_previsto", "Baixa")
        fill = color_map.get(risco, "#999999")
        return {"fillColor": fill, "color": "#333333", "weight": 0.3, "fillOpacity": 0.75}

    tooltip_fields = [c for c in ["cell_id", "score_0_10", "chuva_proxy", "risco_previsto", "dist_water_m", "elev_mean"] if c in gdf_wgs.columns]
    tooltip_aliases = {
        "cell_id": "Célula",
        "score_0_10": "Score",
        "chuva_proxy": "Chuva proxy",
        "risco_previsto": "Risco previsto",
        "dist_water_m": "Dist. água (m)",
        "elev_mean": "Elevação média"
    }

    folium.GeoJson(
        data=json.loads(gdf_wgs.to_json()),
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=[tooltip_aliases.get(f, f) for f in tooltip_fields], localize=True),
        name="Risco IA"
    ).add_to(fmap)

    return fmap

def main():
    st.title("🧠🌧️ Dashboard IA + Mapa Territorial - Tuntum/MA")
    st.caption("Integra score espacial, proxy meteorológico e classificação por IA.")

    try:
        gdf = load_data()
    except Exception as e:
        st.error(str(e))
        st.stop()

    risco_options = ["Todos"] + sorted(gdf["risco_previsto"].dropna().astype(str).unique().tolist())
    risco_sel = st.selectbox("Filtrar risco previsto", risco_options)

    dff = gdf.copy()
    if risco_sel != "Todos":
        dff = dff[dff["risco_previsto"].astype(str) == risco_sel].copy()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de células", f"{len(dff):,}".replace(",", "."))
    col2.metric("Maior score", f"{dff['score_0_10'].max():.2f}")
    col3.metric("Média score", f"{dff['score_0_10'].mean():.2f}")
    modo = dff["risco_previsto"].mode()
    col4.metric("Risco dominante", modo.iloc[0] if len(modo) else "-")

    c1, c2 = st.columns(2)
    with c1:
        top_df = dff.drop(columns="geometry").sort_values("score_0_10", ascending=False).head(15)
        fig_bar = px.bar(top_df, x="cell_id", y="score_0_10", color="risco_previsto",
                         title="Top 15 células por score",
                         labels={"cell_id": "Célula", "score_0_10": "Score"})
        fig_bar.update_layout(xaxis_type="category")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        class_count = dff["risco_previsto"].astype(str).value_counts().reset_index()
        class_count.columns = ["risco_previsto", "quantidade"]
        fig_pie = px.pie(class_count, names="risco_previsto", values="quantidade", title="Distribuição do risco previsto")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("🗺️ Mapa interativo territorial")
    fmap = make_map(dff)
    st_folium(fmap, width=None, height=700)

    st.subheader("📋 Tabela IA consolidada")
    show_cols = [c for c in ["cell_id", "score_0_10", "chuva_proxy", "risco_previsto", "dist_water_m", "elev_mean", "slope_mean"] if c in dff.columns]
    table_df = dff.drop(columns="geometry")[show_cols].sort_values("score_0_10", ascending=False)
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    st.download_button(
        "Baixar tabela IA em CSV",
        data=table_df.to_csv(index=False).encode("utf-8"),
        file_name="dashboard_ia_tuntum_filtrado.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

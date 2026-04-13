#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from pathlib import Path
import json

import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard de Vulnerabilidade a Enchentes - Tuntum/MA", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GPKG = BASE_DIR / "saida" / "score_enchente_tuntum.gpkg"
DEFAULT_CSV = BASE_DIR / "saida" / "score_enchente_tuntum.csv"

@st.cache_data
def load_data(gpkg_path: str | None, csv_path: str | None):
    gdf = None
    if gpkg_path and Path(gpkg_path).exists():
        gdf = gpd.read_file(gpkg_path)
        if gdf.crs is None:
            gdf = gdf.set_crs(31983)
        df = pd.DataFrame(gdf.drop(columns="geometry"))
    elif csv_path and Path(csv_path).exists():
        df = pd.read_csv(csv_path)
    else:
        raise FileNotFoundError("Não foi encontrado nem o GeoPackage nem o CSV.")
    return gdf, df

def make_folium_map(gdf: gpd.GeoDataFrame, color_col: str = "score_0_10"):
    gdf_wgs = gdf.to_crs(4326).copy()
    center = gdf_wgs.geometry.unary_union.centroid
    fmap = folium.Map(location=[center.y, center.x], zoom_start=12, tiles="CartoDB positron")

    min_score = float(gdf_wgs[color_col].min())
    max_score = float(gdf_wgs[color_col].max())

    colormap = cm.LinearColormap(
        colors=["#2E8B57", "#FFD166", "#F4A261", "#D62828"],
        vmin=min_score, vmax=max_score,
        caption="Score de vulnerabilidade (0 a 10)"
    )

    def style_function(feature):
        score = feature["properties"].get(color_col, 0)
        return {
            "fillColor": colormap(score),
            "color": "#333333",
            "weight": 0.4,
            "fillOpacity": 0.70
        }

    tooltip_fields = [c for c in ["cell_id", "score_0_10", "classe", "dist_water_m", "elev_mean", "slope_mean"] if c in gdf_wgs.columns]
    aliases = {
        "cell_id": "Célula", "score_0_10": "Score", "classe": "Classe",
        "dist_water_m": "Dist. água (m)", "elev_mean": "Elevação média", "slope_mean": "Declividade média"
    }

    folium.GeoJson(
        data=json.loads(gdf_wgs.to_json()),
        name="Células",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=[aliases.get(f, f) for f in tooltip_fields], localize=True)
    ).add_to(fmap)

    colormap.add_to(fmap)
    folium.LayerControl().add_to(fmap)
    return fmap

def main():
    st.title("🌧️ Dashboard de Vulnerabilidade a Enchentes - Tuntum/MA")
    st.caption("Modelo espacial baseado em relevo, proximidade da drenagem, edificações e eventos históricos.")

    with st.sidebar:
        st.header("Arquivos de entrada")
        gpkg_path = st.text_input("GeoPackage (.gpkg)", value=str(DEFAULT_GPKG))
        csv_path = st.text_input("CSV (.csv)", value=str(DEFAULT_CSV))
        use_only_csv = st.checkbox("Usar apenas CSV", value=False)

    try:
        gdf, df = load_data(None if use_only_csv else gpkg_path, csv_path)
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.stop()

    col1, col2 = st.columns([1, 1])
    with col1:
        class_options = ["Todas"] + sorted(df["classe"].dropna().astype(str).unique().tolist()) if "classe" in df.columns else ["Todas"]
        selected_class = st.selectbox("Filtrar por classe", class_options)
    with col2:
        top_n = st.slider("Top N para ranking", min_value=5, max_value=30, value=10)

    dff = df.copy()
    if selected_class != "Todas" and "classe" in dff.columns:
        dff = dff[dff["classe"].astype(str) == selected_class].copy()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Maior score", f"{dff['score_0_10'].max():.2f}" if len(dff) else "0.00")
    k2.metric("Média do score", f"{dff['score_0_10'].mean():.2f}" if len(dff) else "0.00")
    k3.metric("Qtd. células", f"{len(dff):,}".replace(",", "."))
    k4.metric("Distância média da água (m)", f"{dff['dist_water_m'].mean():.1f}" if "dist_water_m" in dff.columns and len(dff) else "0.0")

    c1, c2 = st.columns(2)
    with c1:
        top_df = dff.sort_values("score_0_10", ascending=False).head(top_n).copy()
        fig_top = px.bar(top_df, x="cell_id", y="score_0_10", color="classe" if "classe" in top_df.columns else None,
                         title=f"Top {top_n} células mais vulneráveis",
                         labels={"cell_id": "Célula", "score_0_10": "Score"})
        fig_top.update_layout(xaxis_type="category")
        st.plotly_chart(fig_top, use_container_width=True)

    with c2:
        if "classe" in dff.columns:
            class_count = dff["classe"].astype(str).value_counts().reset_index()
            class_count.columns = ["classe", "quantidade"]
            fig_pie = px.pie(class_count, names="classe", values="quantidade", title="Distribuição por classe")
            st.plotly_chart(fig_pie, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_scatter = px.scatter(
            dff, x="dist_water_m", y="score_0_10", color="classe" if "classe" in dff.columns else None,
            hover_data=[c for c in ["cell_id", "elev_mean", "slope_mean"] if c in dff.columns],
            title="Score x Distância da drenagem",
            labels={"dist_water_m": "Distância da água (m)", "score_0_10": "Score"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        if "elev_mean" in dff.columns:
            fig_hist = px.histogram(dff, x="elev_mean", nbins=25, title="Distribuição da elevação média",
                                    labels={"elev_mean": "Elevação média"})
            st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("🗺️ Mapa interativo")
    if gdf is not None and not use_only_csv:
        gdf_plot = gdf.copy()
        if selected_class != "Todas" and "classe" in gdf_plot.columns:
            gdf_plot = gdf_plot[gdf_plot["classe"].astype(str) == selected_class].copy()
        fmap = make_folium_map(gdf_plot)
        st_folium(fmap, width=None, height=650)
    else:
        st.warning("Para o mapa interativo, use o arquivo GeoPackage (.gpkg).")

    st.subheader("📋 Tabela das células")
    show_cols = [c for c in ["cell_id", "score_0_10", "classe", "dist_water_m", "elev_mean", "slope_mean"] if c in dff.columns]
    st.dataframe(dff[show_cols].sort_values("score_0_10", ascending=False), use_container_width=True, hide_index=True)

    st.download_button(
        "Baixar tabela filtrada em CSV",
        data=dff.to_csv(index=False).encode("utf-8"),
        file_name="tuntum_dashboard_filtrado.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

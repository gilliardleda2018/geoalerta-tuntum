#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Score de vulnerabilidade a enchentes para Tuntum/MA
---------------------------------------------------

Pipeline espacial em Python com dados reais:
- Limite municipal/urbano por geocodificação do OpenStreetMap
- Hidrografia e edificações do OpenStreetMap
- DEM SRTM 30 m fornecido pelo usuário (GeoTIFF)
- Saída em grade regular (ou agregável depois por bairro/setor)

Requisitos:
    pip install geopandas osmnx rasterio rasterstats shapely pyproj pandas numpy matplotlib folium

Uso básico:
    python score_enchentes_tuntum.py \
        --dem /caminho/para/srtm_tuntum.tif \
        --cell-size 400 \
        --output-dir ./saida_tuntum

Opcional:
    --events /caminho/eventos_enchente.csv

Formato esperado do CSV de eventos:
    nome,latitude,longitude,severidade
    Enchente_Ana_Isabel,-5.321,-44.637,5
    Enchente_Centro,-5.329,-44.650,4

Observação importante:
Este script gera score por células regulares. Se você tiver polígonos de bairros
ou setores censitários, pode substituir a grade por esses polígonos para obter o
score "por região" diretamente.
"""

from __future__ import annotations

import argparse
import math
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio.transform import array_bounds
from rasterstats import zonal_stats
from shapely.geometry import Point, box

warnings.filterwarnings("ignore", category=UserWarning)

CRS_METRIC = "EPSG:31983"  # SIRGAS 2000 / UTM zone 23S (adequado para MA)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera score espacial de vulnerabilidade a enchentes para Tuntum/MA."
    )
    parser.add_argument("--dem", required=True, help="Caminho do DEM SRTM em GeoTIFF.")
    parser.add_argument("--cell-size", type=int, default=400, help="Tamanho da célula em metros.")
    parser.add_argument("--output-dir", default="saida_tuntum", help="Diretório de saída.")
    parser.add_argument(
        "--place",
        default="Tuntum, Maranhão, Brasil",
        help="Nome do lugar para geocodificação OSM.",
    )
    parser.add_argument(
        "--events",
        default=None,
        help="CSV opcional com eventos históricos georreferenciados.",
    )
    return parser.parse_args()


def minmax_scale(series: pd.Series, invert: bool = False) -> pd.Series:
    s = series.astype(float).copy()
    if s.isna().all():
        return pd.Series(np.zeros(len(s)), index=s.index)
    mn, mx = s.min(), s.max()
    if math.isclose(mx, mn):
        scaled = pd.Series(np.zeros(len(s)), index=s.index)
    else:
        scaled = (s - mn) / (mx - mn)
    if invert:
        scaled = 1 - scaled
    return scaled.fillna(0)


def geocode_area(place: str) -> gpd.GeoDataFrame:
    gdf = ox.geocode_to_gdf(place)
    if gdf.empty:
        raise RuntimeError(f"Não foi possível geocodificar: {place}")
    return gdf.to_crs(CRS_METRIC)


def load_osm_hydrology(area_poly) -> gpd.GeoDataFrame:
    tags = {
        "waterway": True,
        "natural": ["water", "wetland"],
        "water": True,
    }
    hyd = ox.features_from_polygon(area_poly, tags)
    if hyd.empty:
        raise RuntimeError("Nenhuma feição hídrica encontrada no OSM para a área.")
    hyd = hyd.reset_index()
    hyd = gpd.GeoDataFrame(hyd, geometry="geometry", crs="EPSG:4326").to_crs(CRS_METRIC)
    hyd = hyd[hyd.geometry.notnull()].copy()
    return hyd


def load_osm_buildings(area_poly) -> gpd.GeoDataFrame:
    tags = {"building": True}
    bld = ox.features_from_polygon(area_poly, tags)
    if bld.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=CRS_METRIC)
    bld = bld.reset_index()
    bld = gpd.GeoDataFrame(bld, geometry="geometry", crs="EPSG:4326").to_crs(CRS_METRIC)
    bld = bld[bld.geometry.notnull()].copy()
    return bld


def create_grid(study_area: gpd.GeoDataFrame, cell_size: int) -> gpd.GeoDataFrame:
    minx, miny, maxx, maxy = study_area.total_bounds
    xs = np.arange(minx, maxx + cell_size, cell_size)
    ys = np.arange(miny, maxy + cell_size, cell_size)

    cells = []
    cell_id = 1
    for x in xs[:-1]:
        for y in ys[:-1]:
            geom = box(x, y, x + cell_size, y + cell_size)
            cells.append({"cell_id": cell_id, "geometry": geom})
            cell_id += 1

    grid = gpd.GeoDataFrame(cells, geometry="geometry", crs=study_area.crs)
    grid = gpd.overlay(grid, study_area[["geometry"]], how="intersection")
    grid = grid[grid.area > (cell_size * cell_size * 0.10)].copy()
    grid["area_m2"] = grid.area
    return grid


def clip_dem_to_area(dem_path: str, area_gdf: gpd.GeoDataFrame, output_dir: Path) -> Path:
    clipped_path = output_dir / "dem_clip.tif"
    with rasterio.open(dem_path) as src:
        area_wgs84 = area_gdf.to_crs(src.crs)
        geoms = [geom.__geo_interface__ for geom in area_wgs84.geometry]
        out_img, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "height": out_img.shape[1],
                "width": out_img.shape[2],
                "transform": out_transform,
            }
        )

        with rasterio.open(clipped_path, "w", **out_meta) as dst:
            dst.write(out_img)

    return clipped_path


def compute_slope_raster(dem_path: Path, output_dir: Path) -> Path:
    slope_path = output_dir / "slope.tif"

    with rasterio.open(dem_path) as src:
        dem = src.read(1, masked=True).astype("float64")
        xres = src.transform.a
        yres = abs(src.transform.e)

        grad_y, grad_x = np.gradient(dem.filled(np.nan), yres, xres)
        slope = np.degrees(np.arctan(np.sqrt(np.square(grad_x) + np.square(grad_y))))

        meta = src.meta.copy()
        meta.update(dtype="float32", nodata=np.nan)

        with rasterio.open(slope_path, "w", **meta) as dst:
            dst.write(slope.astype("float32"), 1)

    return slope_path


def zonal_mean(gdf: gpd.GeoDataFrame, raster_path: Path, col_name: str) -> gpd.GeoDataFrame:
    with rasterio.open(raster_path) as src:
        geoms = gdf.to_crs(src.crs)
        stats = zonal_stats(
            geoms.geometry,
            raster_path,
            stats=["mean"],
            nodata=src.nodata,
            geojson_out=False,
        )
    gdf[col_name] = [s.get("mean", np.nan) for s in stats]
    return gdf


def distance_to_hydrology(gdf: gpd.GeoDataFrame, hydrology: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    hydro_union = hydrology.geometry.union_all()
    gdf["dist_water_m"] = gdf.geometry.centroid.distance(hydro_union)
    return gdf


def building_density(gdf: gpd.GeoDataFrame, buildings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if buildings.empty:
        gdf["building_density"] = 0.0
        return gdf

    buildings = buildings[buildings.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
    if buildings.empty:
        gdf["building_density"] = 0.0
        return gdf

    join = gpd.overlay(
        gdf[["cell_id", "geometry", "area_m2"]],
        buildings[["geometry"]],
        how="intersection",
    )
    if join.empty:
        gdf["building_density"] = 0.0
        return gdf

    join["build_area"] = join.area
    agg = join.groupby("cell_id", as_index=False)["build_area"].sum()
    gdf = gdf.merge(agg, on="cell_id", how="left")
    gdf["build_area"] = gdf["build_area"].fillna(0)
    gdf["building_density"] = gdf["build_area"] / gdf["area_m2"]
    gdf.drop(columns=["build_area"], inplace=True)
    return gdf


def apply_event_boost(gdf: gpd.GeoDataFrame, events_csv: str | None) -> gpd.GeoDataFrame:
    gdf["hist_event_score"] = 0.0
    if not events_csv:
        return gdf

    events = pd.read_csv(events_csv)
    required = {"nome", "latitude", "longitude", "severidade"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"CSV de eventos sem colunas obrigatórias: {missing}")

    events_gdf = gpd.GeoDataFrame(
        events,
        geometry=gpd.points_from_xy(events["longitude"], events["latitude"]),
        crs="EPSG:4326",
    ).to_crs(CRS_METRIC)

    centroids = gdf.copy()
    centroids["geometry"] = centroids.geometry.centroid

    # distância ao evento mais próximo ponderada pela severidade
    scores = []
    for geom in centroids.geometry:
        dists = events_gdf.distance(geom)
        if len(dists) == 0:
            scores.append(0.0)
            continue

        local = []
        for dist, sev in zip(dists, events_gdf["severidade"]):
            # influência decai até 1200 m
            influence = max(0.0, 1 - min(dist, 1200) / 1200)
            local.append(influence * float(sev))
        scores.append(max(local) if local else 0.0)

    gdf["hist_event_score"] = pd.Series(scores, index=gdf.index)
    return gdf


def compute_score(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # normalizações
    gdf["elev_norm"] = minmax_scale(gdf["elev_mean"], invert=True)
    gdf["slope_norm"] = minmax_scale(gdf["slope_mean"], invert=True)  # plano = maior risco
    gdf["water_norm"] = minmax_scale(gdf["dist_water_m"], invert=True)
    gdf["imperv_norm"] = minmax_scale(gdf["building_density"])
    gdf["event_norm"] = minmax_scale(gdf["hist_event_score"])

    # pesos ajustáveis
    gdf["score_0_1"] = (
        0.30 * gdf["elev_norm"]
        + 0.20 * gdf["slope_norm"]
        + 0.25 * gdf["water_norm"]
        + 0.15 * gdf["imperv_norm"]
        + 0.10 * gdf["event_norm"]
    )

    gdf["score_0_10"] = (gdf["score_0_1"] * 10).round(2)

    bins = [-0.1, 3.9, 5.9, 7.9, 10.0]
    labels = ["Baixa", "Moderada", "Alta", "Muito Alta"]
    gdf["classe"] = pd.cut(gdf["score_0_10"], bins=bins, labels=labels)
    return gdf


def export_outputs(gdf: gpd.GeoDataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    gpkg_path = output_dir / "score_enchente_tuntum.gpkg"
    csv_path = output_dir / "score_enchente_tuntum.csv"
    png_path = output_dir / "mapa_score_enchente_tuntum.png"
    html_path = output_dir / "mapa_score_enchente_tuntum.html"

    gdf.to_file(gpkg_path, layer="score", driver="GPKG")
    gdf.drop(columns="geometry").to_csv(csv_path, index=False)

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(column="score_0_10", legend=True, ax=ax)
    ax.set_title("Tuntum/MA - Score espacial de vulnerabilidade a enchentes")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(png_path, dpi=200)
    plt.close(fig)

    try:
        import folium

        center = gdf.to_crs(4326).geometry.unary_union.centroid
        m = folium.Map(location=[center.y, center.x], zoom_start=13, tiles="CartoDB positron")
        folium.GeoJson(
            gdf.to_crs(4326),
            style_function=lambda feat: {
                "fillOpacity": 0.65,
                "weight": 0.4,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["cell_id", "score_0_10", "classe", "dist_water_m", "elev_mean", "slope_mean"],
                aliases=["Célula", "Score", "Classe", "Dist. água (m)", "Elevação média", "Declividade média"],
            ),
        ).add_to(m)
        m.save(html_path)
    except Exception as e:
        print(f"[aviso] mapa HTML não gerado: {e}")

    print(f"[ok] GeoPackage: {gpkg_path}")
    print(f"[ok] CSV: {csv_path}")
    print(f"[ok] PNG: {png_path}")
    if html_path.exists():
        print(f"[ok] HTML: {html_path}")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[1/8] Geocodificando área de estudo...")
    area = geocode_area(args.place)

    print("[2/8] Buscando hidrografia no OSM...")
    area_wgs84_poly = area.to_crs(4326).geometry.iloc[0]
    hydrology = load_osm_hydrology(area_wgs84_poly)

    print("[3/8] Buscando edificações no OSM...")
    buildings = load_osm_buildings(area_wgs84_poly)

    print("[4/8] Criando grade de análise...")
    grid = create_grid(area, args.cell_size)

    print("[5/8] Recortando DEM...")
    dem_clip = clip_dem_to_area(args.dem, area, output_dir)

    print("[6/8] Calculando declividade...")
    slope_path = compute_slope_raster(dem_clip, output_dir)

    print("[7/8] Calculando métricas por célula...")
    grid = zonal_mean(grid, dem_clip, "elev_mean")
    grid = zonal_mean(grid, slope_path, "slope_mean")
    grid = distance_to_hydrology(grid, hydrology)
    grid = building_density(grid, buildings)
    grid = apply_event_boost(grid, args.events)
    grid = compute_score(grid)

    print("[8/8] Exportando saídas...")
    export_outputs(grid, output_dir)

    top10 = (
        grid[["cell_id", "score_0_10", "classe", "dist_water_m", "elev_mean", "slope_mean"]]
        .sort_values("score_0_10", ascending=False)
        .head(10)
    )
    print("\nTop 10 células mais vulneráveis:")
    print(top10.to_string(index=False))


if __name__ == "__main__":
    main()

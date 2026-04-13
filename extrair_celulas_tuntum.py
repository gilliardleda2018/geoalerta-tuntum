#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extrai coordenadas centrais das células críticas e gera tabela para identificação de bairros.
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE = Path(__file__).resolve().parent
INPUT = BASE / "saida" / "score_enchente_tuntum.gpkg"
OUTPUT_CSV = BASE / "saida" / "celulas_criticas_coordenadas.csv"

# células prioritárias (top vistas no dashboard)
TOP_IDS = [25408, 25121, 25691, 25978, 26262, 25977, 25407, 26266, 25693, 25122]

def infer_bairro(score, dist):
    # inferência inicial baseada no padrão hidrológico de Tuntum
    if dist <= 15:
        return "Corredor do riacho Tuntum (Centro / Mil Réis / Tuntum de Cima)"
    elif dist <= 60:
        return "Faixa urbana baixa (Ana Isabel / Vila Mata / Vila Luizão)"
    elif score >= 6:
        return "Entorno de drenagem secundária urbana"
    else:
        return "Faixa urbana intermediária"

def main():
    gdf = gpd.read_file(INPUT)

    if gdf.crs is None:
        gdf = gdf.set_crs(31983)

    gdf = gdf[gdf["cell_id"].isin(TOP_IDS)].copy()

    cent = gdf.copy()
    cent["geometry"] = cent.geometry.centroid

    cent_wgs = cent.to_crs(4326)

    cent_wgs["longitude"] = cent_wgs.geometry.x
    cent_wgs["latitude"] = cent_wgs.geometry.y

    cent_wgs["bairro_provavel"] = [
        infer_bairro(s, d)
        for s, d in zip(cent_wgs["score_0_10"], cent_wgs["dist_water_m"])
    ]

    cols = [
        "cell_id",
        "score_0_10",
        "classe",
        "dist_water_m",
        "latitude",
        "longitude",
        "bairro_provavel"
    ]

    out = pd.DataFrame(cent_wgs[cols]).sort_values("score_0_10", ascending=False)

    out.to_csv(OUTPUT_CSV, index=False)

    print("Arquivo gerado:")
    print(OUTPUT_CSV)
    print("\nTabela:")
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()

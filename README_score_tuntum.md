# Protótipo em Python — Score de vulnerabilidade a enchentes em Tuntum/MA

Este pacote contém um script para gerar um **score espacial de vulnerabilidade a enchentes** em Tuntum.

## O que ele usa
- **OpenStreetMap** para limite geocodificado, hidrografia e edificações
- **SRTM 30 m** para elevação e declividade
- **CSV opcional de eventos históricos** para reforçar áreas já atingidas

## Como rodar
```bash
pip install geopandas osmnx rasterio rasterstats shapely pyproj pandas numpy matplotlib folium
python score_enchentes_tuntum.py --dem /caminho/srtm_tuntum.tif --cell-size 400 --output-dir ./saida_tuntum
```

## Evento histórico opcional
Você pode criar um arquivo `eventos_enchente.csv` com este formato:

```csv
nome,latitude,longitude,severidade
Enchente_Ana_Isabel,-5.321,-44.637,5
Enchente_Centro,-5.329,-44.650,4
```

E então rodar:
```bash
python score_enchentes_tuntum.py --dem /caminho/srtm_tuntum.tif --events eventos_enchente.csv
```

## Saídas
- `score_enchente_tuntum.gpkg`
- `score_enchente_tuntum.csv`
- `mapa_score_enchente_tuntum.png`
- `mapa_score_enchente_tuntum.html`

## Observação
Para obter score **por bairro** ou **por setor censitário**, basta trocar a grade regular por um shapefile/GeoPackage dessas regiões.

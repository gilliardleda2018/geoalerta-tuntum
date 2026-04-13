# Dashboard por bairro - Tuntum/MA

## Requisito principal
Esse dashboard precisa de uma camada de bairros de Tuntum:
- dados\bairros_tuntum.geojson
ou
- dados\bairros_tuntum.gpkg
ou
- dados\bairros_tuntum.shp

A camada deve ter uma coluna com o nome do bairro, por exemplo:
- bairro
- BAIRRO
- nome
- NM_BAIRRO

## Estrutura recomendada
C:\tuntum_enchentes\
├── dashboard_bairros_tuntum.py
├── dados\
│   ├── output_SRTMGL1.tif
│   └── bairros_tuntum.geojson
└── saida\
    └── score_enchente_tuntum.gpkg

## Execução
streamlit run dashboard_bairros_tuntum.py

# API — GeoAlerta Tuntum

Documentação técnica da API principal do projeto GeoAlerta Tuntum.

A API foi desenvolvida para disponibilizar os resultados analíticos do modelo territorial em formato JSON e GeoJSON, permitindo integração com dashboards, aplicação web e futuros sistemas institucionais.

---

# Finalidade da API

A API serve como camada de distribuição dos dados processados.

Ela entrega:

- indicadores executivos;
- resultados por célula;
- leitura territorial por bairro;
- dados geográficos para mapas;
- rankings de áreas críticas.

---

# Base Tecnológica

- Python
- FastAPI
- Pandas
- GeoPandas

---

# Inicialização local

## Executar API

```bash id="v3khw2"
python -m uvicorn backend.api_tuntum:app --reload

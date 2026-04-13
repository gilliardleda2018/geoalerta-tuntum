# API — GeoAlerta Tuntum

Documentação técnica da API principal do projeto GeoAlerta Tuntum.

A API foi desenvolvida para disponibilizar os resultados analíticos do modelo territorial em formato JSON e GeoJSON, permitindo integração com dashboards, aplicação web e futuros sistemas institucionais.

---

## Finalidade da API

A API serve como camada de distribuição dos dados processados do GeoAlerta.

Ela entrega:

- indicadores executivos gerais;
- resultados por célula territorial;
- rankings de áreas críticas;
- consolidação territorial por bairro;
- geometrias em GeoJSON para mapas interativos.

Sua função é transformar os produtos gerados pelo processamento espacial e pela modelagem analítica em respostas acessíveis para consumo por sistemas externos.

---

## Base Tecnológica

A API utiliza:

- Python
- FastAPI
- Pandas
- GeoPandas
- NumPy

---

## Inicialização local

Para executar a API localmente:

```bash
python -m uvicorn backend.api_tuntum:app --reload
## Executar API

```bash id="v3khw2"
python -m uvicorn backend.api_tuntum:app --reload

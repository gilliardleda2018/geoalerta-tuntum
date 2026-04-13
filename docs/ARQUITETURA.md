# Arquitetura do Sistema — GeoAlerta Tuntum

Este documento descreve a arquitetura técnica do projeto GeoAlerta Tuntum, detalhando as camadas funcionais, fluxo dos dados, responsabilidades dos componentes e lógica de integração entre backend, processamento espacial, API e visualização.

---

# Visão Geral da Arquitetura

O GeoAlerta foi concebido como uma arquitetura em camadas.

Cada camada possui responsabilidade específica e comunica-se de forma progressiva até a entrega final da informação territorial.

---

# Modelo Conceitual Geral

```text id="xw6m8q"
Dados geográficos brutos
        ↓
Preparação espacial
        ↓
Geração de células territoriais
        ↓
Cálculo de variáveis ambientais
        ↓
Classificação analítica
        ↓
Consolidação territorial
        ↓
API FastAPI
        ↓
Dashboards técnicos
        ↓
Aplicação web institucional
Camadas do Sistema
Camada 1 — Dados Territoriais

Responsável pelos insumos espaciais utilizados no modelo.

Entradas principais
limites territoriais do município;
bairros;
hidrografia;
raster altimétrico;
áreas vetoriais auxiliares.
Pasta principal
data/
Subpastas relevantes
dados/
saida/
arquivos/
rasters_SRTMGL1/
Função desta camada

Fornecer a base geográfica necessária para todos os cálculos posteriores.

Camada 2 — Processamento Espacial

Responsável pela geração das unidades territoriais de análise.

Principais scripts
extrair_celulas_tuntum.py
score_enchentes_tuntum.py
Responsabilidades
gerar células espaciais;
recortar área municipal;
associar células aos bairros;
calcular indicadores básicos.
Saídas geradas
CSVs intermediários;
camadas geográficas processadas;
GeoPackage consolidado.
Camada 3 — Variáveis Analíticas

Responsável pelo cálculo das variáveis ambientais.

Variáveis centrais
elevação média;
inclinação média;
distância da água;
proxy de chuva.
Resultado desta camada

Cada célula passa a possuir um vetor analítico.

Exemplo conceitual
Célula A:
elevação = 112
inclinação = 1.7
distância água = 85m
proxy chuva = 0.64
Camada 4 — Classificação Territorial

Responsável pela geração do nível de risco.

Script principal
treinar_modelo_ia_tuntum.py
Resultado

Produção de:

score numérico;
classe qualitativa.
Saídas principais
resultado_ia_tuntum.csv
score_enchente_tuntum.gpkg
Camada 5 — Consolidação Territorial por Bairro

Responsável por agregar as células em leitura territorial executiva.

Script principal
dashboard_bairros_tuntum.py
Indicadores produzidos
nível médio de risco;
ponto mais crítico;
percentual crítico;
áreas prioritárias.
Camada 6 — API

Responsável pela distribuição dos dados.

Script principal
api_tuntum.py
Funções principais
servir JSON;
servir GeoJSON;
alimentar frontend;
alimentar dashboards.
Endpoints principais
/api/resumo
/api/riscos
/api/top-criticas
/api/bairros-resumo
/api/geojson-bairros
Camada 7 — Dashboards Técnicos

Responsável pela leitura analítica aprofundada.

Dashboard por células
dashboard_ia_mapa_tuntum.py
Dashboard por bairros
dashboard_bairros_tuntum.py
Objetivo

Permitir:

inspeção técnica;
conferência territorial;
validação espacial.
Camada 8 — Aplicação Web Institucional

Responsável pela leitura simplificada.

Tecnologias
React
Vite
Leaflet
Objetivo

Entregar:

KPIs;
gráficos;
mapa interativo;
leitura didática.
Público-alvo
gestores;
secretarias;
coordenação técnica;
defesa civil.
Fluxo Completo de Operação
Raster + bairros + hidrografia
        ↓
Células espaciais
        ↓
Variáveis ambientais
        ↓
Classificação territorial
        ↓
Score territorial
        ↓
Agrupamento por bairro
        ↓
API
        ↓
WebApp / Dashboards
Estrutura Atual do Projeto
backend/
webapp/
data/
docs/
scripts/
Separação de Responsabilidades
Camada	Responsabilidade
data	insumos
backend	cálculo e API
webapp	interface institucional
docs	documentação
scripts	operação
Benefício Arquitetural

A separação em camadas permite:

manutenção;
expansão;
substituição modular;
evolução gradual.
Possibilidades de Expansão
Curto prazo
integração meteorológica;
alertas automáticos.
Médio prazo
leitura temporal;
histórico comparativo.
Longo prazo
expansão para outros municípios;
regionalização.
Filosofia Arquitetural

O GeoAlerta foi estruturado para transformar análise territorial complexa em instrumento real de decisão pública.

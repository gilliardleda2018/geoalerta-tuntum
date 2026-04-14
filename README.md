# GeoAlerta Tuntum  
### Plataforma Inteligente de Análise Territorial e Prevenção de Enchentes com Geotecnologia e Inteligência Artificial

---

## Apresentação

O **GeoAlerta Tuntum** é uma plataforma desenvolvida para apoiar a gestão pública municipal na identificação, análise e monitoramento de áreas com maior vulnerabilidade a enchentes e alagamentos.

O sistema integra:

- geoprocessamento territorial;
- análise espacial por microcélulas;
- indicadores topográficos;
- proximidade hídrica;
- proxy climático;
- classificação analítica de risco;
- visualização territorial interativa;
- leitura executiva simplificada para gestores.
- Modelo espacial geográfico
- Inteligência Artificial
- Proxy de chuva dinâmica
- Cenários temporais de risco
- Associação territorial por bairros
- Dashboard executivo interativo
A proposta central é transformar dados geográficos complexos em informação estratégica clara, acessível e acionável.

---

# Finalidade do Projeto

A prevenção territorial exige capacidade de antecipação.

Na ausência de leitura espacial detalhada, decisões sobre drenagem, infraestrutura, proteção urbana e resposta emergencial tendem a ser reativas.

O GeoAlerta foi concebido para permitir:

- antecipação territorial;
- leitura objetiva do risco;
- identificação de áreas prioritárias;
- apoio à formulação de políticas públicas;
- fortalecimento da capacidade preventiva municipal.

---

# Problema Público Enfrentado

Eventos extremos de chuva e ocupação territorial inadequada produzem impactos recorrentes em áreas urbanas vulneráveis.

Sem instrumentos analíticos adequados, a gestão depende predominantemente de observação empírica.

O GeoAlerta introduz uma lógica baseada em evidência territorial.

---

# Objetivos Estratégicos

- identificar microáreas vulneráveis;
- classificar risco territorial;
- gerar leitura espacial por bairro;
- apoiar priorização de intervenções;
- permitir leitura simples por autoridades não técnicas;
- integrar ciência de dados à gestão urbana.

---

# Conceito Analítico

O sistema opera em células espaciais menores distribuídas sobre o território municipal.

Cada célula recebe avaliação baseada em variáveis ambientais e espaciais.

---

# Variáveis consideradas

## Elevação média do terreno

Representa a altitude relativa da célula territorial.

Áreas mais baixas tendem a concentrar maior propensão à acumulação hídrica.
# Variáveis Utilizadas no Modelo

## Variáveis espaciais

- Elevação média (`elev_mean`)
- Declividade média (`slope_mean`)
- Distância da drenagem (`dist_water_m`)
- Score espacial composto (`score_0_10`)

## Variável meteorológica dinâmica

- Proxy de chuva (`chuva_proxy`)

Fonte atual:

- OpenWeather API

---

# Integração com Chuva Real

A chuva real é obtida dinamicamente via API:

https://openweathermap.org/

# Arquivo responsável


servico_chuva.py


## Inclinação média do terreno

Indica a capacidade de escoamento superficial.

Terrenos pouco inclinados favorecem retenção hídrica.

---

## Distância média até corpos d’água

Mede proximidade de rios, drenagens e áreas hídricas.

Quanto menor a distância, maior a influência hídrica potencial.

---

## Proxy de chuva

Representa fator estimado de influência pluviométrica sobre o território analisado.

---

## Nível de risco territorial

Resultado consolidado da combinação das variáveis.

---

# Lógica de Funcionamento

Dados territoriais
      ↓
Camadas geográficas
      ↓
Geração de células espaciais
      ↓
Cálculo de variáveis ambientais
      ↓
Classificação analítica
      ↓
Geração de score territorial
      ↓
Classificação do risco
      ↓
API FastAPI
      ↓
Dashboards + Aplicação Web

---

# Variáveis de ambiente (.env)

WEATHER_PROVIDER=openweather
OPENWEATHER_API_KEY=SUA_CHAVE
TUNTUM_LAT=-5.2583
TUNTUM_LON=-44.6489

---

# Atualização Dinâmica do Modelo

# Script principal

atualizar_modelo_com_chuva_dinamica.py

# Função

consulta chuva real
injeta no modelo
recalcula risco IA
salva nova saída
Saída gerada
resultado_ia_tuntum.csv

---
# Cenários Temporais de Chuva

# O sistema permite simular:

Hoje
24h
48h
72h

# Arquivo de entrada manual

dados/chuva_previsao.json

# Script gerador

gerar_cenarios_chuva.py

# Saídas
saida/cenarios/resultado_ia_hoje.csv
saida/cenarios/resultado_ia_24h.csv
saida/cenarios/resultado_ia_48h.csv
saida/cenarios/resultado_ia_72h.csv

---

# Associação Territorial por Bairros

# Cada célula espacial da sede urbana é associada ao bairro correspondente.

# Arquivo de bairros

dados/bairros_tuntum.geojson

# Script

gerar_cenarios_sede_com_bairro.py

# Saídas enriquecidas

resultado_ia_hoje_sede_com_bairro.csv
resultado_ia_24h_sede_com_bairro.csv
resultado_ia_48h_sede_com_bairro.csv
resultado_ia_72h_sede_com_bairro.csv

---

# Dashboard Executivo

#Arquivo principal

dashboard_v5_cenarios_temporais.py

# Funcionalidades

seletor temporal
filtros por bairro
filtros por risco
cards executivos
bairro mais crítico com alerta visual
ranking territorial
mapa interativo
exportação CSV

# Execução
streamlit run dashboard_v5_cenarios_temporais.py

---

# Pipeline Automático

# Arquivo

pipeline_real.bat

# Executa automaticamente

Atualiza chuva real
Recalcula modelo IA
Gera cenários
Associa bairros
Abre dashboard

---

# Estrutura Atual do Projeto

tuntum_enchentes/
│
├── dados/
│   ├── bairros_tuntum.geojson
│   ├── chuva_manual.json
│   └── chuva_previsao.json
│
├── saida/
│   ├── score_enchente_tuntum.gpkg
│   ├── score_enchente_tuntum.csv
│   └── cenarios/
│
├── servico_chuva.py
├── atualizar_modelo_com_chuva_dinamica.py
├── gerar_cenarios_chuva.py
├── gerar_cenarios_sede_com_bairro.py
├── dashboard_v5_cenarios_temporais.py
├── pipeline_real.bat
└── resultado_ia_tuntum.csv

---

# Tecnologias Utilizadas

Python
Pandas
GeoPandas
Streamlit
Folium
Plotly
Scikit-Learn
OpenWeather API

---

# Projeto

GeoAlerta Tuntum
Inteligência Territorial Aplicada à Gestão de Risco

#Autor

Gilliard Léda



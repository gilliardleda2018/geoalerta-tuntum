# GeoAlerta Tuntum

Sistema inteligente de apoio à prevenção de enchentes no município de Tuntum/MA, integrando geotecnologia, análise espacial, indicadores ambientais e inteligência artificial para apoiar a gestão pública na identificação de áreas vulneráveis.

---

# Visão Geral

O GeoAlerta Tuntum foi desenvolvido para transformar dados territoriais em informação estratégica para tomada de decisão.

A plataforma combina:

- análise espacial por células territoriais;
- variáveis topográficas;
- proximidade hídrica;
- proxy climático;
- classificação automática de risco;
- visualização territorial interativa.

O objetivo é permitir que gestores públicos, técnicos e autoridades visualizem de forma clara os pontos de maior vulnerabilidade a enchentes.

---

# Problema que o projeto resolve

Eventos de alagamento e enchentes exigem capacidade de antecipação territorial.

Sem análise espacial detalhada, a tomada de decisão depende apenas de observação empírica.

O GeoAlerta entrega:

- leitura territorial objetiva;
- priorização de áreas críticas;
- apoio ao planejamento preventivo;
- leitura por bairro;
- leitura por microcélulas territoriais.

---

# Objetivos do sistema

- identificar áreas com maior risco territorial;
- consolidar indicadores de vulnerabilidade;
- gerar leitura acessível para gestores;
- disponibilizar mapas interativos;
- apoiar planejamento preventivo municipal.

---

# Arquitetura Geral

```text
Dados territoriais
     ↓
Processamento espacial
     ↓
Geração de células
     ↓
Cálculo de indicadores
     ↓
Modelo analítico / IA
     ↓
Classificação do risco
     ↓
API FastAPI
     ↓
App Web + Dashboards

# Dicionário de Dados — GeoAlerta Tuntum

Este documento descreve todas as principais variáveis utilizadas no projeto GeoAlerta Tuntum, explicando o significado técnico, interpretação territorial e papel analítico de cada campo.

---

# Objetivo do Dicionário de Dados

O GeoAlerta utiliza variáveis territoriais derivadas de geoprocessamento, análise espacial e classificação analítica de risco.

Este documento foi criado para:

- padronizar interpretação;
- facilitar manutenção do projeto;
- permitir leitura por equipes técnicas;
- apoiar leitura por gestores públicos;
- registrar semântica do modelo.

---

# Estrutura das Variáveis

As variáveis podem aparecer em:

- CSVs processados;
- saídas intermediárias;
- GeoJSON;
- respostas da API;
- dashboards;
- aplicação web.

---

# Variáveis Territoriais Principais

---

## elev_mean

### Nome amigável
Elevação média do terreno

### Significado técnico
Representa a altitude média da célula territorial analisada.

### Unidade
metros

### Interpretação territorial
Áreas com menor elevação tendem a apresentar maior suscetibilidade à acumulação hídrica.

### Papel no modelo
É uma das variáveis estruturais mais importantes para avaliação territorial.

---

## slope_mean

### Nome amigável
Inclinação média do terreno

### Significado técnico
Mede a inclinação média da superfície da célula.

### Unidade
graus ou percentual derivado do raster

### Interpretação territorial
Terrenos pouco inclinados favorecem retenção hídrica.

Terrenos com maior inclinação tendem a escoar água mais rapidamente.

### Papel no modelo
Ajuda a estimar comportamento superficial da água.

---

## dist_water_m

### Nome amigável
Distância média até corpos d’água

### Significado técnico
Distância média entre a célula analisada e o corpo hídrico mais próximo.

### Unidade
metros

### Interpretação territorial
Quanto menor a distância, maior a influência potencial de rios, drenagens ou áreas úmidas.

### Papel no modelo
Variável crítica de influência hídrica.

---

## chuva_proxy

### Nome amigável
Indicador de influência de chuva

### Significado técnico
Proxy analítico que representa influência estimada da chuva no território.

### Unidade
índice relativo

### Interpretação territorial
Áreas com maior proxy podem responder mais rapidamente a eventos pluviométricos.

### Papel no modelo
Aproxima comportamento climático na ausência de série histórica integrada.

---

# Variáveis Analíticas de Risco

---

## score_0_10

### Nome amigável
Nível de risco territorial

### Significado técnico
Índice numérico padronizado de 0 a 10.

### Escala

- 0 → risco muito baixo
- 10 → risco muito elevado

### Interpretação territorial
Quanto maior o valor, maior a vulnerabilidade territorial estimada.

### Papel no sistema
É o principal índice sintético do modelo.

---

## risco_previsto

### Nome amigável
Classe de risco territorial

### Significado técnico
Classificação qualitativa derivada do score.

### Classes possíveis

- Muito Baixo
- Baixo
- Moderado
- Alto
- Muito Alto

### Interpretação territorial
Permite leitura executiva simples.

---

## classe_risco

### Nome amigável
Faixa de classificação territorial

### Função
Agrupa células em classes de leitura visual.

### Uso
Mapas e dashboards.

---

# Variáveis Geográficas de Identificação

---

## bairro

### Nome amigável
Bairro

### Função
Indica a qual bairro a célula pertence.

### Uso
Agregação territorial por bairro.

---

## geometry

### Nome amigável
Geometria espacial

### Função
Representa a forma geográfica da célula ou do bairro.

### Uso
Mapas e GeoJSON.

---

## centroid_x

### Nome amigável
Coordenada X

### Função
Longitude do centro da célula.

---

## centroid_y

### Nome amigável
Coordenada Y

### Função
Latitude do centro da célula.

---

# Variáveis Agregadas por Bairro

---

## score_medio

### Nome amigável
Nível médio de risco do bairro

### Significado
Média dos níveis de risco das células do bairro.

---

## score_maximo

### Nome amigável
Ponto mais crítico do bairro

### Significado
Maior valor encontrado entre as células do bairro.

---

## percentual_critico

### Nome amigável
Percentual crítico territorial

### Significado
Percentual do bairro classificado em níveis altos ou muito altos.

---

## qtd_celulas

### Nome amigável
Quantidade de células analisadas

### Significado
Número de microáreas usadas no cálculo territorial.

---

## qtd_altas

### Nome amigável
Áreas com risco alto

### Significado
Quantidade de células classificadas como risco alto.

---

## qtd_muito_altas

### Nome amigável
Áreas com risco muito alto

### Significado
Quantidade de células classificadas como risco muito alto.

---

## dist_media_agua_m

### Nome amigável
Distância média da água no bairro

### Significado
Média da proximidade hídrica das células do bairro.

---

## elev_media

### Nome amigável
Elevação média do bairro

### Significado
Média altimétrica do bairro.

---

## slope_media

### Nome amigável
Inclinação média do bairro

### Significado
Comportamento médio do relevo local.

---

# Campos da API

---

## total_celulas

Quantidade total de células processadas.

---

## maior_nivel_risco

Maior nível de risco encontrado no território.

---

## nivel_medio_risco

Média geral territorial.

---

## risco_dominante

Classe predominante no território analisado.

---

# Observação Técnica

Os nomes internos podem ser mantidos no backend por compatibilidade.

No frontend, recomenda-se uso de nomes amigáveis.

---

# Recomendação de nomenclatura no frontend

| Backend | Frontend |
|--------|----------|
| score_0_10 | nível de risco |
| score_medio | nível médio de risco |
| score_maximo | ponto mais crítico |
| percentual_critico | percentual crítico |
| elev_mean | elevação média |
| slope_mean | inclinação média |
| dist_water_m | distância da água |
| chuva_proxy | influência de chuva |

---

# Finalidade Institucional

Este dicionário permite:

- transparência metodológica;
- rastreabilidade;
- auditabilidade;
- interpretação consistente do sistema.

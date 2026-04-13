import streamlit as st
import pandas as pd

# =========================
# carregar resultado IA
# =========================
df = pd.read_csv("resultado_ia_tuntum.csv")

# =========================
# layout
# =========================
st.set_page_config(layout="wide")

st.title("🧠 Dashboard IA - Risco de Enchentes em Tuntum")

# =========================
# filtros
# =========================
classe = st.selectbox(
    "Selecionar risco:",
    ["Todos"] + list(df["risco_previsto"].unique())
)

if classe != "Todos":
    df = df[df["risco_previsto"] == classe]

# =========================
# tabela
# =========================
st.subheader("Tabela IA")

st.dataframe(
    df[[
        "cell_id",
        "score_0_10",
        "chuva_proxy",
        "risco_previsto"
    ]]
)

# =========================
# métricas
# =========================
st.subheader("Resumo")

col1, col2, col3 = st.columns(3)

col1.metric("Total células", len(df))
col2.metric("Maior score", round(df["score_0_10"].max(),2))
col3.metric("Média score", round(df["score_0_10"].mean(),2))
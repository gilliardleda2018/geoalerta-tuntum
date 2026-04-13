import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# =========================
# 1. Ler CSV real
# =========================
df = pd.read_csv("saida/score_enchente_tuntum.csv")

# =========================
# 2. Simular variável climática real do CPTEC
# hoje = ec = 7
# =========================
df["chuva_proxy"] = 7

# =========================
# 3. Criar classe alvo
# =========================
def classificar(score):
    if score < 4:
        return "Baixa"
    elif score < 6:
        return "Moderada"
    elif score < 8:
        return "Alta"
    else:
        return "Muito Alta"

df["classe_ia"] = df["score_0_10"].apply(classificar)

# =========================
# 4. Variáveis de treino
# =========================
X = df[["elev_mean", "slope_mean", "dist_water_m", "score_0_10", "chuva_proxy"]]
y = df["classe_ia"]

# =========================
# 5. Modelo IA
# =========================
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# =========================
# 6. Previsão
# =========================
df["risco_previsto"] = model.predict(X)

# =========================
# 7. Salvar resultado
# =========================
df.to_csv("resultado_ia_tuntum.csv", index=False)

print("\nModelo treinado com sucesso.")
print("\nTop 10 previsões:")
print(df[["cell_id","score_0_10","chuva_proxy","risco_previsto"]].head(10))
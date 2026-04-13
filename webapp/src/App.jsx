import React, { useEffect, useMemo, useState } from "react";
import {
  ShieldAlert,
  Activity,
  CloudRain,
  MapPinned,
  RefreshCw,
  Search,
  BarChart3,
  Database,
  Siren,
  Info,
  Map,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";

const API_BASE_DEFAULT = "";

const riskColors = {
  Baixa: "#60a5fa",
  Moderada: "#fbbf24",
  Alta: "#fb923c",
  "Muito Alta": "#ef4444",
};

function cardStyle() {
  return {
    background: "white",
    borderRadius: "24px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.06)",
    padding: "20px",
    border: "1px solid #e5e7eb",
  };
}

function sectionTitle(icon, title, subtitle) {
  const Icon = icon;
  return (
    <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
      <div
        style={{
          padding: 12,
          borderRadius: 16,
          background: "#f1f5f9",
          color: "#334155",
        }}
      >
        <Icon size={20} />
      </div>
      <div>
        <h2 style={{ margin: 0, fontSize: 26 }}>{title}</h2>
        <p style={{ margin: "6px 0 0", color: "#475569" }}>{subtitle}</p>
      </div>
    </div>
  );
}

function RiskBadge({ value }) {
  return (
    <span
      style={{
        background: riskColors[value] || "#64748b",
        color: "white",
        padding: "6px 12px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      {value || "Sem classificação"}
    </span>
  );
}

function KpiCard({ title, value, icon: Icon, subtitle }) {
  return (
    <div style={cardStyle()}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 16,
          alignItems: "flex-start",
        }}
      >
        <div>
          <div style={{ color: "#64748b", fontSize: 14 }}>{title}</div>
          <div
            style={{
              fontSize: 38,
              fontWeight: 700,
              marginTop: 8,
              color: "#0f172a",
            }}
          >
            {value}
          </div>
          <div style={{ color: "#64748b", fontSize: 12, marginTop: 8 }}>
            {subtitle}
          </div>
        </div>
        <div
          style={{
            padding: 12,
            borderRadius: 16,
            background: "#e0f2fe",
            color: "#0369a1",
          }}
        >
          <Icon size={20} />
        </div>
      </div>
    </div>
  );
}

function DidacticCard({ title, value, explanation, color = "#f8fafc" }) {
  return (
    <div
      style={{
        background: color,
        border: "1px solid #e2e8f0",
        borderRadius: 18,
        padding: 16,
      }}
    >
      <div style={{ color: "#64748b", fontSize: 13, marginBottom: 6 }}>
        {title}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: "#0f172a" }}>
        {value}
      </div>
      <p style={{ color: "#475569", marginTop: 10, lineHeight: 1.45 }}>
        {explanation}
      </p>
    </div>
  );
}

function getRiskColor(classe) {
  return riskColors[classe] || "#94a3b8";
}

function formatNumber(value, digits = 2) {
  if (value == null || Number.isNaN(Number(value))) return "-";
  return Number(value).toFixed(digits);
}

function getFeatureCenter(feature) {
  const geometry = feature?.geometry;
  if (!geometry) return [-5.321, -44.6];

  if (geometry.type === "Polygon") {
    const ring = geometry.coordinates?.[0] || [];
    const lats = ring.map((c) => c[1]);
    const lngs = ring.map((c) => c[0]);
    const lat = lats.reduce((a, b) => a + b, 0) / (lats.length || 1);
    const lng = lngs.reduce((a, b) => a + b, 0) / (lngs.length || 1);
    return [lat, lng];
  }

  if (geometry.type === "MultiPolygon") {
    const ring = geometry.coordinates?.[0]?.[0] || [];
    const lats = ring.map((c) => c[1]);
    const lngs = ring.map((c) => c[0]);
    const lat = lats.reduce((a, b) => a + b, 0) / (lats.length || 1);
    const lng = lngs.reduce((a, b) => a + b, 0) / (lngs.length || 1);
    return [lat, lng];
  }

  return [-5.321, -44.6];
}

export default function App() {
  const [apiBase, setApiBase] = useState(API_BASE_DEFAULT);
  const [draftApiBase, setDraftApiBase] = useState(API_BASE_DEFAULT);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);
  const [topCriticas, setTopCriticas] = useState([]);
  const [riscos, setRiscos] = useState([]);
  const [geojson, setGeojson] = useState(null);
  const [riskFilter, setRiskFilter] = useState("Todos");
  const [search, setSearch] = useState("");
  const [tab, setTab] = useState("painel");
  const [selectedBairro, setSelectedBairro] = useState("");

  const fetchJson = async (path) => {
    const url = `${apiBase}${path}`;
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Falha em ${path}: ${res.status}`);
    }
    return res.json();
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [summaryData, bairrosData, geojsonData] = await Promise.all([
        fetchJson("/api/resumo"),
        fetchJson("/api/bairros-resumo?limit=100"),
        fetchJson("/api/geojson-bairros?limit=100"),
      ]);

      setSummary(summaryData);
      setTopCriticas(bairrosData);
      setRiscos(bairrosData);
      setGeojson(geojsonData);
    } catch (e) {
      setError(e.message || "Erro ao carregar dados da API.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [apiBase]);

  useEffect(() => {
    if (!selectedBairro && riscos.length > 0) {
      setSelectedBairro(riscos[0].bairro);
    }
  }, [riscos, selectedBairro]);

  const distributionData = useMemo(() => {
    const counts = riscos.reduce((acc, row) => {
      const key = row.classe_bairro || "Sem classificação";
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [riscos]);

  const filteredRows = useMemo(() => {
    return riscos.filter((row) => {
      const riskOk =
        riskFilter === "Todos" || row.classe_bairro === riskFilter;
      const text =
        `${row.bairro} ${row.classe_bairro} ${row.score_medio}`.toLowerCase();
      const searchOk = text.includes(search.toLowerCase());
      return riskOk && searchOk;
    });
  }, [riscos, riskFilter, search]);

  const riskOptions = useMemo(() => {
    const set = new Set(riscos.map((r) => r.classe_bairro).filter(Boolean));
    return ["Todos", ...Array.from(set)];
  }, [riscos]);

  const geojsonStats = useMemo(() => {
    if (!geojson?.features) return { total: 0, preview: [] };
    return {
      total: geojson.features.length,
      preview: geojson.features.slice(0, 8).map((f) => ({
        bairro: f.properties?.bairro,
        classe_bairro: f.properties?.classe_bairro,
        score_medio: f.properties?.score_medio,
      })),
    };
  }, [geojson]);

  const bairrosOptions = useMemo(() => {
    return [...riscos]
      .map((r) => r.bairro)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b));
  }, [riscos]);

  const bairroSelecionadoData = useMemo(() => {
    return riscos.find((r) => r.bairro === selectedBairro) || null;
  }, [riscos, selectedBairro]);

  const chartDataBairro = useMemo(() => {
    if (!bairroSelecionadoData) return [];
    return [
      {
        nome: "Nível médio",
        valor: Number(bairroSelecionadoData.score_medio || 0),
      },
      {
        nome: "Nível máximo",
        valor: Number(bairroSelecionadoData.score_maximo || 0),
      },
      {
        nome: "% crítico",
        valor: Number(bairroSelecionadoData.percentual_critico || 0),
      },
    ];
  }, [bairroSelecionadoData]);

  const leituraExecutiva = useMemo(() => {
    if (!bairroSelecionadoData) return "";

    const classe = bairroSelecionadoData.classe_bairro;
    const critico = Number(bairroSelecionadoData.percentual_critico || 0);
    const nivel = Number(bairroSelecionadoData.score_medio || 0);

    if (classe === "Muito Alta") {
      return `O bairro ${bairroSelecionadoData.bairro} exige atenção imediata. O nível médio de risco está elevado e há forte indício de áreas críticas que merecem prioridade de monitoramento e prevenção.`;
    }

    if (classe === "Alta") {
      return `O bairro ${bairroSelecionadoData.bairro} apresenta risco relevante. É recomendável reforçar o acompanhamento, especialmente em períodos de chuva intensa.`;
    }

    if (classe === "Moderada") {
      return `O bairro ${bairroSelecionadoData.bairro} está em nível intermediário de atenção. O cenário não é o mais crítico, mas já pede vigilância preventiva.`;
    }

    if (critico > 50 || nivel >= 8) {
      return `O bairro ${bairroSelecionadoData.bairro} possui indicadores que sugerem prioridade de observação pelo poder público.`;
    }

    return `O bairro ${bairroSelecionadoData.bairro} apresenta condição relativamente mais estável quando comparado aos mais críticos, mas ainda deve permanecer no radar preventivo.`;
  }, [bairroSelecionadoData]);

  const filteredGeojson = useMemo(() => {
    if (!geojson?.features) return null;

    let features = geojson.features;

    if (riskFilter !== "Todos") {
      features = features.filter(
        (f) => f.properties?.classe_bairro === riskFilter
      );
    }

    if (search.trim()) {
      const term = search.toLowerCase();
      features = features.filter((f) => {
        const p = f.properties || {};
        const text =
          `${p.bairro || ""} ${p.classe_bairro || ""} ${p.score_medio || ""}`.toLowerCase();
        return text.includes(term);
      });
    }

    return {
      ...geojson,
      features,
    };
  }, [geojson, riskFilter, search]);

  const mapCenter = useMemo(() => {
    if (!filteredGeojson?.features?.length) return [-5.321, -44.6];

    const selectedFeature = filteredGeojson.features.find(
      (f) => f.properties?.bairro === selectedBairro
    );

    if (selectedFeature) return getFeatureCenter(selectedFeature);

    return getFeatureCenter(filteredGeojson.features[0]);
  }, [filteredGeojson, selectedBairro]);

  const geoJsonStyle = (feature) => {
    const props = feature?.properties || {};
    const isSelected = props.bairro === selectedBairro;
    const isHighRisk =
      props.classe_bairro === "Alta" || props.classe_bairro === "Muito Alta";

    return {
      fillColor: getRiskColor(props.classe_bairro),
      weight: isSelected ? 4 : isHighRisk ? 3 : 1.2,
      opacity: 1,
      color: isSelected ? "#0f172a" : isHighRisk ? "#7c2d12" : "#334155",
      fillOpacity: isSelected ? 0.9 : 0.72,
      dashArray: isHighRisk ? "6 4" : undefined,
    };
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, #e0f2fe, #f8fafc 40%, #f8fafc)",
        color: "#0f172a",
        padding: 24,
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div
          style={{
            ...cardStyle(),
            padding: 32,
            marginBottom: 24,
            background: "rgba(255,255,255,0.85)",
          }}
        >
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 24,
              justifyContent: "space-between",
            }}
          >
            <div style={{ flex: "1 1 700px" }}>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  background: "#f0f9ff",
                  color: "#075985",
                  border: "1px solid #dbeafe",
                  padding: "10px 16px",
                  borderRadius: 999,
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                <ShieldAlert size={16} />
                Plataforma institucional de apoio à prevenção de enchentes
              </div>

              <h1
                style={{
                  fontSize: 52,
                  margin: "18px 0 0",
                  lineHeight: 1.05,
                }}
              >
                GeoAlerta Tuntum
              </h1>

              <p
                style={{
                  fontSize: 20,
                  color: "#475569",
                  maxWidth: 900,
                  lineHeight: 1.5,
                  marginTop: 16,
                }}
              >
                Aplicação institucional para apresentação do projeto
                desenvolvido no Centro Educa Mais, integrando geoprocessamento,
                clima e inteligência artificial para apoiar a leitura
                territorial de risco de enchentes em Tuntum.
              </p>
            </div>

            <div
              style={{
                flex: "1 1 320px",
                background: "#020617",
                color: "white",
                borderRadius: 24,
                padding: 24,
              }}
            >
              <h3 style={{ marginTop: 0 }}>Conexão com a API</h3>

              <input
                value={draftApiBase}
                onChange={(e) => setDraftApiBase(e.target.value)}
                placeholder="Deixe em branco para usar o proxy do Vite"
                style={{
                  width: "100%",
                  height: 42,
                  borderRadius: 14,
                  border: "none",
                  padding: "0 12px",
                  marginBottom: 12,
                }}
              />

              <div style={{ display: "flex", gap: 8 }}>
                <button
                  onClick={() => setApiBase(draftApiBase)}
                  style={{
                    flex: 1,
                    height: 40,
                    borderRadius: 14,
                    border: "none",
                    background: "#2563eb",
                    color: "white",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Conectar
                </button>

                <button
                  onClick={loadData}
                  disabled={loading}
                  style={{
                    height: 40,
                    width: 44,
                    borderRadius: 14,
                    border: "none",
                    background: "#334155",
                    color: "white",
                    cursor: "pointer",
                  }}
                >
                  <RefreshCw
                    size={16}
                    style={{
                      animation: loading ? "spin 1s linear infinite" : "none",
                    }}
                  />
                </button>
              </div>

              <p style={{ color: "#cbd5e1", fontSize: 14, marginTop: 12 }}>
                API via proxy do Vite:{" "}
                <strong>{apiBase === "" ? "ativa" : apiBase}</strong>
              </p>

              <pre
                style={{
                  background: "#0f172a",
                  border: "1px solid #1e293b",
                  padding: 12,
                  borderRadius: 16,
                  overflow: "auto",
                  fontSize: 12,
                }}
              >
{`python -m uvicorn api_tuntum:app --reload`}
              </pre>
            </div>
          </div>
        </div>

        {error ? (
          <div
            style={{
              background: "#fef2f2",
              border: "1px solid #fecaca",
              color: "#991b1b",
              padding: 16,
              borderRadius: 20,
              marginBottom: 24,
            }}
          >
            <strong>Erro ao carregar dados:</strong> {error}
          </div>
        ) : null}

        <div style={{ marginBottom: 18 }}>
          {sectionTitle(
            BarChart3,
            "Indicadores executivos",
            "Leitura rápida do cenário atual do modelo."
          )}
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: 16,
            marginBottom: 28,
          }}
        >
          <KpiCard
            title="Total de células"
            value={summary?.total_celulas ?? "-"}
            icon={MapPinned}
            subtitle="Microáreas analisadas no território"
          />
          <KpiCard
            title="Maior nível de risco"
            value={summary?.maior_score?.toFixed?.(2) ?? "-"}
            icon={Activity}
            subtitle="Área mais sensível identificada"
          />
          <KpiCard
            title="Nível médio de risco"
            value={summary?.media_score?.toFixed?.(2) ?? "-"}
            icon={CloudRain}
            subtitle="Comportamento médio do território"
          />
          <KpiCard
            title="Risco dominante"
            value={summary?.risco_dominante ?? "-"}
            icon={Siren}
            subtitle="Classe predominante prevista"
          />
        </div>

        <div
          style={{
            display: "flex",
            gap: 8,
            marginBottom: 20,
            flexWrap: "wrap",
          }}
        >
          {[
            ["painel", "Painel executivo"],
            ["analitico", "Analítico"],
            ["integracao", "Integração e API"],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              style={{
                padding: "10px 16px",
                borderRadius: 14,
                border:
                  tab === key
                    ? "1px solid #2563eb"
                    : "1px solid #cbd5e1",
                background: tab === key ? "#eff6ff" : "white",
                color: tab === key ? "#1d4ed8" : "#334155",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === "painel" && (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
                gap: 16,
                marginBottom: 16,
              }}
            >
              <div style={cardStyle()}>
                <h3 style={{ marginTop: 0 }}>Distribuição do risco por bairro</h3>
                <div style={{ width: "100%", height: 360 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={distributionData}
                        dataKey="value"
                        nameKey="name"
                        outerRadius={125}
                        label
                      >
                        {distributionData.map((entry, index) => (
                          <Cell
                            key={index}
                            fill={riskColors[entry.name] || "#94a3b8"}
                          />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div style={cardStyle()}>
                <h3 style={{ marginTop: 0 }}>
                  Top bairros por nível médio de risco
                </h3>
                <div style={{ width: "100%", height: 360 }}>
                  <ResponsiveContainer>
                    <BarChart data={topCriticas}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="bairro" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="score_medio" radius={[10, 10, 0, 0]}>
                        {topCriticas.map((entry, index) => (
                          <Cell
                            key={index}
                            fill={
                              riskColors[entry.classe_bairro] || "#60a5fa"
                            }
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div style={cardStyle()}>
              <h3 style={{ marginTop: 0 }}>Leitura institucional</h3>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: 16,
                }}
              >
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                    padding: 16,
                  }}
                >
                  <strong>Granularidade preservada</strong>
                  <p style={{ color: "#475569", marginBottom: 0 }}>
                    O risco continua sendo calculado em microcélulas, mas agora
                    é apresentado em escala de bairro para facilitar a leitura
                    institucional.
                  </p>
                </div>
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                    padding: 16,
                  }}
                >
                  <strong>Apoio à prevenção</strong>
                  <p style={{ color: "#475569", marginBottom: 0 }}>
                    Bairros com maior nível médio de risco e maior percentual
                    crítico podem orientar ações preventivas e monitoramento.
                  </p>
                </div>
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                    padding: 16,
                  }}
                >
                  <strong>Tradução territorial da IA</strong>
                  <p style={{ color: "#475569", marginBottom: 0 }}>
                    O app apresenta a saída do modelo de IA em linguagem mais
                    compreensível para gestão pública e Defesa Civil.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        {tab === "analitico" && (
          <>
            <div style={{ marginBottom: 16 }}>
              {sectionTitle(
                Database,
                "Tabela analítica por bairro",
                "Consulta rápida dos bairros com filtro por classe, busca textual e leitura didática para gestores."
              )}
            </div>

            <div
              style={{
                display: "flex",
                gap: 12,
                marginBottom: 16,
                flexWrap: "wrap",
                alignItems: "center",
              }}
            >
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                style={{
                  height: 42,
                  borderRadius: 14,
                  border: "1px solid #cbd5e1",
                  padding: "0 12px",
                  background: "white",
                }}
              >
                {riskOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>

              <div style={{ position: "relative" }}>
                <Search
                  size={16}
                  style={{
                    position: "absolute",
                    left: 12,
                    top: 13,
                    color: "#94a3b8",
                  }}
                />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Buscar bairro, classe ou nível de risco"
                  style={{
                    height: 42,
                    borderRadius: 14,
                    border: "1px solid #cbd5e1",
                    padding: "0 12px 0 34px",
                    minWidth: 280,
                    background: "white",
                  }}
                />
              </div>

              <select
                value={selectedBairro}
                onChange={(e) => setSelectedBairro(e.target.value)}
                style={{
                  height: 42,
                  borderRadius: 14,
                  border: "1px solid #cbd5e1",
                  padding: "0 12px",
                  background: "white",
                  minWidth: 240,
                }}
              >
                {bairrosOptions.map((bairro) => (
                  <option key={bairro} value={bairro}>
                    {bairro}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ ...cardStyle(), marginBottom: 16 }}>
              <h3 style={{ marginTop: 0 }}>Mapa interativo por bairro</h3>
              <p style={{ color: "#475569", marginBottom: 16, lineHeight: 1.6 }}>
                O mapa mostra os bairros coloridos pelo nível de risco. Ao clicar
                em um bairro, ele fica destacado e os painéis abaixo passam a
                explicar os indicadores daquela área em linguagem simples.
              </p>

              <div
                style={{
                  display: "flex",
                  gap: 12,
                  flexWrap: "wrap",
                  marginBottom: 16,
                }}
              >
                <button
                  onClick={() => setRiskFilter("Alta")}
                  style={{
                    padding: "10px 14px",
                    borderRadius: 12,
                    border: "1px solid #fed7aa",
                    background: riskFilter === "Alta" ? "#fff7ed" : "white",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  Marcar bairros de risco alto
                </button>

                <button
                  onClick={() => setRiskFilter("Muito Alta")}
                  style={{
                    padding: "10px 14px",
                    borderRadius: 12,
                    border: "1px solid #fecaca",
                    background:
                      riskFilter === "Muito Alta" ? "#fef2f2" : "white",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  Marcar bairros de risco muito alto
                </button>

                <button
                  onClick={() => setRiskFilter("Todos")}
                  style={{
                    padding: "10px 14px",
                    borderRadius: 12,
                    border: "1px solid #cbd5e1",
                    background: riskFilter === "Todos" ? "#eff6ff" : "white",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  Mostrar todos
                </button>
              </div>

              <div
                style={{
                  height: 620,
                  borderRadius: 20,
                  overflow: "hidden",
                  border: "1px solid #e2e8f0",
                }}
              >
                {filteredGeojson?.features?.length ? (
                  <MapContainer
                    center={mapCenter}
                    zoom={12}
                    style={{ height: "100%", width: "100%" }}
                  >
                    <TileLayer
                      attribution='&copy; OpenStreetMap contributors & CartoDB'
                      url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                    />

                    <GeoJSON
                      data={filteredGeojson}
                      style={geoJsonStyle}
                      onEachFeature={(feature, layer) => {
                        const p = feature.properties || {};

                        layer.on({
                          click: () => {
                            setSelectedBairro(p.bairro || "");
                            setTab("analitico");
                          },
                        });

                        layer.bindTooltip(
                          `
                            <div style="min-width:220px">
                              <strong>Bairro:</strong> ${p.bairro || "-"}<br/>
                              <strong>Classe:</strong> ${p.classe_bairro || "-"}<br/>
                              <strong>Nível médio de risco:</strong> ${formatNumber(p.score_medio)}<br/>
                              <strong>Nível máximo de risco:</strong> ${formatNumber(p.score_maximo)}<br/>
                              <strong>Percentual crítico:</strong> ${formatNumber(p.percentual_critico)}%<br/>
                              <strong>Qtd. de células:</strong> ${p.qtd_celulas ?? "-"}<br/>
                              <strong>Áreas com risco alto:</strong> ${p.qtd_altas ?? "-"}<br/>
                              <strong>Áreas com risco muito alto:</strong> ${p.qtd_muito_altas ?? "-"}<br/>
                              <strong>Distância média da água:</strong> ${
                                p.dist_media_agua_m != null
                                  ? `${formatNumber(p.dist_media_agua_m, 0)} m`
                                  : "-"
                              }
                            </div>
                          `,
                          { sticky: true }
                        );
                      }}
                    />
                  </MapContainer>
                ) : (
                  <div
                    style={{
                      height: "100%",
                      display: "grid",
                      placeItems: "center",
                      color: "#64748b",
                    }}
                  >
                    Nenhum bairro disponível para o filtro atual.
                  </div>
                )}
              </div>
            </div>

            <div style={{ ...cardStyle(), padding: 0, marginBottom: 16 }}>
              <div
                style={{
                  overflow: "auto",
                  maxHeight: 560,
                  borderRadius: 24,
                }}
              >
                <table
                  style={{
                    width: "100%",
                    fontSize: 14,
                    borderCollapse: "collapse",
                  }}
                >
                  <thead
                    style={{
                      background: "#f1f5f9",
                      position: "sticky",
                      top: 0,
                    }}
                  >
                    <tr>
                      <th style={{ textAlign: "left", padding: 16 }}>Bairro</th>
                      <th style={{ textAlign: "left", padding: 16 }}>
                        Nível médio de risco
                      </th>
                      <th style={{ textAlign: "left", padding: 16 }}>Classe</th>
                      <th style={{ textAlign: "left", padding: 16 }}>
                        % crítico
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRows.map((row) => (
                      <tr
                        key={row.bairro}
                        onClick={() => setSelectedBairro(row.bairro)}
                        style={{
                          borderTop: "1px solid #f1f5f9",
                          background:
                            selectedBairro === row.bairro ? "#eff6ff" : "white",
                          cursor: "pointer",
                        }}
                      >
                        <td style={{ padding: 16, fontWeight: 600 }}>
                          {row.bairro}
                        </td>
                        <td style={{ padding: 16 }}>
                          {Number(row.score_medio).toFixed(2)}
                        </td>
                        <td style={{ padding: 16 }}>
                          <RiskBadge value={row.classe_bairro} />
                        </td>
                        <td style={{ padding: 16 }}>
                          {Number(row.percentual_critico).toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {bairroSelecionadoData && (
              <>
                <div style={{ marginBottom: 16 }}>
                  {sectionTitle(
                    Info,
                    `Leitura didática do bairro: ${bairroSelecionadoData.bairro}`,
                    "Explicação simples dos indicadores para apoio à decisão de gestores e autoridades."
                  )}
                </div>

                <div
                  style={{
                    ...cardStyle(),
                    marginBottom: 16,
                    background: "#f8fafc",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: 12,
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div>
                      <div style={{ color: "#64748b", fontSize: 14 }}>
                        Bairro selecionado
                      </div>
                      <div
                        style={{
                          fontSize: 30,
                          fontWeight: 700,
                          marginTop: 6,
                        }}
                      >
                        {bairroSelecionadoData.bairro}
                      </div>
                    </div>
                    <RiskBadge value={bairroSelecionadoData.classe_bairro} />
                  </div>

                  <p
                    style={{
                      color: "#334155",
                      marginTop: 16,
                      lineHeight: 1.6,
                      fontSize: 16,
                    }}
                  >
                    {leituraExecutiva}
                  </p>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(320px, 1.1fr) minmax(320px, 1fr)",
                    gap: 16,
                    marginBottom: 16,
                  }}
                >
                  <div style={cardStyle()}>
                    <h3 style={{ marginTop: 0 }}>
                      Gráfico explicativo do bairro
                    </h3>
                    <p style={{ color: "#475569", marginBottom: 16 }}>
                      Este gráfico resume três sinais importantes: o nível médio
                      de risco do bairro, o pior ponto identificado e o
                      percentual de áreas críticas.
                    </p>
                    <div style={{ width: "100%", height: 340 }}>
                      <ResponsiveContainer>
                        <BarChart data={chartDataBairro}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="nome" />
                          <YAxis />
                          <RechartsTooltip />
                          <Bar dataKey="valor" radius={[10, 10, 0, 0]}>
                            {chartDataBairro.map((entry, index) => (
                              <Cell
                                key={index}
                                fill={
                                  entry.nome === "% crítico"
                                    ? "#8b5cf6"
                                    : riskColors[bairroSelecionadoData.classe_bairro] || "#60a5fa"
                                }
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div style={cardStyle()}>
                    <h3 style={{ marginTop: 0 }}>Como interpretar</h3>
                    <div style={{ display: "grid", gap: 12 }}>
                      <div
                        style={{
                          background: "#f8fafc",
                          border: "1px solid #e2e8f0",
                          borderRadius: 18,
                          padding: 14,
                        }}
                      >
                        <strong>Nível médio de risco</strong>
                        <p style={{ color: "#475569", marginTop: 8 }}>
                          É a média do risco do bairro como um todo. Quanto maior
                          esse valor, maior a preocupação geral com enchentes na
                          área.
                        </p>
                      </div>

                      <div
                        style={{
                          background: "#f8fafc",
                          border: "1px solid #e2e8f0",
                          borderRadius: 18,
                          padding: 14,
                        }}
                      >
                        <strong>Nível máximo de risco</strong>
                        <p style={{ color: "#475569", marginTop: 8 }}>
                          Mostra o ponto mais crítico encontrado dentro do bairro.
                          Mesmo que a média não seja tão alta, esse valor revela
                          se há bolsões de maior perigo.
                        </p>
                      </div>

                      <div
                        style={{
                          background: "#f8fafc",
                          border: "1px solid #e2e8f0",
                          borderRadius: 18,
                          padding: 14,
                        }}
                      >
                        <strong>% crítico</strong>
                        <p style={{ color: "#475569", marginTop: 8 }}>
                          Indica quanto do bairro está em situação preocupante.
                          Quanto maior esse percentual, maior a área que merece
                          atenção prioritária.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                    gap: 16,
                    marginBottom: 16,
                  }}
                >
                  <DidacticCard
                    title="Nível médio de risco"
                    value={Number(bairroSelecionadoData.score_medio || 0).toFixed(2)}
                    explanation="Resume o risco médio do bairro. É um termômetro geral: quanto maior, mais preocupante é a situação média da área."
                    color="#eff6ff"
                  />

                  <DidacticCard
                    title="Nível máximo de risco"
                    value={Number(bairroSelecionadoData.score_maximo || 0).toFixed(2)}
                    explanation="Representa o pior ponto encontrado dentro do bairro. Ajuda a localizar locais que podem exigir resposta mais rápida."
                    color="#fff7ed"
                  />

                  <DidacticCard
                    title="% crítico"
                    value={`${Number(
                      bairroSelecionadoData.percentual_critico || 0
                    ).toFixed(2)}%`}
                    explanation="Mostra a fatia do bairro que está em condição crítica. É útil para entender se o problema é pontual ou espalhado."
                    color="#faf5ff"
                  />

                  <DidacticCard
                    title="Quantidade de células"
                    value={bairroSelecionadoData.qtd_celulas ?? "-"}
                    explanation="É a quantidade de pequenas áreas analisadas dentro do bairro. Quanto mais células, mais detalhada foi a leitura territorial."
                  />

                  <DidacticCard
                    title="Áreas com risco alto"
                    value={bairroSelecionadoData.qtd_altas ?? "-"}
                    explanation="Mostra quantas microáreas do bairro já entraram na faixa de risco alto. Serve para dimensionar a atenção preventiva."
                  />

                  <DidacticCard
                    title="Áreas com risco muito alto"
                    value={bairroSelecionadoData.qtd_muito_altas ?? "-"}
                    explanation="Indica quantas microáreas atingiram o nível mais grave do modelo. São os pontos com maior prioridade de observação."
                    color="#fef2f2"
                  />

                  <DidacticCard
                    title="Distância média da água"
                    value={
                      bairroSelecionadoData.dist_media_agua_m != null
                        ? `${Number(bairroSelecionadoData.dist_media_agua_m).toFixed(0)} m`
                        : "-"
                    }
                    explanation="Mostra o quão perto, em média, o bairro está de rios, córregos ou drenagens. Quanto menor essa distância, maior tende a ser a sensibilidade à água."
                  />

                  <DidacticCard
                    title="Elevação média"
                    value={
                      bairroSelecionadoData.elev_media != null
                        ? Number(bairroSelecionadoData.elev_media).toFixed(2)
                        : "-"
                    }
                    explanation="Indica a altura média do terreno. Em geral, áreas mais baixas podem acumular água com maior facilidade."
                  />

                  <DidacticCard
                    title="Inclinação média"
                    value={
                      bairroSelecionadoData.slope_media != null
                        ? Number(bairroSelecionadoData.slope_media).toFixed(4)
                        : "-"
                    }
                    explanation="Mostra o quanto o terreno é inclinado. Terrenos muito planos tendem a reter água; terrenos com maior inclinação facilitam o escoamento."
                  />
                </div>

                <div style={cardStyle()}>
                  <h3 style={{ marginTop: 0 }}>Síntese para autoridade leiga</h3>
                  <p style={{ color: "#475569", lineHeight: 1.7 }}>
                    Em termos práticos, este painel responde três perguntas:
                    <strong> qual é o nível geral de risco do bairro</strong>,
                    <strong> onde estão os pontos mais sensíveis</strong> e
                    <strong> quanto do bairro exige atenção</strong>. Assim, uma
                    autoridade pode entender rapidamente se a área precisa de
                    monitoramento rotineiro, reforço preventivo ou ação mais
                    imediata em períodos de chuva forte.
                  </p>
                </div>
              </>
            )}
          </>
        )}

        {tab === "integracao" && (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
                gap: 16,
                marginBottom: 16,
              }}
            >
              <div style={cardStyle()}>
                <h3 style={{ marginTop: 0 }}>Integração com aplicativos</h3>
                <p style={{ color: "#475569" }}>
                  O app institucional consome os dados do modelo por API. Agora,
                  além dos indicadores gerais, ele também trabalha com a leitura
                  territorial por bairro.
                </p>
                <div
                  style={{
                    marginTop: 12,
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                    padding: 16,
                  }}
                >
                  <strong>Endpoints principais</strong>
                  <ul style={{ marginBottom: 0, color: "#475569" }}>
                    <li>/api/resumo</li>
                    <li>/api/bairros-resumo</li>
                    <li>/api/geojson-bairros</li>
                  </ul>
                </div>

                <pre
                  style={{
                    background: "#020617",
                    color: "#e2e8f0",
                    padding: 16,
                    borderRadius: 18,
                    overflow: "auto",
                    fontSize: 12,
                    marginTop: 16,
                  }}
                >
{`fetch("/api/bairros-resumo")
  .then(res => res.json())
  .then(data => console.log(data));`}
                </pre>
              </div>

              <div style={cardStyle()}>
                <h3 style={{ marginTop: 0 }}>Prévia dos dados do mapa</h3>
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                    padding: 16,
                    marginBottom: 16,
                  }}
                >
                  <div style={{ color: "#64748b", fontSize: 14 }}>
                    Total de bairros no GeoJSON
                  </div>
                  <div
                    style={{ fontSize: 36, fontWeight: 700, marginTop: 6 }}
                  >
                    {geojsonStats.total}
                  </div>
                </div>

                <div
                  style={{
                    overflow: "auto",
                    maxHeight: 260,
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                  }}
                >
                  <table
                    style={{
                      width: "100%",
                      fontSize: 14,
                      borderCollapse: "collapse",
                    }}
                  >
                    <thead style={{ background: "#f1f5f9" }}>
                      <tr>
                        <th style={{ textAlign: "left", padding: 12 }}>Bairro</th>
                        <th style={{ textAlign: "left", padding: 12 }}>
                          Nível médio de risco
                        </th>
                        <th style={{ textAlign: "left", padding: 12 }}>Classe</th>
                      </tr>
                    </thead>
                    <tbody>
                      {geojsonStats.preview.map((row) => (
                        <tr
                          key={row.bairro}
                          style={{ borderTop: "1px solid #f1f5f9" }}
                        >
                          <td style={{ padding: 12 }}>{row.bairro}</td>
                          <td style={{ padding: 12 }}>
                            {Number(row.score_medio).toFixed(2)}
                          </td>
                          <td style={{ padding: 12 }}>
                            <RiskBadge value={row.classe_bairro} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div style={cardStyle()}>
              <h3 style={{ marginTop: 0 }}>
                Mensagem institucional do projeto
              </h3>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                  gap: 16,
                }}
              >
                <div
                  style={{
                    background: "#f0f9ff",
                    border: "1px solid #dbeafe",
                    borderRadius: 18,
                    padding: 18,
                  }}
                >
                  <strong>Valor público</strong>
                  <p style={{ color: "#475569", marginBottom: 0 }}>
                    O projeto transforma dados territoriais e meteorológicos em
                    inteligência preventiva para apoiar monitoramento,
                    planejamento e proteção da comunidade.
                  </p>
                </div>
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 18,
                    padding: 18,
                  }}
                >
                  <strong>Valor educacional</strong>
                  <p style={{ color: "#475569", marginBottom: 0 }}>
                    A solução nasce no ambiente escolar, aproximando educação,
                    ciência de dados, geotecnologia e impacto social concreto.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
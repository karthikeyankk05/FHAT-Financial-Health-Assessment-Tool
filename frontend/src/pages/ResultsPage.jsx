import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function ResultsPage() {
  const [analysis, setAnalysis] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const data = localStorage.getItem("analysis");
    if (data) {
      setAnalysis(JSON.parse(data));
    } else {
      navigate("/");
    }
  }, [navigate]);

  if (!analysis) return <p className="loading">Loading...</p>;

  return (
    <div className="dashboard-container">
      <h1 className="page-title">Financial Overview</h1>

      <div className="grid">
        <Card
          title="Risk Score"
          value={analysis?.risk?.score ?? 0}
          subtitle={analysis?.risk?.category ?? ""}
        />
        <Card
          title="Investor Readiness"
          value={analysis?.investor?.score ?? 0}
          subtitle={analysis?.investor?.category ?? ""}
        />
        <Card
          title="ESG Score"
          value={analysis?.esg?.score ?? 0}
          subtitle={analysis?.esg?.category ?? ""}
        />
        <Card title="Survival Score" value={analysis?.survival_score ?? 0} />
      </div>

      <div className="grid">
        <Card
          title="Net Cash Flow"
          value={analysis?.cashflow?.net_cash_flow ?? 0}
          subtitle={analysis?.cashflow?.liquidity_status ?? ""}
        />
        <Card
          title="Working Capital"
          value={analysis?.working_capital?.working_capital ?? 0}
          subtitle={analysis?.working_capital?.status ?? ""}
        />
        <Card
          title="Compliance Score"
          value={analysis?.compliance?.compliance_score ?? 0}
        />
        <Card
          title="Industry Percentile"
          value={`${analysis?.benchmarking?.percentile_rank ?? 0}%`}
        />
      </div>

      <div className="section-card">
        <h2>Product Recommendation</h2>
        <p>{analysis?.product_recommendations?.recommended_product ?? "N/A"}</p>
        <small>{analysis?.product_recommendations?.reason ?? ""}</small>
      </div>

      <div className="section-card">
        <h2>Forecast</h2>
        <p>
          Revenue:{" "}
          {analysis?.forecast?.next_revenue_forecast ?? 0}
        </p>
        <p>
          Expenses:{" "}
          {analysis?.forecast?.next_expense_forecast ?? 0}
        </p>
      </div>

      <div className="section-card">
        <h2>AI CFO Summary</h2>
        <p>{analysis?.ai_summary ?? ""}</p>
      </div>
    </div>
  );
}

function Card({ title, value, subtitle }) {
  return (
    <div className="glass-card">
      <h3>{title}</h3>
      <h2>{value}</h2>
      {subtitle && <p className="sub">{subtitle}</p>}
    </div>
  );
}

export default ResultsPage;

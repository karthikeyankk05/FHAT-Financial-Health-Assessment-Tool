import React, { useEffect, useState } from "react";
import { analyzeBusiness } from "../api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function Dashboard() {
  const [data, setData] = useState(null);
  const businessId = 1;

  useEffect(() => {
    async function fetchData() {
      const res = await analyzeBusiness(businessId);
      setData(res);
    }
    fetchData();
  }, []);

  if (!data) return <div className="loading">Analyzing Financial Data...</div>;

  const forecastData =
    data.forecast?.revenue_forecast?.future?.map((item) => ({
      period: item.period,
      revenue: item.value,
    })) || [];

  return (
    <div className="dashboard">

      {/* METRIC GRID */}
      <div className="metric-grid">

        <MetricCard title="Risk Score" value={data.risk?.score} subtitle={data.risk?.category} />
        <MetricCard title="Investor Readiness" value={data.investor?.score} subtitle={data.investor?.category} />
        <MetricCard title="ESG Score" value={data.esg?.score} subtitle={data.esg?.category} />
        <MetricCard title="Survival Score" value={data.survival_score} />

        <MetricCard title="Net Cash Flow" value={data.cashflow?.net_cash_flow} />
        <MetricCard title="Working Capital" value={data.working_capital?.working_capital} />
        <MetricCard title="Compliance Score" value={data.compliance?.compliance_score} />
        <MetricCard title="Industry Percentile" value={`${data.benchmarking?.industry_percentile || 0}%`} />

      </div>

      {/* FORECAST CHART */}
      <div className="card large-card">
        <h2>Revenue Forecast</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecastData}>
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* PRODUCT RECOMMENDATIONS */}
      <div className="card">
        <h2>Product Recommendations</h2>
        {data.product_recommendations?.length > 0 ? (
          data.product_recommendations.map((p, index) => (
            <div key={index} className="product-card">
              {p.name || JSON.stringify(p)}
            </div>
          ))
        ) : (
          <p>No suitable financial products recommended.</p>
        )}
      </div>

      {/* AI SUMMARY */}
      <div className="card ai-card">
        <h2>AI CFO Summary</h2>
        <pre>{data.ai_summary}</pre>
      </div>

    </div>
  );
}

function MetricCard({ title, value, subtitle }) {
  return (
    <div className="metric-card">
      <h4>{title}</h4>
      <h2>{value}</h2>
      {subtitle && <p>{subtitle}</p>}
    </div>
  );
}

export default Dashboard;

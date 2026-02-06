import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

function FinancialTrendChart({ metrics }) {

  // Simulated historical data for demo
  const data = [
    { name: "Q1", revenue: metrics.gross_margin - 5 },
    { name: "Q2", revenue: metrics.gross_margin - 2 },
    { name: "Q3", revenue: metrics.gross_margin },
    { name: "Q4", revenue: metrics.gross_margin + 3 },
  ];

  return (
    <div className="chart-container">
      <h3>Financial Trend (Gross Margin)</h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#3b82f6"
            strokeWidth={3}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default FinancialTrendChart;

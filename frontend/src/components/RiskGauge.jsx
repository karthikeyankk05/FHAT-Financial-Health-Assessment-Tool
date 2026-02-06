import React from "react";
import { RadialBarChart, RadialBar, Legend } from "recharts";

function RiskGauge({ score, category }) {
  const data = [
    {
      name: "Risk",
      value: score,
      fill:
        score >= 750
          ? "#28a745"
          : score >= 600
          ? "#fd7e14"
          : "#dc3545",
    },
  ];

  return (
    <div className="gauge-card">
      <h3>Risk Score</h3>

      <RadialBarChart
        width={300}
        height={250}
        cx="50%"
        cy="100%"
        innerRadius="80%"
        outerRadius="100%"
        barSize={20}
        data={data}
        startAngle={180}
        endAngle={0}
      >
        <RadialBar
          minAngle={15}
          background
          clockWise
          dataKey="value"
          cornerRadius={10}
        />
      </RadialBarChart>

      <h2
        style={{
          color:
            score >= 750
              ? "#28a745"
              : score >= 600
              ? "#fd7e14"
              : "#dc3545",
        }}
      >
        {score}
      </h2>

      <p>{category}</p>
    </div>
  );
}

export default RiskGauge;

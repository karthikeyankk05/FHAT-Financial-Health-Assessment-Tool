import React from "react";
import { RadialBarChart, RadialBar } from "recharts";

function SurvivalGauge({ score }) {
  const data = [
    {
      name: "Survival",
      value: score,
      fill:
        score >= 70
          ? "#28a745"
          : score >= 50
          ? "#fd7e14"
          : "#dc3545",
    },
  ];

  return (
    <div className="gauge-card">
      <h3>Business Survival Score</h3>

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
            score >= 70
              ? "#28a745"
              : score >= 50
              ? "#fd7e14"
              : "#dc3545",
        }}
      >
        {score}
      </h2>

      <p>
        {score >= 70
          ? "Stable"
          : score >= 50
          ? "Watch Closely"
          : "High Risk"}
      </p>
    </div>
  );
}

export default SurvivalGauge;

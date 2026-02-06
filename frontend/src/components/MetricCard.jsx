import React from "react";

function MetricCard({ title, value, suffix = "", color = "blue" }) {
  return (
    <div className={`metric-card ${color}`}>
      <h4>{title}</h4>
      <h2>
        {value}
        {suffix}
      </h2>
    </div>
  );
}

export default MetricCard;

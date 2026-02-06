import React from "react";

function ESGCard({ esg }) {
  if (!esg) return null;

  const { score, category, breakdown } = esg;

  const getColor = () => {
    if (score >= 80) return "#22c55e";   // Green
    if (score >= 65) return "#3b82f6";   // Blue
    if (score >= 50) return "#f59e0b";   // Orange
    return "#ef4444";                    // Red
  };

  return (
    <div className="esg-card">
      <h3>ESG Sustainability Score</h3>

      <div className="esg-score" style={{ color: getColor() }}>
        {score}
      </div>

      <p className="esg-category">{category}</p>

      {breakdown && (
        <div className="esg-breakdown">
          <div>
            <strong>Environmental:</strong> {breakdown.environmental}
          </div>
          <div>
            <strong>Social:</strong> {breakdown.social}
          </div>
          <div>
            <strong>Governance:</strong> {breakdown.governance}
          </div>
        </div>
      )}
    </div>
  );
}

export default ESGCard;

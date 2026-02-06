import React from "react";

function AISummary({ summary }) {
  if (!summary) return null;

  return (
    <div className="ai-summary card">
      <h3>AI CFO Executive Summary</h3>

      <div className="ai-content">
        {summary.split("\n").map((line, index) => (
          <p key={index}>{line}</p>
        ))}
      </div>
    </div>
  );
}

export default AISummary;

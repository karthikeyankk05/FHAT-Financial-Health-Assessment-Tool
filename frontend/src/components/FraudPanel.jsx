import React from "react";

function FraudPanel({ fraud }) {
  if (!fraud || fraud.length === 0) {
    return (
      <div className="fraud-panel card">
        <h3>Fraud Detection</h3>
        <p style={{ color: "#22c55e" }}>
          ✅ No fraud risks detected
        </p>
      </div>
    );
  }

  const getSeverityColor = (severity) => {
    if (severity === "Critical") return "#ef4444";
    if (severity === "High") return "#dc2626";
    if (severity === "Medium") return "#f59e0b";
    return "#3b82f6";
  };

  return (
    <div className="fraud-panel card">
      <h3>Fraud & Anomaly Alerts</h3>

      {fraud.map((flag, index) => (
        <div
          key={index}
          className="fraud-alert"
          style={{
            borderLeft: `6px solid ${getSeverityColor(flag.severity)}`,
          }}
        >
          <div className="fraud-header">
            <strong>{flag.type}</strong>
            <span
              className="fraud-severity"
              style={{
                backgroundColor: getSeverityColor(flag.severity),
              }}
            >
              {flag.severity}
            </span>
          </div>

          <p>{flag.message || flag.description}</p>
        </div>
      ))}
    </div>
  );
}

export default FraudPanel;

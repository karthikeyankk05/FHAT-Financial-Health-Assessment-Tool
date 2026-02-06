import React from "react";

function WarningPanel({ warnings }) {
  if (!warnings || warnings.length === 0) {
    return (
      <div className="warning-panel card">
        <h3>Early Warning System</h3>
        <p style={{ color: "#22c55e" }}>
          ✅ No active financial warnings
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
    <div className="warning-panel card">
      <h3>Early Warning Alerts</h3>

      {warnings.map((warn, index) => (
        <div
          key={index}
          className="warning-alert"
          style={{
            borderLeft: `6px solid ${getSeverityColor(warn.severity)}`,
          }}
        >
          <div className="warning-header">
            <strong>{warn.type}</strong>
            <span
              className="warning-severity"
              style={{
                backgroundColor: getSeverityColor(warn.severity),
              }}
            >
              {warn.severity}
            </span>
          </div>

          <p>{warn.message || warn.description}</p>
        </div>
      ))}
    </div>
  );
}

export default WarningPanel;

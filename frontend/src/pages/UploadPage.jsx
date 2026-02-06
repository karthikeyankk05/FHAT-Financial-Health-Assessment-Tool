import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile, runAnalysis } from "../api";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const businessId = 1;

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file.");
      return;
    }

    setLoading(true);

    try {
      await uploadFile(businessId, file);
      const res = await runAnalysis(businessId);

      localStorage.setItem("analysis", JSON.stringify(res.data));
      navigate("/results");
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Upload or analysis failed.";
      alert(detail);
    }

    setLoading(false);
  };

  return (
    <div className="center-screen">
      <div className="glass-card upload-card">
        <h1 className="logo">FHAT</h1>
        <p className="subtitle">AI Financial Intelligence Platform</p>

        <input
          type="file"
          accept=".csv,.xlsx"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Processing..." : "Analyze Business"}
        </button>
      </div>
    </div>
  );
}

export default UploadPage;

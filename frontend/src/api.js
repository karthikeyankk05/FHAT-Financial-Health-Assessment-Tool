import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Upload file
export const uploadFile = async (businessId, file) => {
  const formData = new FormData();
  formData.append("file", file);

  return API.post(`/upload/${businessId}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// Full analysis
export const runAnalysis = async (businessId) => {
  return API.post(`/analyze/${businessId}`);
};

export default API;

import axios from "axios";

export async function fetchResults(runId) {
  const res = await axios.get(`http://localhost:8000/results/${runId}`, {
    headers: { "X-API-Key": "mydevkey" },
  });
  return res.data;
}

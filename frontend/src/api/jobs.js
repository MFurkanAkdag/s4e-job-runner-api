import client from "./client";

// Backend health kontrolü
export const getHealth = async () => {
  const res = await client.get("/health");
  return res.data;
};

// Job run listesini getir
export const getJobRuns = async () => {
  const res = await client.get("/job-runs");
  return res.data;
};

// Belirli job’un sonuçlarını getir
export const getResults = async (runId) => {
  const res = await client.get(`/results/${runId}`);
  return res.data;
};

// OS job tetikle
export const triggerOsJob = async (payload) => {
  const res = await client.post("/jobs/os", payload);
  return res.data;
};

// Katana job tetikle
export const triggerKatanaJob = async (payload) => {
  const res = await client.post("/jobs/katana", payload);
  return res.data;
};

export const fetchResults = async () => {
  const res = await client.get("/results");
  return res.data;
};
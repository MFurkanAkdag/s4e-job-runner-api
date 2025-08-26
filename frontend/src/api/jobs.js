import client from "./client";

// Backend health kontrolü
export const getHealth = async () => {
  const res = await client.get("/health");
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

// Job run listesini getir (pagination + filtreleme destekli)
export const getJobRuns = async ({ limit = 10, offset = 0, status, job_type } = {}) => {
  const res = await client.get("/job-runs", {
    params: { limit, offset, status, job_type },
  });
  return res.data;
};
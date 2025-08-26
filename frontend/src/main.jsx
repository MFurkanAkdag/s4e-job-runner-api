import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";
import JobsPage from "./features/jobs/JobsPage";
import ResultsPage from "./features/results/ResultsPage";
import HealthCheck from "./features/health/HealthCheck";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route path="jobs" element={<JobsPage />} />
            <Route path="results" element={<ResultsPage />} />
            <Route path="results/:runId" element={<ResultsPage />} />
            <Route path="health" element={<HealthCheck />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);

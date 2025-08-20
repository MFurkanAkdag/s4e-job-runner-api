// src/features/results/ResultsPage.jsx
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { fetchResults } from "../../api/results";
import ResultsTable from "./ResultsTable";

function ResultsPage() {
  const { runId } = useParams();
  const { data, error, isLoading } = useQuery({
    queryKey: ["results", runId],
    queryFn: () => fetchResults(runId),
    enabled: !!runId,
  });

  if (!runId) return <div>Bir job seçilmedi.</div>;
  if (isLoading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata oluştu, sonuçlar alınamadı.</div>;

  return (
    <div>
      <h2>Sonuçlar (Run ID: {runId})</h2>
      <ResultsTable rows={data} />
    </div>
  );
}

export default ResultsPage;

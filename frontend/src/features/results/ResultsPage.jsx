import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { fetchResults } from "../../api/results";
import ResultsTable from "./ResultsTable";
import UrlsTable from "./UrlsTable";

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

  // 🔹 Burada backend’den gelen datayı uygun hale getiriyoruz
  const results = data || [];
  const resultData = results[0]?.data || {};   // ilk result kaydı
  const urls = resultData.sample_urls || [];   // sample_urls varsa al, yoksa []

  return (
    <div>
      <h2>Sonuçlar (Run ID: {runId})</h2>
      <ResultsTable rows={results} />

      {urls.length > 0 && (
        <>
          <h3>Bulunan URL’ler</h3>
          <UrlsTable urls={urls} />
        </>
      )}
    </div>
  );
}

export default ResultsPage;

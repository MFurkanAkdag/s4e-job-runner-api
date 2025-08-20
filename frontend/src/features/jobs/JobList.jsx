import { useQuery } from "@tanstack/react-query";
import { getJobRuns } from "../../api/jobs";
import { DataGrid } from "@mui/x-data-grid";
import { Box, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function JobList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["job-runs"],
    queryFn: getJobRuns,
  });
  const navigate = useNavigate();

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">Error: {error.message}</Typography>;

  const rows = data.items.map((job) => ({ id: job.id, ...job }));

  const columns = [
    { field: "id", headerName: "Run ID", width: 250 },
    { field: "job_type", headerName: "Job Type", width: 120 },
    { field: "status", headerName: "Status", width: 120 },
    { field: "requested_at", headerName: "Requested At", width: 200 },
    { field: "finished_at", headerName: "Finished At", width: 200 },
  ];

  return (
    <Box mt={2} style={{ height: 400, width: "100%" }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={5}
        onRowClick={(params) => navigate(`/results/${params.row.id}`)} // 👈 satıra tıklayınca ResultsPage açılır
      />
    </Box>
  );
}

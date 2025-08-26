// frontend/src/features/jobs/JobList.jsx
import { useQuery } from "@tanstack/react-query";
import { getJobRuns } from "../../api/jobs";
import { DataGrid } from "@mui/x-data-grid";
import { GridToolbar } from "@mui/x-data-grid-pro";
import { Box, Typography } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function JobList() {
  const navigate = useNavigate();

  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 10 });
  const [filterModel, setFilterModel] = useState({ items: [] });

  const statusFilter = filterModel.items.find((f) => f.columnField === "status")?.value;
  const jobTypeFilter = filterModel.items.find((f) => f.columnField === "job_type")?.value;

  const { data, isLoading, error } = useQuery({
    queryKey: ["job-runs", paginationModel, filterModel],
    queryFn: () =>
      getJobRuns({
        limit: paginationModel.pageSize,
        offset: paginationModel.page * paginationModel.pageSize,
        status: statusFilter || undefined,
        job_type: jobTypeFilter ? jobTypeFilter.toLowerCase() : undefined,
      }),
    keepPreviousData: true,
  });

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">Error: {error.message}</Typography>;

  const rows = data.items.map((job) => ({ id: job.id, ...job }));

  const columns = [
    { field: "id", headerName: "Run ID", width: 250 },
    {
      field: "job_type",
      headerName: "Job Type",
      width: 120,
      filterable: true,
      type: "singleSelect",
      valueOptions: ["os", "katana"],
    },
    {
      field: "status",
      headerName: "Status",
      width: 120,
      filterable: true,
      type: "singleSelect",
      valueOptions: ["QUEUED", "STARTED", "SUCCEEDED", "FAILED"],
    },
    { field: "requested_at", headerName: "Requested At", width: 200 },
    { field: "finished_at", headerName: "Finished At", width: 200 },
  ];

  return (
    <Box mt={2} style={{ height: 500, width: "100%" }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pagination
        paginationMode="server"
        rowCount={data.pagination.total}
        pageSizeOptions={[5, 10, 20]}
        paginationModel={paginationModel}
        onPaginationModelChange={setPaginationModel}
        filterMode="server"
        filterModel={filterModel}
        onFilterModelChange={setFilterModel}
        onRowClick={(params) => navigate(`/results/${params.row.id}`)}
        slots={{ toolbar: GridToolbar }}
      />
    </Box>
  );
}

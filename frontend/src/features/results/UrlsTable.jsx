import React from "react";
import { DataGrid } from "@mui/x-data-grid";

export default function UrlsTable({ urls }) {
  // DataGrid satırlarını hazırlıyoruz
  const rows = urls.map((url, index) => ({
    id: index + 1, // DataGrid için benzersiz ID gerekiyor
    url,
  }));

  // Kolon tanımı
  const columns = [
    { field: "id", headerName: "ID", width: 100 },
    { field: "url", headerName: "URL", flex: 1 },
  ];

  return (
    <div style={{ height: 400, width: "100%", marginTop: "1rem" }}>
      <DataGrid rows={rows} columns={columns} pageSize={10} />
    </div>
  );
}

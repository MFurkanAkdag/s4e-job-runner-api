import React from "react";
import { Container, Typography, Divider } from "@mui/material";
import OsJobForm from "./OsJobForm";
import KatanaJobForm from "./KatanaJobForm";
import JobList from "./JobList";

export default function JobsPage() {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      {/* OS Jobs Section */}
      <Typography variant="h5" gutterBottom>
        OS Jobs
      </Typography>
      <OsJobForm />
      <Divider sx={{ my: 4 }} />

      {/* Katana Jobs Section */}
      <Typography variant="h5" gutterBottom>
        Katana Jobs
      </Typography>
      <KatanaJobForm />
      <Divider sx={{ my: 4 }} />

      {/* Job List */}
      <Typography variant="h5" gutterBottom>
        All Jobs
      </Typography>
      <JobList />
    </Container>
  );
}

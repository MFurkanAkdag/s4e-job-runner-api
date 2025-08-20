// src/features/jobs/KatanaJobForm.jsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { triggerKatanaJob } from "../../api/jobs";
import { useState } from "react";
import { Box, Button, TextField } from "@mui/material";

export default function KatanaJobForm() {
  const queryClient = useQueryClient();
  const [url, setUrl] = useState("http://example.com");
  const [depth, setDepth] = useState(1);
  const [timeout, setTimeout] = useState(60);

  const mutation = useMutation({
    mutationFn: (payload) => triggerKatanaJob(payload),
    onSuccess: () => {
      queryClient.invalidateQueries(["job-runs"]);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate({ url, depth, timeout_sec: timeout });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} mt={2}>
      <TextField
        label="Target URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        fullWidth
        margin="normal"
      />
      <TextField
        label="Depth"
        type="number"
        value={depth}
        onChange={(e) => setDepth(Number(e.target.value))}
        fullWidth
        margin="normal"
      />
      <TextField
        label="Timeout (sec)"
        type="number"
        value={timeout}
        onChange={(e) => setTimeout(Number(e.target.value))}
        fullWidth
        margin="normal"
      />
      <Button type="submit" variant="contained" disabled={mutation.isLoading}>
        Run Katana Scan
      </Button>
    </Box>
  );
}

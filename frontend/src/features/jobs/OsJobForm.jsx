// src/features/jobs/OsJobForm.jsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { triggerOsJob } from "../../api/jobs";
import { useState } from "react";
import { Box, Button, TextField } from "@mui/material";

export default function OsJobForm() {
  const queryClient = useQueryClient();
  const [cmd, setCmd] = useState("ls"); // varsayılan komut

  const mutation = useMutation({
    mutationFn: (payload) => triggerOsJob(payload),
    onSuccess: () => {
      queryClient.invalidateQueries(["job-runs"]);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate({ cmd: cmd.split(" "), cwd: "/workspace/jobs" });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} mt={2}>
      <TextField
        label="OS Command"
        value={cmd}
        onChange={(e) => setCmd(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button type="submit" variant="contained" disabled={mutation.isLoading}>
        Run Command
      </Button>
    </Box>
  );
}

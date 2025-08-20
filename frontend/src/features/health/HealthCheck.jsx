import { useQuery } from "@tanstack/react-query";
import { getHealth } from "../../api/jobs";
import { Typography, Box, CircularProgress } from "@mui/material";

export default function HealthCheck() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
  });

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography color="error">Error: {error.message}</Typography>;

  return (
    <Box mt={2}>
      <Typography variant="h6">Backend Health: {data?.status}</Typography>
    </Box>
  );
}

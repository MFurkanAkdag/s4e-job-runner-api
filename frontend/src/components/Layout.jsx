import { AppBar, Toolbar, Typography, Container, Box, Button } from "@mui/material";
import { Outlet, NavLink } from "react-router-dom";

export default function Layout() {
  return (
    <Box>
      {/* Navbar */}
      <AppBar
        position="static"
        sx={{
          background: "linear-gradient(90deg, #1976d2 0%, #9c27b0 100%)", // mavi → mor geçişli
        }}
      >
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Job Runner Frontend
          </Typography>

          {/* NavLink kullanarak aktif sayfayı belirgin yapıyoruz */}
          <Button
            color="inherit"
            component={NavLink}
            to="/jobs"
            sx={{
              "&.active": {
                borderBottom: "2px solid white",
                fontWeight: "bold",
              },
            }}
          >
            Jobs
          </Button>

          <Button
            color="inherit"
            component={NavLink}
            to="/results"
            sx={{
              "&.active": {
                borderBottom: "2px solid white",
                fontWeight: "bold",
              },
            }}
          >
            Results
          </Button>

          <Button
            color="inherit"
            component={NavLink}
            to="/health"
            sx={{
              "&.active": {
                borderBottom: "2px solid white",
                fontWeight: "bold",
              },
            }}
          >
            Health
          </Button>
        </Toolbar>
      </AppBar>

      {/* İçerik */}
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}

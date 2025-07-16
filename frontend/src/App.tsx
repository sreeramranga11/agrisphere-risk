import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

// Components
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import FarmManagement from './pages/FarmManagement/FarmManagement';
import RiskAssessment from './pages/RiskAssessment/RiskAssessment';
import DamageAnalysis from './pages/DamageAnalysis/DamageAnalysis';
import Portfolio from './pages/Portfolio/Portfolio';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32', // Green for agriculture
      light: '#4caf50',
      dark: '#1b5e20',
    },
    secondary: {
      main: '#ff9800', // Orange for alerts/warnings
      light: '#ffb74d',
      dark: '#f57c00',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      color: '#2e7d32',
    },
    h5: {
      fontWeight: 500,
      color: '#424242',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/farms" element={<FarmManagement />} />
                <Route path="/risk-assessment" element={<RiskAssessment />} />
                <Route path="/damage-analysis" element={<DamageAnalysis />} />
                <Route path="/portfolio" element={<Portfolio />} />
              </Routes>
            </Layout>
          </Box>
        </Router>
      </LocalizationProvider>
    </ThemeProvider>
  );
}

export default App;

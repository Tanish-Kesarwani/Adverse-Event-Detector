import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './pages/HomePage';
import RecordingDashboard from './pages/RecordingDashboard';
import ResultsPage from './pages/ResultsPage';
import Header from './components/Header';

// Create a medical-themed color palette
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Medical blue
      light: '#4791db',
      dark: '#115293',
    },
    secondary: {
      main: '#28a745', // Success green
      light: '#48b461',
      dark: '#1e7e34',
    },
    error: {
      main: '#dc3545', // Critical red
      light: '#e05c68',
      dark: '#bd2130',
    },
    warning: {
      main: '#ffc107', // Warning yellow
      light: '#ffcd38',
      dark: '#e0a800',
    },
    info: {
      main: '#17a2b8', // Info teal
      light: '#4fb3c6',
      dark: '#138496',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
    },
    h2: {
      fontWeight: 500,
    },
    h3: {
      fontWeight: 500,
    },
    button: {
      textTransform: 'none',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 28,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 20px 0 rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/record" element={<RecordingDashboard />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;

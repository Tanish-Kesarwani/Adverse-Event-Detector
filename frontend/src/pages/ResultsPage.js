import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; //
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Grid, 
  Divider, 
  Chip, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  Card, 
  CardContent, 
  IconButton, 
  Tooltip,
  LinearProgress,
  Menu,
  MenuItem
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import ShareIcon from '@mui/icons-material/Share';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import ErrorIcon from '@mui/icons-material/Error';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip as ChartTooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { useLocation } from 'react-router-dom';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, ChartTooltip, Legend);

// Mock data for demonstration
const mockAnalysisResults = {
  extracted_medicines: ['Lisinopril', 'Aspirin'],
  extracted_symptoms: ['dry cough', 'dizziness', 'headache'],
  adverse_events: [
    {
      medicine: 'Lisinopril',
      matched_drug: 'lisinopril',
      drug_match_confidence: 0.95,
      severity: 'Needs Attention',
      matched_symptoms: [
        {
          symptom: 'dry cough',
          matched_reaction: 'cough',
          prediction_confidence: 0.89,
          predicted_severity: 'Needs Attention'
        },
        {
          symptom: 'dizziness',
          matched_reaction: 'dizziness',
          prediction_confidence: 0.78,
          predicted_severity: 'Near-Critical'
        }
      ]
    },
    {
      medicine: 'Aspirin',
      matched_drug: 'aspirin',
      drug_match_confidence: 0.92,
      severity: 'Needs Attention',
      matched_symptoms: [
        {
          symptom: 'headache',
          matched_reaction: 'headache',
          prediction_confidence: 0.65,
          predicted_severity: 'Needs Attention'
        }
      ]
    }
  ],
  transcription: {
    text: `Doctor: Hello, how are you feeling today?
Patient: Not great. I've been taking Lisinopril for my blood pressure, but I've been having this persistent dry cough.
Doctor: How long have you been experiencing this cough?
Patient: About two weeks now. It's worse at night.
Doctor: That's a common side effect of Lisinopril. Are you experiencing any other symptoms?
Patient: I've also been feeling a bit dizzy sometimes, especially when I stand up quickly.
Doctor: I see. Have you been taking any other medications?
Patient: Just a low-dose Aspirin daily, as you recommended.
Doctor: And have you had any headaches recently?
Patient: Yes, occasionally. Usually in the afternoon.`,
    model: 'base',
    diarization_enabled: true
  },
  processing_time: 3.45,
  timestamp: Date.now() / 1000
};

// Timeline markers for key mentions in the conversation
const mockTimelineMarkers = [
  { time: '00:12', type: 'medicine', text: 'Lisinopril', severity: 'normal' },
  { time: '00:18', type: 'symptom', text: 'dry cough', severity: 'warning' },
  { time: '00:42', type: 'symptom', text: 'dizziness', severity: 'critical' },
  { time: '01:05', type: 'medicine', text: 'Aspirin', severity: 'normal' },
  { time: '01:22', type: 'symptom', text: 'headache', severity: 'warning' }
];

const ResultsPage = () => {
  const location = useLocation();
  const { results: locationResults, audioUrl } = location.state || {};
  
  // Use results from location instead of mockAnalysisResults
  const [analysisResults, setAnalysisResults] = useState(locationResults || mockAnalysisResults);
  
  const { sessionId } = useParams();
  const navigate = useNavigate();
  // Removing this line since it conflicts with the destructured 'results' from location.state
  // const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTimelineMarker, setActiveTimelineMarker] = useState(null);
  const [shareMenuAnchor, setShareMenuAnchor] = useState(null);
  const reportRef = useRef(null);
  
  // Fetch results data
  useEffect(() => {
    // In a real app, you would fetch the results from the API
    // For demo purposes, we'll use mock data
    const fetchResults = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setAnalysisResults(locationResults || mockAnalysisResults);
        setLoading(false);
      } catch (err) {
        setError('Failed to load analysis results');
        setLoading(false);
      }
    };
    
    fetchResults();
  }, [sessionId, locationResults]);
  
  // Prepare chart data
  const getChartData = () => {
    if (!analysisResults) return null;
    
    const medicines = [];
    const confidenceScores = [];
    const backgroundColors = [];
    
    analysisResults.adverse_events.forEach(event => {
      event.matched_symptoms.forEach(symptom => {
        medicines.push(`${event.medicine} - ${symptom.symptom}`);
        confidenceScores.push(symptom.prediction_confidence);
        
        // Set color based on severity
        if (symptom.predicted_severity.includes('Critical')) {
          backgroundColors.push('rgba(220, 53, 69, 0.7)'); // Red for critical
        } else if (symptom.predicted_severity.includes('Near')) {
          backgroundColors.push('rgba(255, 193, 7, 0.7)'); // Yellow for near-critical
        } else {
          backgroundColors.push('rgba(40, 167, 69, 0.7)'); // Green for needs attention
        }
      });
    });
    
    return {
      labels: medicines,
      datasets: [
        {
          label: 'Confidence Score',
          data: confidenceScores,
          backgroundColor: backgroundColors,
          borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
          borderWidth: 1
        }
      ]
    };
  };
  
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `Confidence: ${(context.raw * 100).toFixed(1)}%`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        ticks: {
          callback: function(value) {
            return `${(value * 100).toFixed(0)}%`;
          }
        },
        title: {
          display: true,
          text: 'Confidence'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Medicine - Symptom Pairs'
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      }
    }
  };
  
  const handleTimelineMarkerClick = (marker) => {
    setActiveTimelineMarker(marker);
    
    // In a real app, you would scroll to the relevant part of the transcript
    // or highlight the relevant text
  };
  
  const handleShareClick = (event) => {
    setShareMenuAnchor(event.currentTarget);
  };
  
  const handleShareClose = () => {
    setShareMenuAnchor(null);
  };
  
  const handleDownloadPDF = async () => {
    if (!reportRef.current) return;
    
    try {
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        logging: false,
        useCORS: true
      });
      
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      const imgY = 30;
      
      pdf.setFontSize(18);
      pdf.text('MedSafeVoice Analysis Report', pdfWidth / 2, 20, { align: 'center' });
      pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
      pdf.save('medsafevoice-report.pdf');
    } catch (err) {
      console.error('Error generating PDF:', err);
    }
  };
  
  const getSeverityIcon = (severity) => {
    if (severity.includes('Critical') && !severity.includes('Near')) {
      return <ErrorIcon color="error" />;
    } else if (severity.includes('Near')) {
      return <WarningIcon color="warning" />;
    } else {
      return <InfoIcon color="success" />;
    }
  };
  
  const formatTranscript = (text) => {
    if (!text) return [];
    
    const lines = text.split('\n').filter(line => line.trim());
    return lines.map((line, index) => {
      const isSpeakerLine = line.includes(':');
      if (!isSpeakerLine) return { text: line, speaker: null };
      
      const [speaker, content] = line.split(':', 2);
      return {
        text: content.trim(),
        speaker: speaker.trim(),
        isPatient: speaker.trim().toLowerCase() === 'patient'
      };
    });
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
          <Typography variant="h5" gutterBottom>Loading Analysis Results</Typography>
          <LinearProgress sx={{ width: '50%', mt: 2 }} />
        </Box>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
          <Typography variant="h5" color="error" gutterBottom>{error}</Typography>
          <Button 
            variant="contained" 
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Back to Recording
          </Button>
        </Box>
      </Container>
    );
  }
  
  if (!analysisResults) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
          <Typography variant="h5" gutterBottom>No results found</Typography>
          <Button 
            variant="contained" 
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Back to Recording
          </Button>
        </Box>
      </Container>
    );
  }
  
  const formattedTranscript = formatTranscript(analysisResults.transcription?.text);
  const chartData = getChartData();
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }} ref={reportRef}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button 
          variant="outlined" 
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
        >
          Back to Recording
        </Button>
        
        <Typography variant="h4" component="h1">
          Analysis Results
        </Typography>
        
        <Box>
          <Tooltip title="Download Report">
            <IconButton onClick={handleDownloadPDF}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Share Report">
            <IconButton onClick={handleShareClick}>
              <ShareIcon />
            </IconButton>
          </Tooltip>
          
          <Menu
            anchorEl={shareMenuAnchor}
            open={Boolean(shareMenuAnchor)}
            onClose={handleShareClose}
          >
            <MenuItem onClick={handleShareClose}>Share via Email</MenuItem>
            <MenuItem onClick={handleShareClose}>Copy Link</MenuItem>
            <MenuItem onClick={handleShareClose}>Export to EHR</MenuItem>
          </Menu>
        </Box>
      </Box>
      
      {/* Timeline */}
      <Paper elevation={2} sx={{ p: 2, mb: 4, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Conversation Timeline
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          overflowX: 'auto', 
          py: 2,
          '&::-webkit-scrollbar': {
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f1f1',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#888',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: '#555',
          },
        }}>
          <Box sx={{ 
            position: 'relative', 
            height: '60px', 
            width: '100%', 
            minWidth: '600px',
            borderBottom: '2px solid #e0e0e0',
          }}>
            {mockTimelineMarkers.map((marker, index) => (
              <Tooltip 
                key={index} 
                title={`${marker.time}: ${marker.text}`}
                placement="top"
              >
                <Box
                  onClick={() => handleTimelineMarkerClick(marker)}
                  sx={{
                    position: 'absolute',
                    left: `${(index / (mockTimelineMarkers.length - 1)) * 100}%`,
                    bottom: 0,
                    transform: 'translateX(-50%)',
                    cursor: 'pointer',
                  }}
                >
                  <Box sx={{
                    width: '2px',
                    height: '10px',
                    backgroundColor: '#757575',
                    mb: '4px',
                    mx: 'auto'
                  }} />
                  <Chip
                    label={marker.text}
                    size="small"
                    icon={
                      marker.type === 'medicine' 
                        ? <InfoIcon fontSize="small" /> 
                        : marker.severity === 'critical' 
                          ? <ErrorIcon fontSize="small" /> 
                          : <WarningIcon fontSize="small" />
                    }
                    color={
                      marker.severity === 'critical' 
                        ? 'error' 
                        : marker.severity === 'warning' 
                          ? 'warning' 
                          : 'primary'
                    }
                    sx={{ 
                      transform: 'translateY(50%)',
                      mb: 1
                    }}
                  />
                  <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', mt: 3 }}>
                    {marker.time}
                  </Typography>
                </Box>
              </Tooltip>
            ))}
          </Box>
        </Box>
      </Paper>
      
      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Left Panel - Transcript */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Conversation Transcript
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ maxHeight: '600px', overflowY: 'auto', pr: 2 }}>
              {formattedTranscript.map((line, index) => (
                <Box 
                  key={index} 
                  sx={{ 
                    mb: 2,
                    backgroundColor: line.isPatient ? 'rgba(25, 118, 210, 0.05)' : 'transparent',
                    borderRadius: 1,
                    p: 1
                  }}
                >
                  {line.speaker && (
                    <Typography 
                      variant="subtitle2" 
                      color={line.isPatient ? 'primary' : 'text.secondary'}
                      sx={{ fontWeight: 'bold' }}
                    >
                      {line.speaker}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    {line.text}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
        
        {/* Right Panel - Analysis Results */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Detected Medicines & Symptoms
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Medicines
                </Typography>
                <List dense>
                  {analysisResults.extracted_medicines.map((medicine, index) => (
                    <ListItem key={index}>
                      <ListItemText 
                        primary={medicine} 
                        secondary="Extracted from conversation"
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Symptoms
                </Typography>
                <List dense>
                  {analysisResults.extracted_symptoms.map((symptom, index) => (
                    <ListItem key={index}>
                      <ListItemText 
                        primary={symptom} 
                        secondary="Extracted from conversation"
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            </Grid>
          </Paper>
          
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Potential Adverse Events
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {analysisResults.adverse_events.map((event, index) => (
              <Card key={index} sx={{ mb: 2, borderLeft: '4px solid', borderColor: 'primary.main' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {event.medicine}
                    <Chip 
                      size="small" 
                      label={event.severity} 
                      color={
                        event.severity.includes('Critical') && !event.severity.includes('Near')
                          ? 'error'
                          : event.severity.includes('Near')
                            ? 'warning'
                            : 'success'
                      }
                      icon={getSeverityIcon(event.severity)}
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Matched to {event.matched_drug} with {(event.drug_match_confidence * 100).toFixed(1)}% confidence
                  </Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 2 }}>
                    Associated Symptoms:
                  </Typography>
                  
                  <List dense>
                    {event.matched_symptoms.map((symptom, symptomIndex) => (
                      <ListItem key={symptomIndex}>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {symptom.symptom}
                              <Chip 
                                size="small" 
                                label={symptom.predicted_severity} 
                                color={
                                  symptom.predicted_severity.includes('Critical') && !symptom.predicted_severity.includes('Near')
                                    ? 'error'
                                    : symptom.predicted_severity.includes('Near')
                                      ? 'warning'
                                      : 'success'
                                }
                                sx={{ ml: 1 }}
                              />
                            </Box>
                          }
                          secondary={`Matched to ${symptom.matched_reaction} with ${(symptom.prediction_confidence * 100).toFixed(1)}% confidence`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            ))}
          </Paper>
          
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Confidence Analysis
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {chartData && (
              <Box sx={{ height: '300px' }}>
                <Bar data={chartData} options={chartOptions} />
              </Box>
            )}
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
              Chart showing confidence scores for detected medicine-symptom pairs
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ResultsPage;
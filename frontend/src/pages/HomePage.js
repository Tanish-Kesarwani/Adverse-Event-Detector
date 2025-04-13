import React from 'react';
import { Container, Typography, Button, Box, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom'; // 
import MicIcon from '@mui/icons-material/Mic';
import InfoIcon from '@mui/icons-material/Info';
import HistoryIcon from '@mui/icons-material/History';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Adverse Event Detection System
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
          Record and analyze medical conversations to detect potential adverse drug events
        </Typography>
        <Button 
          variant="contained" 
          size="large" 
          startIcon={<MicIcon />}
          onClick={() => navigate('/record')}
          sx={{ 
            py: 1.5, 
            px: 4, 
            borderRadius: 3,
            fontSize: '1.1rem'
          }}
        >
          Start Recording
        </Button>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, height: '100%', borderRadius: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MicIcon color="primary" sx={{ mr: 1, fontSize: 28 }} />
                <Typography variant="h6">Record Conversations</Typography>
              </Box>
              <Typography variant="body1" sx={{ mb: 2, flexGrow: 1 }}>
                Record patient-doctor conversations with our easy-to-use interface. 
                Our system automatically transcribes the audio and identifies speakers.
              </Typography>
              <Button 
                variant="outlined" 
                onClick={() => navigate('/record')}
                sx={{ alignSelf: 'flex-start' }}
              >
                Start Recording
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, height: '100%', borderRadius: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <InfoIcon color="primary" sx={{ mr: 1, fontSize: 28 }} />
                <Typography variant="h6">Detect Adverse Events</Typography>
              </Box>
              <Typography variant="body1" sx={{ mb: 2, flexGrow: 1 }}>
                Our AI-powered system analyzes conversations to identify potential adverse 
                drug events, medication mentions, and symptoms with high accuracy.
              </Typography>
              <Button 
                variant="outlined"
                onClick={() => navigate('/about')}
                sx={{ alignSelf: 'flex-start' }}
              >
                Learn More
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, height: '100%', borderRadius: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <HistoryIcon color="primary" sx={{ mr: 1, fontSize: 28 }} />
                <Typography variant="h6">Review Past Recordings</Typography>
              </Box>
              <Typography variant="body1" sx={{ mb: 2, flexGrow: 1 }}>
                Access your past recordings and analysis results. Review transcripts, 
                identified medications, symptoms, and potential adverse events.
              </Typography>
              <Button 
                variant="outlined"
                onClick={() => navigate('/history')}
                sx={{ alignSelf: 'flex-start' }}
              >
                View History
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 6, p: 3, bgcolor: 'rgba(0, 0, 0, 0.02)', borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom>
          About This Project
        </Typography>
        <Typography variant="body1">
          The Adverse Event Detection System is designed to help healthcare professionals identify 
          potential adverse drug events in patient-doctor conversations. By leveraging advanced 
          speech recognition and natural language processing technologies, our system can automatically 
          detect medications, symptoms, and their relationships to flag potential issues.
        </Typography>
      </Box>
    </Container>
  );
};

export default HomePage;
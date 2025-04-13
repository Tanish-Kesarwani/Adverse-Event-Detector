import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom'; // 
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Paper, 
  Grid, 
  IconButton, 
  Drawer, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Divider, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Switch, 
  FormControlLabel, 
  Alert, 
  CircularProgress, 
  LinearProgress,
  Tooltip
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import SettingsIcon from '@mui/icons-material/Settings';
import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';
import SpeedIcon from '@mui/icons-material/Speed';
import TranslateIcon from '@mui/icons-material/Translate';
import Wave from 'react-wavify';
import axios from 'axios';

// Mock audio visualization data
const generateWavePoints = (amplitude) => {
  return Array.from({ length: 100 }, () => Math.random() * amplitude);
};

const RecordingDashboard = () => {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [waveAmplitude, setWaveAmplitude] = useState(20);
  const [wavePoints, setWavePoints] = useState(generateWavePoints(20));
  const [processingStatus, setProcessingStatus] = useState('idle'); // idle, recording, transcribing, analyzing, complete
  const [notification, setNotification] = useState(null);
  const [whisperModel, setWhisperModel] = useState('base');
  const [enableDiarization, setEnableDiarization] = useState(true);
  const [patientSpeaker, setPatientSpeaker] = useState('speaker1');
  const [availableModels, setAvailableModels] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const timerRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  
  // Fetch available models on component mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/models');
        setAvailableModels(response.data);
      } catch (error) {
        console.error('Error fetching models:', error);
        setNotification({
          type: 'error',
          message: 'Failed to fetch available models. Please refresh the page.'
        });
      }
    };
    
    fetchModels();
  }, []);
  
  // Timer effect for recording duration
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    
    return () => clearInterval(timerRef.current);
  }, [isRecording]);
  
  // Audio visualization effect
  useEffect(() => {
    let animationFrame;
    
    const updateWaveform = () => {
      if (isRecording) {
        // Simulate microphone input by varying the amplitude
        const newAmplitude = 20 + Math.sin(Date.now() / 500) * 15;
        setWaveAmplitude(newAmplitude);
        setWavePoints(generateWavePoints(newAmplitude));
      }
      animationFrame = requestAnimationFrame(updateWaveform);
    };
    
    if (isRecording) {
      animationFrame = requestAnimationFrame(updateWaveform);
    } else {
      setWaveAmplitude(20);
      setWavePoints(generateWavePoints(20));
    }
    
    return () => cancelAnimationFrame(animationFrame);
  }, [isRecording]);
  
  // Progress simulation for demo purposes
  useEffect(() => {
    let progressInterval;
    
    if (processingStatus === 'transcribing' || processingStatus === 'analyzing') {
      progressInterval = setInterval(() => {
        setProgress(prev => {
          const increment = Math.random() * 10;
          const newProgress = Math.min(prev + increment, 95);
          
          if (newProgress > 50 && processingStatus === 'transcribing') {
            setProcessingStatus('analyzing');
            return 50; // Reset progress for analysis phase
          }
          
          return newProgress;
        });
      }, 500);
    }
    
    return () => clearInterval(progressInterval);
  }, [processingStatus]);
  
  const toggleRecording = async () => {
    if (!isRecording) {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];
        
        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };
        
        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          processAudioRecording(audioBlob);
        };
        
        mediaRecorderRef.current.start();
        setIsRecording(true);
        setRecordingTime(0);
        setProcessingStatus('recording');
        setNotification({
          type: 'info',
          message: 'Recording started. Speak clearly for best results.'
        });
      } catch (error) {
        console.error('Error accessing microphone:', error);
        setNotification({
          type: 'error',
          message: 'Could not access microphone. Please check permissions.'
        });
      }
    } else {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
      setIsRecording(false);
      setProcessingStatus('transcribing');
      setProgress(0);
      setNotification({
        type: 'info',
        message: 'Processing audio. Please wait...'
      });
    }
  };
  
  const processAudioRecording = async (audioBlob) => {
    try {
      setIsLoading(true);
      setProcessingStatus('transcribing');
      setProgress(0);
      
      // DEBUG: Save audio for debugging purposes
      const audioUrl = URL.createObjectURL(audioBlob);
      const debugAudioLink = document.createElement('a');
      debugAudioLink.href = audioUrl;
      debugAudioLink.download = 'debug-recording.wav';
      
      // Create a debug text file with recording info
      const debugText = `Recording Debug Info:
Time: ${new Date().toISOString()}
Duration: ${recordingTime} seconds
Audio Size: ${(audioBlob.size / 1024).toFixed(2)} KB
Settings:
- Whisper Model: ${whisperModel}
- Diarization: ${enableDiarization ? 'Enabled' : 'Disabled'}
- Patient Speaker: ${patientSpeaker}

Backend Error: SymptomExtractor object has no attribute 'extract_symptoms_from_conversation'
This suggests the backend API is expecting a method that doesn't exist in the SymptomExtractor class.
`;
      
      const debugTextBlob = new Blob([debugText], { type: 'text/plain' });
      const debugTextUrl = URL.createObjectURL(debugTextBlob);
      const debugTextLink = document.createElement('a');
      debugTextLink.href = debugTextUrl;
      debugTextLink.download = 'audio-debug.txt';
      
      // Save both files
      debugAudioLink.click();
      debugTextLink.click();
      
      // Create form data for the API request
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav'); // Add filename to help server identify file type
      formData.append('whisper_model', whisperModel);
      formData.append('enable_diarization', enableDiarization.toString());
      formData.append('patient_speaker', patientSpeaker);
      
      console.log('Sending audio to backend:', {
        audioSize: audioBlob.size,
        whisperModel,
        enableDiarization,
        patientSpeaker
      });
      
      try {
        // Send the audio to the backend for processing
        const response = await axios.post('http://localhost:5000/api/analyze-audio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          // Increase timeout to 5 minutes for larger files
          timeout: 300000, // 5 minutes timeout
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            console.log(`Upload progress: ${percentCompleted}%`);
            setProgress(Math.min(percentCompleted / 2, 45)); // Cap at 45% for upload phase
          }
        });
        
        setIsLoading(false);
        setProcessingStatus('complete');
        setProgress(100);
        
        // Navigate to results page with the response data
        navigate('/results', { 
          state: { 
            results: response.data,
            audioUrl: URL.createObjectURL(audioBlob)
          } 
        });
      } catch (error) {
        // If the server is not responding or has an error, use mock data for demo purposes
        console.error('Backend error, using fallback data:', error);
        
        // For demo purposes, use mock data if the backend fails
        setIsLoading(false);
        setProcessingStatus('complete');
        setProgress(100);
        
        // Navigate with mock data
        navigate('/results', { 
          state: { 
            results: null, // This will trigger the mock data in ResultsPage
            audioUrl: URL.createObjectURL(audioBlob)
          } 
        });
        
        setNotification({
          type: 'warning',
          message: 'Backend server error. Using demo data for preview purposes.'
        });
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      setIsLoading(false);
      setProcessingStatus('idle');
      setNotification({
        type: 'error',
        message: `Failed to process audio: ${error.response?.data?.error || error.message}`
      });
    }
  };
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };
  
  const getStatusText = () => {
    switch (processingStatus) {
      case 'idle':
        return 'Ready to record';
      case 'recording':
        return 'Recording in progress';
      case 'transcribing':
        return 'Transcribing audio';
      case 'analyzing':
        return 'Analyzing for adverse events';
      case 'complete':
        return 'Analysis complete';
      default:
        return 'Ready';
    }
  };
  
  const toggleSettings = () => {
    setSettingsOpen(!settingsOpen);
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={4}>
        <Grid item xs={12}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Medical Conversation Recorder
          </Typography>
          <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary">
            Record patient-doctor conversations to detect potential adverse drug events
          </Typography>
        </Grid>
        
        {notification && (
          <Grid item xs={12}>
            <Alert 
              severity={notification.type} 
              onClose={() => setNotification(null)}
              sx={{ mb: 2 }}
            >
              {notification.message}
            </Alert>
          </Grid>
        )}
        
        <Grid item xs={12} md={8} sx={{ mx: 'auto' }}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 4, 
              borderRadius: 4,
              background: 'linear-gradient(to right bottom, #ffffff, #f8f9fa)'
            }}
          >
            {/* Status and Timer */}
            <Box sx={{ mb: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                {getStatusText()}
              </Typography>
              <Typography variant="h3" sx={{ fontFamily: 'monospace', my: 1 }}>
                {formatTime(recordingTime)}
              </Typography>
              
              {(processingStatus === 'transcribing' || processingStatus === 'analyzing') && (
                <Box sx={{ width: '100%', mt: 2 }}>
                  <LinearProgress variant="determinate" value={progress} color="primary" />
                  <Typography variant="body2" color="text.secondary" align="right" sx={{ mt: 0.5 }}>
                    {Math.round(progress)}%
                  </Typography>
                </Box>
              )}
            </Box>
            
            {/* Audio Visualization */}
            <Box 
              sx={{ 
                height: 120, 
                mb: 4, 
                borderRadius: 2,
                overflow: 'hidden',
                bgcolor: 'rgba(25, 118, 210, 0.05)',
                border: '1px solid rgba(25, 118, 210, 0.1)'
              }}
            >
              {isRecording ? (
                <Wave 
                  fill="#1976d2"
                  paused={!isRecording}
                  options={{
                    height: 80,
                    amplitude: waveAmplitude,
                    speed: 0.3,
                    points: 5
                  }}
                />
              ) : (
                <Box 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center' 
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    {processingStatus === 'idle' ? 'Press the microphone button to start recording' : 'Processing...'}
                  </Typography>
                </Box>
              )}
            </Box>
            
            {/* Microphone Button */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
              <Tooltip title={isRecording ? "Stop Recording" : "Start Recording"}>
                <IconButton
                  aria-label="record"
                  onClick={toggleRecording}
                  disabled={processingStatus === 'transcribing' || processingStatus === 'analyzing'}
                  sx={{
                    width: 80,
                    height: 80,
                    bgcolor: isRecording ? 'error.main' : 'primary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: isRecording ? 'error.dark' : 'primary.dark',
                    },
                    transition: 'all 0.3s ease',
                    animation: isRecording ? 'pulse 1.5s infinite' : 'none',
                    '@keyframes pulse': {
                      '0%': {
                        boxShadow: '0 0 0 0 rgba(220, 53, 69, 0.7)',
                      },
                      '70%': {
                        boxShadow: '0 0 0 10px rgba(220, 53, 69, 0)',
                      },
                      '100%': {
                        boxShadow: '0 0 0 0 rgba(220, 53, 69, 0)',
                      },
                    },
                  }}
                >
                  {isLoading ? (
                    <CircularProgress size={40} color="inherit" />
                  ) : (
                    <MicIcon sx={{ fontSize: 40 }} />
                  )}
                </IconButton>
              </Tooltip>
            </Box>
            
            {/* Settings Button */}
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<SettingsIcon />}
                onClick={toggleSettings}
                sx={{ borderRadius: 4 }}
              >
                Recording Settings
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Settings Drawer */}
      <Drawer
        anchor="right"
        open={settingsOpen}
        onClose={toggleSettings}
      >
        <Box sx={{ width: 320, p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recording Settings</Typography>
            <IconButton onClick={toggleSettings}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <List>
            <ListItem>
              <ListItemIcon>
                <SpeedIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Transcription Model" 
                secondary="Select model size and accuracy"
              />
            </ListItem>
            <ListItem sx={{ pl: 9 }}>
              <FormControl fullWidth size="small">
                <InputLabel id="whisper-model-label">Whisper Model</InputLabel>
                <Select
                  labelId="whisper-model-label"
                  value={whisperModel}
                  label="Whisper Model"
                  onChange={(e) => setWhisperModel(e.target.value)}
                >
                  {availableModels.map(model => (
                    <MenuItem key={model.id} value={model.id}>
                      {model.name} - {model.processing_speed}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <TranslateIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Speaker Diarization" 
                secondary="Identify different speakers"
              />
            </ListItem>
            <ListItem sx={{ pl: 9 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={enableDiarization}
                    onChange={(e) => setEnableDiarization(e.target.checked)}
                    color="primary"
                  />
                }
                label="Enable speaker identification"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <PersonIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Patient Speaker" 
                secondary="Identify which speaker is the patient"
              />
            </ListItem>
            <ListItem sx={{ pl: 9 }}>
              <FormControl fullWidth size="small">
                <InputLabel id="patient-speaker-label">Patient Speaker</InputLabel>
                <Select
                  labelId="patient-speaker-label"
                  value={patientSpeaker}
                  label="Patient Speaker"
                  onChange={(e) => setPatientSpeaker(e.target.value)}
                  disabled={!enableDiarization}
                >
                  <MenuItem value="speaker1">Speaker 1</MenuItem>
                  <MenuItem value="speaker2">Speaker 2</MenuItem>
                  <MenuItem value="auto">Auto-detect</MenuItem>
                </Select>
              </FormControl>
            </ListItem>
          </List>
          
          <Box sx={{ mt: 4 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Larger models provide better accuracy but take longer to process.
              </Typography>
            </Alert>
            <Button 
              variant="contained" 
              fullWidth 
              onClick={toggleSettings}
              sx={{ mt: 2 }}
            >
              Apply Settings
            </Button>
          </Box>
        </Box>
      </Drawer>
    </Container>
  );
};

export default RecordingDashboard;

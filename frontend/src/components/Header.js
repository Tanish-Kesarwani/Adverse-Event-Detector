import React from 'react'; // 
import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';

const Header = () => {
  return (
    <AppBar position="static" color="primary" elevation={0}>
      <Toolbar>
        <Box display="flex" alignItems="center">
          <MedicalServicesIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MedSafeVoice
          </Typography>
        </Box>
        <Box sx={{ flexGrow: 1 }} />
        <Button 
          color="inherit" 
          component={RouterLink} 
          to="/"
        >
          Record
        </Button>
        <Button 
          color="inherit" 
          component="a" 
          href="https://github.com/yourusername/MedSafeVoice" 
          target="_blank"
        >
          About
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
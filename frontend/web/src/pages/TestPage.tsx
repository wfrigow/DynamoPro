import React from 'react';
import { Box, Typography, Paper, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const TestPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <Container maxWidth="md">
      <Box sx={{ p: 3, mt: 4 }}>
        <Paper sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h4" gutterBottom>
            DynamoPro Test Page
          </Typography>
          <Typography variant="body1" paragraph>
            If you can see this page, the React application is rendering correctly.
            This is a public test page that doesn't require authentication.
          </Typography>
          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => navigate('/login')}
            >
              Go to Login
            </Button>
            <Button 
              variant="outlined" 
              color="primary"
              onClick={() => navigate('/')}
            >
              Go to Dashboard
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default TestPage;

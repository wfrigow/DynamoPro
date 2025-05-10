import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const TestComponent: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 4, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          DynamoPro Test Component
        </Typography>
        <Typography variant="body1" paragraph>
          If you can see this component, the React application is rendering correctly.
        </Typography>
        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/audit')}
          >
            Go to Audit
          </Button>
          <Button 
            variant="outlined" 
            color="primary"
            onClick={() => navigate('/recommendations')}
          >
            Go to Recommendations
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default TestComponent;

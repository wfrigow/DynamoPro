import React, { useState } from 'react';
import { Container, Typography, Box, Paper, Button, Grid } from '@mui/material';
import VoiceAuditAssistant from '../components/audit/VoiceAuditAssistant';
import UnifiedVoiceAssistant from '../components/audit/UnifiedVoiceAssistant';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

const TestPage: React.FC = () => {
  const userId = useSelector((state: RootState) => state.auth.user?.id) || 'test-user';
  const [useUnifiedAssistant, setUseUnifiedAssistant] = useState<boolean>(true);

  const handleAuditComplete = (auditData: Record<string, any>) => {
    console.log('Audit complété avec succès:', auditData);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Page de Test - Assistant Vocal
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item>
            <Button 
              variant={useUnifiedAssistant ? "contained" : "outlined"}
              onClick={() => setUseUnifiedAssistant(true)}
              color="primary"
            >
              Assistant Unifié (1 étape)
            </Button>
          </Grid>
          <Grid item>
            <Button 
              variant={!useUnifiedAssistant ? "contained" : "outlined"}
              onClick={() => setUseUnifiedAssistant(false)}
              color="primary"
            >
              Assistant Original (3 étapes)
            </Button>
          </Grid>
        </Grid>
        
        <Paper elevation={3} sx={{ p: 3, height: '70vh' }}>
          {useUnifiedAssistant ? (
            <UnifiedVoiceAssistant userId={userId} onAuditComplete={handleAuditComplete} />
          ) : (
            <VoiceAuditAssistant userId={userId} onAuditComplete={handleAuditComplete} />
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default TestPage;

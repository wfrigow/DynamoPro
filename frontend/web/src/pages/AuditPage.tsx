import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Stepper, 
  Step, 
  StepLabel, 
  Button,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectAuth } from '../store/slices/authSlice';
import VoiceAuditAssistant from '../components/audit/VoiceAuditAssistant';
import { Home, Bolt, Opacity, Delete, Nature, Business } from '@mui/icons-material';

const steps = ['Profil', 'Consommation', 'Propriété', 'Recommandations'];

const AuditPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useSelector(selectAuth);
  const [activeStep, setActiveStep] = useState(0);
  const [auditData, setAuditData] = useState<Record<string, any>>({});
  const [auditComplete, setAuditComplete] = useState(false);
  const [recommendations, setRecommendations] = useState<any[]>([]);

  const handleAuditComplete = async (data: Record<string, any>) => {
    setAuditData(data);
    setAuditComplete(true);
    
    // In a real implementation, we would call an API to get recommendations
    // based on the collected audit data
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock recommendations based on collected data
      const mockRecommendations = generateMockRecommendations(data);
      setRecommendations(mockRecommendations);
      setActiveStep(3); // Move to recommendations step
    } catch (error) {
      console.error('Error generating recommendations:', error);
    }
  };

  const generateMockRecommendations = (data: Record<string, any>) => {
    const recs = [];
    
    // Property-based recommendations
    if (data.property?.propertyType === 'house' && data.property?.yearBuilt < 2000) {
      recs.push({
        id: '1',
        title: 'Isolation des murs',
        description: 'L\'isolation des murs peut réduire votre consommation énergétique de 25%.',
        savings: 850,
        roi: 4,
        domain: 'energy',
        priority: 'high'
      });
    }
    
    // Consumption-based recommendations
    if (data.consumption?.electricityUsage > 4000) {
      recs.push({
        id: '2',
        title: 'Installation de panneaux solaires',
        description: 'Avec votre consommation élevée, les panneaux solaires seraient rentabilisés en 5 ans.',
        savings: 1200,
        roi: 5,
        domain: 'energy',
        priority: 'medium'
      });
    }
    
    if (data.consumption?.waterUsage > 100) {
      recs.push({
        id: '3',
        title: 'Système de récupération d\'eau de pluie',
        description: 'Réduisez votre consommation d\'eau potable avec un système de récupération d\'eau de pluie.',
        savings: 350,
        roi: 3,
        domain: 'water',
        priority: 'medium'
      });
    }
    
    // Add some default recommendations
    recs.push({
      id: '4',
      title: 'Remplacement des ampoules par des LED',
      description: 'Remplacer toutes vos ampoules par des LED peut réduire votre consommation d\'électricité liée à l\'éclairage de 80%.',
      savings: 120,
      roi: 1,
      domain: 'energy',
      priority: 'low'
    });
    
    return recs;
  };

  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'energy':
        return <Bolt />;
      case 'water':
        return <Opacity />;
      case 'waste':
        return <Delete />;
      case 'biodiversity':
        return <Nature />;
      default:
        return <Bolt />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error.main';
      case 'medium':
        return 'warning.main';
      case 'low':
        return 'success.main';
      default:
        return 'info.main';
    }
  };

  const handleViewRecommendationDetails = (id: string) => {
    // Navigate to recommendation details page
    navigate(`/recommendations/${id}`);
  };

  const handleStartNewAudit = () => {
    setActiveStep(0);
    setAuditComplete(false);
    setAuditData({});
    setRecommendations([]);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" gutterBottom>
        Audit de durabilité
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      <Box>
        {activeStep === 3 ? (
          // Recommendations step
          <>
            <Alert severity="success" sx={{ mb: 3 }}>
              Audit terminé avec succès ! Voici les recommandations personnalisées basées sur vos informations.
            </Alert>
            
            <Grid container spacing={3}>
              {recommendations.map((rec) => (
                <Grid item xs={12} md={6} key={rec.id}>
                  <Card>
                    <CardHeader
                      avatar={getDomainIcon(rec.domain)}
                      title={rec.title}
                      subheader={`Économies estimées: ${rec.savings}€/an • Retour sur investissement: ${rec.roi} ans`}
                      action={
                        <Box 
                          sx={{ 
                            width: 12, 
                            height: 12, 
                            borderRadius: '50%', 
                            bgcolor: getPriorityColor(rec.priority),
                            mr: 1
                          }} 
                        />
                      }
                    />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        {rec.description}
                      </Typography>
                      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                        <Button 
                          size="small" 
                          onClick={() => handleViewRecommendationDetails(rec.id)}
                        >
                          Voir les détails
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
            
            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
              <Button 
                variant="contained" 
                onClick={handleStartNewAudit}
                sx={{ mr: 2 }}
              >
                Démarrer un nouvel audit
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => navigate('/dashboard')}
              >
                Retour au tableau de bord
              </Button>
            </Box>
          </>
        ) : (
          // Audit assistant steps
          <Box>
            <VoiceAuditAssistant 
              userId={user?.id || 'guest'}
              initialAgentType={
                activeStep === 0 ? 'profile' : 
                activeStep === 1 ? 'consumption' : 'property'
              }
              onAuditComplete={handleAuditComplete}
            />
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                * Vous pouvez utiliser votre microphone ou taper vos réponses. L'assistant vous guidera à travers le processus d'audit.
              </Typography>
            </Box>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default AuditPage;

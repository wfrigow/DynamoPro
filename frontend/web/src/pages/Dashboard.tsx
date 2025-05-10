import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  LinearProgress,
  Divider,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  EmojiEvents,
  Euro,
  Bolt,
  WaterDrop,
  Co2,
  QueryBuilder,
  ChevronRight,
  ArrowCircleRight,
  VisibilityOutlined,
  SvgIconComponent,
} from '@mui/icons-material';
import { Chart as ChartJS, ArcElement, Tooltip as ChartTooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { selectAuth } from '../store/slices/authSlice';

// Register ChartJS components
ChartJS.register(ArcElement, ChartTooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement);

const Dashboard: React.FC = () => {
  const { user } = useSelector(selectAuth);
  const navigate = useNavigate();
  
  // Mock data - In real app, this would come from API/Redux
  const greenPassportScore = 65; // Out of 100
  const totalSavings = 2380; // in EUR
  const energySavings = 4500; // in kWh
  const waterSavings = 120; // in m3
  const co2Reduction = 1850; // in kg
  const roi = 2.5; // in years
  
  // Mock recommendations
  const topRecommendations = [
    {
      id: '1',
      title: 'Installation de panneaux solaires',
      savings: 1200,
      roi: 5,
      icon: Bolt,
      status: 'new',
      subsidies: 3,
    },
    {
      id: '2',
      title: 'Isolation du toit',
      savings: 800,
      roi: 3,
      icon: Bolt,
      status: 'in_progress',
      subsidies: 2,
    },
    {
      id: '3',
      title: "Système de récupération d'eau de pluie",
      savings: 350,
      roi: 4,
      icon: WaterDrop,
      status: 'new',
      subsidies: 1,
    },
  ];
  
  // Subsidy data
  const subsidyData = {
    applied: 2,
    approved: 1,
    pending: 1,
    available: 5,
    potentialAmount: 4500,
  };
  
  // Chart data for savings breakdown
  const savingsChartData = {
    labels: ['Électricité', 'Chauffage', 'Eau'],
    datasets: [
      {
        data: [30, 50, 20],
        backgroundColor: ['#1976d2', '#e53935', '#43a047'],
        borderColor: ['#1976d2', '#e53935', '#43a047'],
        borderWidth: 1,
      },
    ],
  };
  
  // Monthly savings data
  const monthlySavingsData = {
    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jui'],
    datasets: [
      {
        label: 'Économies (€)',
        data: [120, 190, 230, 250, 300, 350],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
      },
    ],
  };
  
  // Function to get status chip color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new':
        return 'primary';
      case 'in_progress':
        return 'warning';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };
  
  // Function to get status label
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'new':
        return 'Nouveau';
      case 'in_progress':
        return 'En cours';
      case 'completed':
        return 'Complété';
      default:
        return status;
    }
  };
  
  return (
    <Box>
      {/* Welcome Banner */}
      <Paper
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          background: 'linear-gradient(90deg, #2E7D32 0%, #1B5E20 100%)',
          color: 'white',
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h4" component="h1" gutterBottom>
              Bonjour, {user?.name || 'Utilisateur'}
            </Typography>
            <Typography variant="body1" paragraph>
              Bienvenue sur votre tableau de bord DynamoPro. Découvrez vos opportunités d'économies
              et votre impact environnemental en un coup d'œil.
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              endIcon={<ArrowCircleRight />}
              sx={{ mt: 1, backgroundColor: 'white', color: 'primary.main' }}
              onClick={() => navigate('/recommendations')}
            >
              Voir toutes mes recommandations
            </Button>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
            <Box sx={{ position: 'relative', display: 'inline-block' }}>
              <Box
                sx={{
                  width: 120,
                  height: 120,
                  borderRadius: '50%',
                  border: '10px solid rgba(255,255,255,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  position: 'relative',
                }}
              >
                <Typography variant="h4" component="div" fontWeight="bold">
                  {greenPassportScore}
                </Typography>
              </Box>
              <EmojiEvents
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  right: 0,
                  fontSize: 40,
                  color: '#FFD700',
                  background: '#2E7D32',
                  borderRadius: '50%',
                  p: '4px',
                }}
              />
              <Typography variant="body2" sx={{ mt: 1, fontWeight: 'medium' }}>
                Score Passeport Vert
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Économies Totales
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Euro color="primary" sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h4" component="div">
                  {totalSavings}€
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                depuis le début de vos actions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Énergie Économisée
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Bolt color="primary" sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h4" component="div">
                  {energySavings} kWh
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                équivalent à 450 jours d'usage moyen
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Eau Économisée
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WaterDrop color="primary" sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h4" component="div">
                  {waterSavings} m³
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                équivalent à 1200 douches
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Réduction CO₂
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Co2 color="primary" sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h4" component="div">
                  {co2Reduction} kg
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                équivalent à 10 000 km en voiture
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Dashboard Content */}
      <Grid container spacing={3}>
        {/* Top Recommendations */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommandations Prioritaires
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List sx={{ width: '100%' }}>
                {topRecommendations.map((rec, index) => {
                  const Icon = rec.icon;
                  return (
                    <React.Fragment key={rec.id}>
                      {index > 0 && <Divider component="li" />}
                      <ListItem alignItems="flex-start">
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: rec.icon === WaterDrop ? 'secondary.main' : 'primary.main' }}>
                            <Icon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Typography variant="subtitle1" component="span">
                                {rec.title}
                              </Typography>
                              <Chip
                                label={getStatusLabel(rec.status)}
                                color={getStatusColor(rec.status) as any}
                                size="small"
                                sx={{ ml: 1 }}
                              />
                            </Box>
                          }
                          secondary={
                            <>
                              <Typography component="span" variant="body2" color="textPrimary">
                                Économies: {rec.savings}€/an
                              </Typography>
                              {' — '}
                              <Typography component="span" variant="body2" color="textSecondary">
                                ROI: {rec.roi} ans
                              </Typography>
                              {' — '}
                              <Typography component="span" variant="body2" color="primary">
                                {rec.subsidies} subvention{rec.subsidies > 1 ? 's' : ''} disponible{rec.subsidies > 1 ? 's' : ''}
                              </Typography>
                            </>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Tooltip title="Voir les détails">
                            <IconButton edge="end" onClick={() => navigate(`/recommendations/${rec.id}`)}>
                              <ChevronRight />
                            </IconButton>
                          </Tooltip>
                        </ListItemSecondaryAction>
                      </ListItem>
                    </React.Fragment>
                  );
                })}
              </List>
            </CardContent>
            <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
              <Button 
                variant="outlined" 
                endIcon={<ArrowCircleRight />}
                onClick={() => navigate('/recommendations')}
              >
                Voir toutes les recommandations
              </Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Subsidies & ROI */}
        <Grid item xs={12} md={6}>
          <Grid container spacing={3}>
            {/* Subsidies summary */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Subventions
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h3" color="primary" gutterBottom>
                          {subsidyData.potentialAmount}€
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Montant potentiel de subventions
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">Demandées</Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {subsidyData.applied}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">Approuvées</Typography>
                          <Typography variant="body2" fontWeight="medium" color="success.main">
                            {subsidyData.approved}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">En attente</Typography>
                          <Typography variant="body2" fontWeight="medium" color="warning.main">
                            {subsidyData.pending}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2">Disponibles</Typography>
                          <Typography variant="body2" fontWeight="medium" color="info.main">
                            {subsidyData.available}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="outlined" 
                    endIcon={<ArrowCircleRight />}
                    onClick={() => navigate('/subsidies')}
                  >
                    Explorer les subventions
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            {/* ROI & Savings Charts */}
            <Grid item xs={12} sm={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Répartition des économies
                  </Typography>
                  <Box sx={{ height: 200, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <Doughnut data={savingsChartData} options={{ maintainAspectRatio: false }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Retour sur investissement
                  </Typography>
                  <Box sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h3" color="primary">
                      {roi} ans
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      ROI moyen de vos projets
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2 }}>
                      <QueryBuilder color="primary" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        Récupération de votre investissement d'ici {new Date().getFullYear() + Math.floor(roi)}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Monthly Savings Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Évolution des économies mensuelles
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ height: 300 }}>
                <Bar
                  data={monthlySavingsData}
                  options={{
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        title: {
                          display: true,
                          text: 'Économies (€)',
                        },
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Divider,
  Chip,
  Button,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Bolt as EnergyIcon,
  WaterDrop as WaterIcon,
  Co2 as CO2Icon,
  Euro as EuroIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from '@mui/icons-material';

const GreenPassport: React.FC = () => {
  // Mock data
  const passportData = {
    score: 65,
    label: 'Silver',
    issuedDate: '2025-05-01',
    validUntil: '2026-05-01',
    energySavingsKwh: 4500,
    waterSavingsM3: 120,
    costSavingsTotal: 2380,
    co2SavingsKg: 1850,
    completedProjects: [
      { id: 'project-1', title: 'Installation de panneaux solaires' },
      { id: 'project-4', title: 'Remplacement des ampoules par LED' },
    ],
  };

  // Function to get label color
  const getLabelColor = (label: string) => {
    switch (label) {
      case 'Bronze':
        return '#CD7F32';
      case 'Silver':
        return '#C0C0C0';
      case 'Gold':
        return '#FFD700';
      default:
        return '#C0C0C0';
    }
  };

  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Passeport Vert
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Votre Passeport Vert documente et valorise vos efforts en matière de durabilité.
          Il peut être partagé avec différentes parties prenantes pour démontrer votre engagement.
        </Typography>
      </Paper>

      {/* Main Passport Card */}
      <Card sx={{ mb: 4, overflow: 'visible', position: 'relative' }}>
        <Box
          sx={{
            position: 'absolute',
            top: -25,
            right: 20,
            width: 80,
            height: 80,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: getLabelColor(passportData.label),
            boxShadow: 3,
          }}
        >
          <Box sx={{ textAlign: 'center' }}>
            <TrophyIcon sx={{ color: 'white', fontSize: 30 }} />
            <Typography variant="subtitle2" color="white" fontWeight="bold">
              {passportData.label}
            </Typography>
          </Box>
        </Box>

        <CardContent sx={{ p: 4 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h4" gutterBottom>
                Passeport Vert
              </Typography>
              <Typography variant="body1" paragraph>
                Ce document certifie l'impact positif de vos actions durables sur l'environnement
                et atteste des économies réalisées.
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Score global
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ flexGrow: 1, mr: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={passportData.score}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </Box>
                  <Typography variant="h6">{passportData.score}/100</Typography>
                </Box>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Émis le: {passportData.issuedDate} | Valide jusqu'au: {passportData.validUntil}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <EnergyIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="subtitle2">Énergie économisée</Typography>
                      </Box>
                      <Typography variant="h6">{passportData.energySavingsKwh} kWh</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <WaterIcon sx={{ mr: 1, color: 'secondary.main' }} />
                        <Typography variant="subtitle2">Eau économisée</Typography>
                      </Box>
                      <Typography variant="h6">{passportData.waterSavingsM3} m³</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <EuroIcon sx={{ mr: 1, color: 'success.main' }} />
                        <Typography variant="subtitle2">Économies financières</Typography>
                      </Box>
                      <Typography variant="h6">{passportData.costSavingsTotal} €</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <CO2Icon sx={{ mr: 1, color: 'error.main' }} />
                        <Typography variant="subtitle2">Réduction CO₂</Typography>
                      </Box>
                      <Typography variant="h6">{passportData.co2SavingsKg} kg</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Projects Section */}
      <Typography variant="h6" gutterBottom>
        Projets Complétés
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        {passportData.completedProjects.map((project, index) => (
          <React.Fragment key={project.id}>
            {index > 0 && <Divider sx={{ my: 2 }} />}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="subtitle1">{project.title}</Typography>
                <Chip
                  label="Vérifié"
                  color="success"
                  size="small"
                  sx={{ mt: 0.5 }}
                />
              </Box>
              <Button size="small" color="primary">
                Voir détails
              </Button>
            </Box>
          </React.Fragment>
        ))}
      </Paper>

      {/* Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button 
          variant="contained" 
          startIcon={<DownloadIcon />}
          sx={{ mr: 2 }}
        >
          Télécharger le PDF
        </Button>
        <Button 
          variant="outlined" 
          startIcon={<ShareIcon />}
        >
          Partager
        </Button>
      </Box>
    </Box>
  );
};

export default GreenPassport;

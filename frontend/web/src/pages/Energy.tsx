import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Energy: React.FC = () => {
  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Gestion de l'Énergie
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Cette page permet de suivre et d'analyser votre consommation énergétique.
          (Page en cours de développement)
        </Typography>
      </Paper>
    </Box>
  );
};

export default Energy;

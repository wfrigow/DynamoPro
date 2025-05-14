import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Euro, TrendingUp } from '@mui/icons-material';
import { API_CONFIG } from '../config/api'; // Importer la configuration d'API
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Avatar,
  Divider,
  Paper,
  Tab,
  Tabs,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
} from '@mui/material';
import {
  Bolt as EnergyIcon,
  WaterDrop as WaterIcon,
  Delete as WasteIcon,
  Park as BiodiversityIcon,
  Euro as SubsidyIcon,
  Business as SupplierIcon,
  TrendingUp as ROIIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

// Interface pour les recommandations
interface Recommendation {
  id: string;
  title: string;
  description: string;
  domain: 'energy' | 'water' | 'waste' | 'biodiversity';
  priorityScore: number;
  estimatedCostMin: number;
  estimatedCostMax: number;
  estimatedSavingsPerYear: number;
  estimatedRoiMonths: number;
  ecologicalImpactScore: number; // 1-10
  difficulty: number; // 1-10
  applicableSubsidies: string[];
  status: 'pending' | 'accepted' | 'rejected' | 'completed';
}

// Interface pour les données d'audit simplifiées
interface SimplifiedAuditData {
  userType?: string;
  region?: string;
  electricityUsage?: number;
  gasUsage?: boolean;
  gasConsumption?: number;
  propertyType?: string;
  area?: number;
  constructionYear?: number;
  insulationStatus?: string;
}

interface SimplifiedAudit {
  timestamp: string;
  data: SimplifiedAuditData;
}

const Recommendations: React.FC = () => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);

  const handleFetchError = useCallback((error: unknown) => {
    console.error("Erreur lors de la récupération des recommandations:", error);
    console.log("Utilisation de données fictives suite à une erreur");
    const mockRecommendations: Recommendation[] = [
      {
        id: 'mock-1',
        title: 'Isoler votre toiture',
        description: 'Réduisez vos pertes de chaleur en isolant votre toiture.',
        domain: 'energy',
        priorityScore: 8,
        estimatedCostMin: 2000,
        estimatedCostMax: 5000,
        estimatedSavingsPerYear: 300,
        estimatedRoiMonths: 24,
        ecologicalImpactScore: 7,
        difficulty: 5,
        applicableSubsidies: ['Prime Energie'],
        status: 'pending'
      },
      // Add more mock data if needed
    ];
    setRecommendations(mockRecommendations);
    setLoading(false);
  }, []);

  const fetchRecommendationsFromAPI = useCallback(async (simplifiedAudit: SimplifiedAudit, token: string | null) => {
    try {
      console.log("Envoi des données d'audit pour recommandations:", simplifiedAudit.data);
      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.recommendations.simple}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token || 'test-token'}`
        },
        body: JSON.stringify(simplifiedAudit.data)
      });
      if (!response.ok) {
        throw new Error(`Erreur lors de la récupération des recommandations: ${response.status}`);
      }
      const result = await response.json();
      const normalizedRecommendations = result.recommendations.map((rec: any) => ({
        id: rec.id || `rec-${Math.random().toString(36).substring(2, 9)}`,
        title: rec.title,
        description: rec.description,
        domain: rec.domain,
        priorityScore: rec.priority_score,
        estimatedCostMin: rec.estimated_cost_min,
        estimatedCostMax: rec.estimated_cost_max,
        estimatedSavingsPerYear: rec.estimated_savings_per_year,
        estimatedRoiMonths: rec.estimated_roi_months,
        ecologicalImpactScore: rec.ecological_impact_score,
        difficulty: rec.difficulty,
        applicableSubsidies: rec.applicable_subsidies || [],
        status: rec.status || 'pending'
      }));
      setRecommendations(normalizedRecommendations);
      setLoading(false);
    } catch (err) {
      handleFetchError(err);
    }
  }, [handleFetchError]);

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      const { getAuditData } = await import('../utils/auditStorage');
      const userId = localStorage.getItem('userId');
      console.log("UserId récupéré:", userId);
      const token = localStorage.getItem('token');
      console.log("Token disponible:", !!token);
      if (!userId || !token) {
        console.warn("Utilisateur non authentifié - utilisation de valeurs de test pour le développement");
      }
      const auditData = getAuditData();
      if (auditData) {
        console.log("Données d'audit trouvées:", auditData);
        await fetchRecommendationsFromAPI(auditData, token);
        return;
      }
      setLoading(false);
      setRecommendations([]);
      alert("Aucun audit n'a été trouvé. Veuillez effectuer un audit vocal pour obtenir des recommandations personnalisées.");
      navigate('/audit');
    } catch (error) {
      handleFetchError(error);
    }
  }, [navigate, fetchRecommendationsFromAPI, handleFetchError]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleOpenDetails = (recommendation: Recommendation) => {
    setSelectedRecommendation(recommendation);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
  };

  const filteredRecommendations = recommendations.filter(rec => {
    if (activeTab === 0) return true; // All
    if (activeTab === 1) return rec.domain === 'energy';
    if (activeTab === 2) return rec.domain === 'water';
    if (activeTab === 3) return rec.domain === 'waste';
    if (activeTab === 4) return rec.domain === 'biodiversity';
    return false;
  });

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Recommandations personnalisées
      </Typography>
      
      <Typography variant="body1" paragraph>
        Basées sur votre audit énergétique, voici les recommandations les plus pertinentes pour réduire votre consommation et votre impact environnemental.
      </Typography>
      
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<FilterIcon />} label="Toutes" />
          <Tab icon={<EnergyIcon />} label="Énergie" />
          <Tab icon={<WaterIcon />} label="Eau" />
          <Tab icon={<WasteIcon />} label="Déchets" />
          <Tab icon={<BiodiversityIcon />} label="Biodiversité" />
        </Tabs>
      </Paper>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}>
          <CircularProgress />
        </Box>
      ) : filteredRecommendations.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6">
            Aucune recommandation trouvée pour cette catégorie
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Essayez une autre catégorie ou effectuez un nouvel audit pour obtenir des recommandations personnalisées.
          </Typography>
          <Button 
            variant="contained" 
            sx={{ mt: 2 }}
            onClick={() => navigate('/audit')}
          >
            Nouvel audit
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredRecommendations.map((recommendation) => (
            <Grid item xs={12} sm={6} md={4} key={recommendation.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Avatar 
                      sx={{ 
                        bgcolor: 
                          recommendation.domain === 'energy' ? 'error.main' : 
                          recommendation.domain === 'water' ? 'info.main' : 
                          recommendation.domain === 'waste' ? 'warning.main' : 
                          'success.main'
                      }}
                    >
                      {recommendation.domain === 'energy' && <EnergyIcon />}
                      {recommendation.domain === 'water' && <WaterIcon />}
                      {recommendation.domain === 'waste' && <WasteIcon />}
                      {recommendation.domain === 'biodiversity' && <BiodiversityIcon />}
                    </Avatar>
                    <Chip 
                      label={`Priorité: ${recommendation.priorityScore}/100`}
                      color={
                        recommendation.priorityScore > 80 ? 'error' :
                        recommendation.priorityScore > 60 ? 'warning' :
                        'success'
                      }
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="h6" component="h2" gutterBottom>
                    {recommendation.title}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {recommendation.description}
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Euro fontSize="small" color="primary" />
                        <Typography variant="body2" sx={{ ml: 0.5 }}>
                          {recommendation.estimatedCostMin} - {recommendation.estimatedCostMax}€
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TrendingUp fontSize="small" color="success" />
                        <Typography variant="body2" sx={{ ml: 0.5 }}>
                          {recommendation.estimatedSavingsPerYear}€/an
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" display="block">
                      Difficulté:
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress
                        variant="determinate"
                        value={recommendation.difficulty * 10}
                        color={
                          recommendation.difficulty <= 3 ? 'success' :
                          recommendation.difficulty <= 7 ? 'warning' :
                          'error'
                        }
                        sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                      />
                      <Typography variant="caption" sx={{ ml: 1 }}>
                        {recommendation.difficulty}/10
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
                
                <Box sx={{ p: 2, pt: 0 }}>
                  <Button 
                    variant="outlined" 
                    fullWidth
                    onClick={() => handleOpenDetails(recommendation)}
                  >
                    Voir détails
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {selectedRecommendation && (
        <Dialog
          open={detailsOpen}
          onClose={handleCloseDetails}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar 
                sx={{ 
                  bgcolor: 
                    selectedRecommendation.domain === 'energy' ? 'error.main' : 
                    selectedRecommendation.domain === 'water' ? 'info.main' : 
                    selectedRecommendation.domain === 'waste' ? 'warning.main' : 
                    'success.main',
                  mr: 2
                }}
              >
                {selectedRecommendation.domain === 'energy' && <EnergyIcon />}
                {selectedRecommendation.domain === 'water' && <WaterIcon />}
                {selectedRecommendation.domain === 'waste' && <WasteIcon />}
                {selectedRecommendation.domain === 'biodiversity' && <BiodiversityIcon />}
              </Avatar>
              <Typography variant="h6">{selectedRecommendation.title}</Typography>
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            <Typography variant="body1" paragraph>
              {selectedRecommendation.description}
            </Typography>
            
            <Typography variant="h6" gutterBottom>Coûts et économies</Typography>
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      Coût estimé
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <SubsidyIcon color="primary" />
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {selectedRecommendation.estimatedCostMin} - {selectedRecommendation.estimatedCostMax}€
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      Économies annuelles
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <TrendingUp color="success" />
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {selectedRecommendation.estimatedSavingsPerYear}€/an
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      Retour sur investissement
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <ROIIcon color="info" />
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {Math.floor(selectedRecommendation.estimatedRoiMonths / 12)} ans {selectedRecommendation.estimatedRoiMonths % 12} mois
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Typography variant="h6" gutterBottom>Impact et difficulté</Typography>
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" gutterBottom>
                  Impact écologique
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress
                    variant="determinate"
                    value={selectedRecommendation.ecologicalImpactScore * 10}
                    color="success"
                    sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                  />
                  <Typography variant="body2" sx={{ ml: 2, minWidth: 30 }}>
                    {selectedRecommendation.ecologicalImpactScore}/10
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" gutterBottom>
                  Difficulté de mise en œuvre
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress
                    variant="determinate"
                    value={selectedRecommendation.difficulty * 10}
                    color={
                      selectedRecommendation.difficulty <= 3
                        ? 'success'
                        : selectedRecommendation.difficulty <= 7
                        ? 'warning'
                        : 'error'
                    }
                    sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                  />
                  <Typography variant="body2" sx={{ ml: 2, minWidth: 30 }}>
                    {selectedRecommendation.difficulty}/10
                  </Typography>
                </Box>
              </Grid>
            </Grid>
            
            <Typography variant="h6" gutterBottom>Subventions applicables</Typography>
            {selectedRecommendation.applicableSubsidies.length > 0 ? (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Nom</TableCell>
                      <TableCell>Organisme</TableCell>
                      <TableCell align="right">Montant max</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedRecommendation.applicableSubsidies.map((subsidy) => (
                      <TableRow key={subsidy}>
                        <TableCell>Prime Énergie - Isolation Toiture</TableCell>
                        <TableCell>Région Wallonne</TableCell>
                        <TableCell align="right">2000€</TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            onClick={() => navigate('/subsidies')}
                          >
                            Détails
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Aucune subvention applicable n'a été trouvée pour cette recommandation.
              </Typography>
            )}
            
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>Fournisseurs recommandés</Typography>
              <Typography variant="body2" paragraph>
                Ces fournisseurs qualifiés peuvent réaliser les travaux nécessaires pour cette recommandation.
              </Typography>
              
              <Button
                variant="outlined"
                startIcon={<SupplierIcon />}
                onClick={() => navigate('/suppliers')}
              >
                Trouver des fournisseurs
              </Button>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDetails}>Fermer</Button>
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => {
                handleCloseDetails();
                // In a real app, would update the recommendation status
              }}
            >
              Je suis intéressé(e)
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default Recommendations;

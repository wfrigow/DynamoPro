import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Tabs, 
  Tab, 
  Paper, 
  CircularProgress, 
  Button, 
  Divider,
  Breadcrumbs,
  Link,
  Alert,
  IconButton,
  Grid,
  TextField
} from '@mui/material';
import { 
  Add, 
  ListAlt, 
  Refresh, 
  NavigateNext,
  Search,
  FilterList
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router-dom';
import SubsidiesList from '../components/subsidies/SubsidiesList';
import { SubsidyType } from '../components/subsidies/SubsidyCard';
import subsidyService, { Subsidy, SubsidySearchParams } from '../services/SubsidyService';
import { applicationService } from '../services/ApplicationService';
import SubsidyFilters, { ISubsidyFilters as SubsidyFiltersType } from '../components/subsidies/SubsidyFilters';
import { notificationService } from '../services/NotificationService';
import { useSelector } from 'react-redux';
import { selectUser } from '../store/slices/authSlice';

// Interface pour le suivi des applications
interface ApplicationTracker {
  id: string;
  subsidyId: string;
  subsidyName: string;
  status: 'draft' | 'submitted' | 'processing' | 'approved' | 'rejected' | 'additional_info';
  submissionDate: string;
  lastUpdated: string;
  documents: {
    required: number;
    uploaded: number;
    validated: number;
  };
  notes?: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`subsidies-tabpanel-${index}`}
      aria-labelledby={`subsidies-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const SubsidiesPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [subsidies, setSubsidies] = useState<SubsidyType[]>([]);
  const [applications, setApplications] = useState<ApplicationTracker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const [urlParams, setUrlParams] = useSearchParams();
  const user = useSelector(selectUser);

  // État pour les filtres avancés
  const [filters, setFilters] = useState<SubsidyFiltersType>({
    searchTerm: urlParams.get('query') || '',
    categories: urlParams.getAll('categories') || [],
    regions: urlParams.getAll('regions') || [],
    minAmount: urlParams.get('minAmount') ? Number(urlParams.get('minAmount')) : null,
    maxAmount: urlParams.get('maxAmount') ? Number(urlParams.get('maxAmount')) : null,
    deadlineRange: urlParams.get('deadlineRange') ? Number(urlParams.get('deadlineRange')) : 365,
    targetAudiences: urlParams.getAll('targetAudiences') || [],
    sortBy: (urlParams.get('sortBy') as 'relevance' | 'amount' | 'deadline' | 'popularity') || 'relevance',
    sortOrder: (urlParams.get('sortOrder') as 'asc' | 'desc') || 'desc'
  });

  // Mettre à jour les paramètres d'URL lorsque les filtres changent
  useEffect(() => {
    const newParams = new URLSearchParams();
    
    if (filters.searchTerm) newParams.set('query', filters.searchTerm);
    
    filters.categories.forEach(category => {
      newParams.append('categories', category);
    });
    
    filters.regions.forEach(region => {
      newParams.append('regions', region);
    });
    
    filters.targetAudiences.forEach(audience => {
      newParams.append('targetAudiences', audience);
    });
    
    if (filters.minAmount) newParams.set('minAmount', filters.minAmount.toString());
    if (filters.maxAmount) newParams.set('maxAmount', filters.maxAmount.toString());
    if (filters.deadlineRange) newParams.set('deadlineRange', filters.deadlineRange.toString());
    
    newParams.set('sortBy', filters.sortBy);
    newParams.set('sortOrder', filters.sortOrder);
    
    setUrlParams(newParams);

    // Cette partie n'est plus nécessaire car nous utilisons maintenant le composant SubsidyFilters
    // qui gère lui-même l'affichage des filtres
  }, []);

  // Charger les données depuis l'API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Construire les paramètres de recherche à partir des filtres
        const params: SubsidySearchParams = {
          language: 'fr',
          query: filters.searchTerm,
          regions: filters.regions,
          domains: filters.categories, // Mapper les catégories aux domaines
          user_types: filters.targetAudiences,
          min_amount: filters.minAmount !== null ? filters.minAmount : undefined,
          max_amount: filters.maxAmount !== null ? filters.maxAmount : undefined
          // Les propriétés suivantes n'existent pas dans l'interface SubsidySearchParams
          // max_deadline_days, sort_by, sort_order
          // Nous allons donc les omettre pour l'instant
        };
        
        // Appeler l'API pour récupérer les subventions
        const subsidiesData = await subsidyService.searchSubsidies(params);
        
        // Transformer les données pour correspondre au format attendu par SubsidiesList
        const formattedSubsidies: SubsidyType[] = subsidiesData.results.map(subsidy => ({
          id: subsidy.id,
          name: subsidy.name || '',
          description: subsidy.description || '',
          provider: subsidy.provider || '',
          regions: subsidy.regions || [],
          maxAmount: subsidy.max_amount || null,
          percentage: subsidy.percentage || null,
          keywords: subsidy.keywords || [],
          eligibility: [] // Cette propriété n'existe pas dans le type Subsidy, nous initialisons donc un tableau vide
        }));
        
        setSubsidies(formattedSubsidies);
        
        // Récupérer les applications de l'utilisateur
        if (user && user.id) { 
          const applicationsData = await applicationService.getUserApplications(user.id);
          
          // Transformer les données de ApplicationResponse[] vers ApplicationTracker[]
          const formattedApplications: ApplicationTracker[] = applicationsData.map(app => ({
            id: app.id,
            subsidyId: app.subsidy.id || app.subsidy_id,
            subsidyName: app.subsidy ? app.subsidy.name : 'Subvention',
            status: app.status as 'draft' | 'submitted' | 'processing' | 'approved' | 'rejected' | 'additional_info',
            submissionDate: app.created_at || new Date().toISOString(),
            lastUpdated: app.updated_at || new Date().toISOString(),
            documents: {
              required: Array.isArray(app.documents) ? app.documents.length : 0, // Estimation du nombre de documents requis
              uploaded: Array.isArray(app.documents) ? app.documents.filter(doc => doc.status === 'uploaded' || doc.status === 'validated').length : 0,
              validated: Array.isArray(app.documents) ? app.documents.filter(doc => doc.status === 'validated').length : 0
            },
            notes: app.notes && app.notes.length > 0 ? app.notes[app.notes.length - 1].content : undefined
          }));
          
          setApplications(formattedApplications);
        } else {
          // Gérer le cas où user ou user.id n'est pas disponible, si nécessaire
          console.warn("User ID not available, cannot fetch user applications.");
          setApplications([]); // ou une autre valeur par défaut appropriée
        }
        
        // Afficher une notification si des filtres sont appliqués
        if (filters.searchTerm || filters.categories.length > 0 || filters.regions.length > 0 || 
            filters.targetAudiences.length > 0 || filters.minAmount || filters.maxAmount) {
          notificationService.info(
            `${formattedSubsidies.length} subvention(s) trouvée(s)`,
            'Résultats de recherche',
            3000
          );
        }
      } catch (err) {
        console.error('Erreur lors de la récupération des données:', err);
        setError('Impossible de charger les subventions. Veuillez réessayer plus tard.');
        notificationService.error('Impossible de charger les subventions. Veuillez réessayer plus tard.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [filters]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleApplyForSubsidy = (id: string) => {
    navigate(`/subsidies/apply/${id}`);
  };

  const handleLoadRecommendations = () => {
    // À implémenter: charger les recommandations personnalisées
  };

  // Gestionnaire pour les changements de filtres
  const handleFiltersChange = (newFilters: SubsidyFiltersType) => {
    setFilters(newFilters);
    // La mise à jour des paramètres d'URL est gérée par l'effet
  };
  
  const getStatusLabel = (status: string) => {
    switch(status) {
      case 'draft': return 'Brouillon';
      case 'submitted': return 'Soumis';
      case 'processing': return 'En traitement';
      case 'approved': return 'Approuvé';
      case 'rejected': return 'Rejeté';
      case 'additional_info': return 'Information supplémentaire requise';
      default: return 'Inconnu';
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'draft': return 'info';
      case 'submitted': return 'info';
      case 'processing': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'additional_info': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Breadcrumbs separator={<NavigateNext fontSize="small" />} aria-label="breadcrumb">
          <Link color="inherit" component={RouterLink} to="/dashboard">
            Tableau de bord
          </Link>
          <Typography color="text.primary">Subventions</Typography>
        </Breadcrumbs>
      </Box>
      
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Subventions
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<Refresh />}
          onClick={() => window.location.reload()}
        >
          Rafraîchir
        </Button>
      </Box>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Explorez les subventions disponibles pour vos projets de durabilité et suivez vos demandes en cours.
      </Typography>
      
      <Paper sx={{ mt: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<ListAlt />} 
            label="Subventions disponibles" 
            id="subsidies-tab-0" 
            aria-controls="subsidies-tabpanel-0" 
          />
          <Tab 
            icon={<Add />} 
            label="Mes demandes" 
            id="subsidies-tab-1" 
            aria-controls="subsidies-tabpanel-1" 
          />
        </Tabs>
        
        <TabPanel value={tabValue} index={0}>
          <Box mb={3}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  label="Rechercher"
                  variant="outlined"
                  value={filters.searchTerm}
                  onChange={(event) => handleFiltersChange({ ...filters, searchTerm: event.target.value })}
                  InputProps={{
                    endAdornment: (
                      <IconButton onClick={() => handleFiltersChange({ ...filters, searchTerm: '' })}>
                        <Search />
                      </IconButton>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={8}>
                <Box display="flex" justifyContent="flex-end">
                  <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<FilterList />}
                    onClick={() => handleFiltersChange(filters)}
                    sx={{ mr: 1 }}
                  >
                    Filtres
                  </Button>
                  <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<Refresh />}
                    onClick={handleLoadRecommendations}
                  >
                    Recommandations personnalisées
                  </Button>
                </Box>
              </Grid>
            </Grid>

            <SubsidyFilters 
              onFiltersChange={handleFiltersChange} 
              initialFilters={filters}
            />
          </Box>
          
          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
            <SubsidiesList 
              subsidies={subsidies} 
              onApply={handleApplyForSubsidy}
            />
          )}
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          {applications.length > 0 ? (
            <Box>
              {applications.map((app) => (
                <Paper key={app.id} sx={{ p: 3, mb: 2, border: '1px solid #e0e0e0' }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" color="primary">
                      {app.subsidyName}
                    </Typography>
                    <Alert 
                      severity={getStatusColor(app.status) as "success" | "info" | "warning" | "error"}
                      icon={false}
                      sx={{ py: 0 }}
                    >
                      {getStatusLabel(app.status)}
                    </Alert>
                  </Box>
                  
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box display="flex" flexWrap="wrap" gap={2} mb={2}>
                    {app.status !== 'draft' && (
                      <Typography variant="body2" color="text.secondary">
                        <strong>Soumis le:</strong> {app.submissionDate}
                      </Typography>
                    )}
                    <Typography variant="body2" color="text.secondary">
                      <strong>Dernière mise à jour:</strong> {app.lastUpdated}
                    </Typography>
                  </Box>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Documents:
                  </Typography>
                  <Box display="flex" gap={2} mb={2}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Requis:</strong> {app.documents.required}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Téléchargés:</strong> {app.documents.uploaded}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Validés:</strong> {app.documents.validated}
                    </Typography>
                  </Box>
                  
                  {app.notes && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      {app.notes}
                    </Typography>
                  )}
                  
                  <Box display="flex" justifyContent="flex-end" mt={2}>
                    <Button
                      variant="outlined"
                      color="primary"
                      component={RouterLink}
                      to={app.status === 'draft' 
                        ? `/subsidies/apply/${app.subsidyId}?applicationId=${app.id}` 
                        : `/subsidies/track/${app.id}`}
                    >
                      {app.status === 'draft' ? 'Continuer' : 'Voir les détails'}
                    </Button>
                  </Box>
                </Paper>
              ))}
            </Box>
          ) : (
            <Box textAlign="center" p={4}>
              <Typography variant="body1" color="text.secondary" paragraph>
                Vous n'avez pas encore de demandes de subvention en cours.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setTabValue(0)}
              >
                Explorer les subventions disponibles
              </Button>
            </Box>
          )}
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default SubsidiesPage;

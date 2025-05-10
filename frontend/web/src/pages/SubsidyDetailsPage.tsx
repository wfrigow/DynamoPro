import React, { useState, useEffect } from 'react';
import { 
  Container,
  Box,
  Typography,
  Paper,
  Breadcrumbs,
  Link,
  Button,
  Divider,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  CardActions,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  NavigateNext, 
  ArrowBack, 
  CheckCircle, 
  Euro, 
  InfoOutlined, 
  LocationOn, 
  BusinessCenter, 
  Description,
  ExpandMore,
  Assignment,
  OpenInNew
} from '@mui/icons-material';
import { Link as RouterLink, useParams, useNavigate } from 'react-router-dom';
import { SubsidyType } from '../components/subsidies/SubsidyCard';
import subsidyService, { SubsidyDetail } from '../services/SubsidyService';

const SubsidyDetailsPage: React.FC = () => {
  const { subsidyId } = useParams<{ subsidyId: string }>();
  const navigate = useNavigate();
  const [subsidy, setSubsidy] = useState<SubsidyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [similarSubsidies, setSimilarSubsidies] = useState<SubsidyType[]>([]);

  // Traduire les régions
  const getRegionName = (region: string): string => {
    const regionMap: {[key: string]: string} = {
      'wallonie': 'Wallonie',
      'bruxelles': 'Bruxelles',
      'flandre': 'Flandre',
      'federal': 'Fédéral'
    };
    return regionMap[region.toLowerCase()] || region;
  };

  useEffect(() => {
    const fetchSubsidyDetails = async () => {
      if (!subsidyId) {
        setError("ID de subvention non spécifié");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        
        // Récupérer les détails de la subvention depuis l'API
        const subsidyDetails = await subsidyService.getSubsidyById(subsidyId);
        setSubsidy(subsidyDetails);
        
        // Récupérer des subventions similaires (basées sur le domaine)
        if (subsidyDetails.domains && subsidyDetails.domains.length > 0) {
          const domainResponse = await subsidyService.getSubsidiesByDomain(subsidyDetails.domains[0]);
          
          // Filtrer pour exclure la subvention actuelle et limiter à 3 subventions similaires
          const filteredSimilarSubsidies = domainResponse.results
            .filter(sub => sub.id !== subsidyId)
            .slice(0, 3)
            .map(subsidy => ({
              id: subsidy.id,
              name: subsidy.name,
              description: subsidy.description,
              provider: subsidy.provider,
              regions: subsidy.regions,
              maxAmount: subsidy.max_amount,
              percentage: subsidy.percentage,
              keywords: subsidy.keywords,
              eligibility: []
            }));
          
          setSimilarSubsidies(filteredSimilarSubsidies);
        }
        
        setError(null);
      } catch (err) {
        console.error('Erreur lors du chargement des détails de la subvention:', err);
        setError('Une erreur est survenue lors du chargement des détails. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchSubsidyDetails();
  }, [subsidyId]);

  const handleApply = () => {
    if (subsidyId) {
      navigate(`/subsidies/apply/${subsidyId}`);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Breadcrumbs separator={<NavigateNext fontSize="small" />} aria-label="breadcrumb">
          <Link component={RouterLink} to="/" color="inherit">
            Accueil
          </Link>
          <Link component={RouterLink} to="/subsidies" color="inherit">
            Subventions
          </Link>
          <Typography color="text.primary">Détails</Typography>
        </Breadcrumbs>
      </Box>
      
      <Button
        startIcon={<ArrowBack />}
        variant="text"
        component={RouterLink}
        to="/subsidies"
        sx={{ mb: 3 }}
      >
        Retour aux subventions
      </Button>
      
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 4 }}>
          <AlertTitle>Erreur</AlertTitle>
          {error}
        </Alert>
      ) : subsidy ? (
        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
              <Box mb={3}>
                <Typography variant="h5" component="h1" gutterBottom>
                  {subsidy.name}
                </Typography>
                
                <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                  {subsidy.regions.map((region) => (
                    <Chip 
                      key={region} 
                      icon={<LocationOn />} 
                      label={getRegionName(region)} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  ))}
                  {subsidy.keywords.map((keyword) => (
                    <Chip 
                      key={keyword} 
                      label={keyword} 
                      size="small" 
                      variant="outlined"
                    />
                  ))}
                </Box>
                
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  Fournie par: {subsidy.provider}
                </Typography>
                
                <Typography variant="body1" paragraph>
                  {subsidy.description}
                </Typography>
                
                {subsidy.additional_info && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {subsidy.additional_info}
                  </Typography>
                )}
              </Box>
              
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Montant de la subvention
                </Typography>
                <Box display="flex" alignItems="center" mb={2}>
                  <Euro color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    {subsidy.max_amount 
                      ? `Jusqu'à ${subsidy.max_amount.toLocaleString()}€` 
                      : 'Montant variable'}
                    {subsidy.percentage && ` (${subsidy.percentage}% des coûts éligibles)`}
                  </Typography>
                </Box>
              </Box>
              
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Conditions d'éligibilité
                </Typography>
                {subsidy.conditions && (
                  <Typography variant="body2" paragraph>
                    {subsidy.conditions}
                  </Typography>
                )}
                <List>
                  {subsidy.eligibility.map((criterion, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={criterion} />
                    </ListItem>
                  ))}
                </List>
              </Box>
              
              {subsidy.documentation_url && (
                <Box mt={3}>
                  <Button
                    variant="outlined"
                    color="primary"
                    endIcon={<OpenInNew />}
                    component="a"
                    href={subsidy.documentation_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Documentation officielle
                  </Button>
                </Box>
              )}
              
              <Accordion defaultExpanded sx={{ mt: 3 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">Documents requis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {subsidy.required_documents && subsidy.required_documents.length > 0 ? (
                    <List>
                      {subsidy.required_documents.map((doc) => (
                        <ListItem key={doc.id} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <Assignment fontSize="small" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={doc.name} 
                            secondary={doc.description}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Aucun document spécifique n'est listé. Veuillez consulter la documentation officielle pour plus d'informations.
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>
              
              {subsidy.application_process && (
                <Accordion sx={{ mt: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Processus de demande</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2">
                      {subsidy.application_process}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              )}
              
              <Box mt={4} display="flex" justifyContent="center">
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={handleApply}
                >
                  Faire une demande
                </Button>
              </Box>
            </Paper>
            
            {similarSubsidies.length > 0 && (
              <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Subventions similaires
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Ces subventions pourraient également vous intéresser:
                </Typography>
                
                {similarSubsidies.map((sim) => (
                  <Card key={sim.id} variant="outlined" sx={{ mb: 2 }}>
                    <CardContent sx={{ pb: 1 }}>
                      <Typography variant="subtitle1" color="primary" gutterBottom noWrap>
                        {sim.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{
                        display: '-webkit-box',
                        overflow: 'hidden',
                        WebkitBoxOrient: 'vertical',
                        WebkitLineClamp: 2,
                      }}>
                        {sim.description}
                      </Typography>
                      
                      <Box mt={1} display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="caption" color="text.secondary">
                          {sim.provider}
                        </Typography>
                        {sim.maxAmount && (
                          <Chip 
                            size="small" 
                            label={`Jusqu'à ${sim.maxAmount.toLocaleString()}€`} 
                            color="primary"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        component={RouterLink} 
                        to={`/subsidies/details/${sim.id}`}
                      >
                        Voir les détails
                      </Button>
                    </CardActions>
                  </Card>
                ))}
              </Paper>
            )}
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ position: { md: 'sticky' }, top: { md: '100px' } }}>
              <Alert severity="info" sx={{ mb: 4 }}>
                <AlertTitle>Besoin d'aide ?</AlertTitle>
                Notre équipe est disponible pour vous aider dans vos démarches.
                <Box mt={2}>
                  <Button 
                    variant="outlined" 
                    color="info" 
                    size="small"
                    component={RouterLink}
                    to="/contact"
                  >
                    Nous contacter
                  </Button>
                </Box>
              </Alert>
              
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                    Évaluation de cette subvention
                  </Typography>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Popularité:
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      Élevée
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Taux d'acceptation:
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      85%
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Complexité:
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      Moyenne
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </Grid>
        </Grid>
      ) : (
        <Alert severity="warning">
          <AlertTitle>Subvention non trouvée</AlertTitle>
          La subvention que vous recherchez n'existe pas ou a été supprimée.
        </Alert>
      )}
    </Container>
  );
};

export default SubsidyDetailsPage;

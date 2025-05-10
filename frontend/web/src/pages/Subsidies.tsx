import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Tab,
  Tabs,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Euro,
  Assignment,
  AccountBalance,
  CheckCircle,
  ArrowForward,
  CalendarToday,
  Description,
  Bolt as EnergyIcon,
  WaterDrop as WaterIcon,
  Delete as WasteIcon,
  Park as BiodiversityIcon,
  InfoOutlined,
  CloudDownload,
} from '@mui/icons-material';

interface Subsidy {
  id: string;
  name: string;
  provider: string;
  description: string;
  domains: ('energy' | 'water' | 'waste' | 'biodiversity')[];
  maxAmount: number | null;
  percentage: number | null;
  conditions: string;
  documentationUrl: string;
  applicationProcess: string;
  expirationDate: string | null;
  active: boolean;
}

interface Application {
  id: string;
  subsidyId: string;
  subsidyName: string;
  status: 'draft' | 'submitted' | 'pending' | 'approved' | 'rejected';
  submissionDate: string | null;
  responseDate: string | null;
  amountRequested: number;
  amountApproved: number | null;
}

const Subsidies: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [subsidies, setSubsidies] = useState<Subsidy[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedSubsidy, setSelectedSubsidy] = useState<Subsidy | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [applicationOpen, setApplicationOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    // In a real application, this would be an API call
    const fetchData = async () => {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock subsidies data
      const mockSubsidies: Subsidy[] = [
        {
          id: 'subsidy-1',
          name: 'Prime Energie - Isolation Toiture',
          provider: 'Région Wallonne',
          description: 'Prime pour l\'isolation thermique du toit ou des combles dans une habitation existante.',
          domains: ['energy'],
          maxAmount: 2000,
          percentage: 35,
          conditions: 'Le coefficient de résistance thermique R doit être ≥ 4,5 m²K/W. Les travaux doivent être réalisés par un entrepreneur enregistré.',
          documentationUrl: 'https://energie.wallonie.be/fr/prime-isolation-du-toit.html',
          applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
          expirationDate: null,
          active: true
        },
        {
          id: 'subsidy-2',
          name: 'Prime Energie - Pompe à Chaleur',
          provider: 'Région Wallonne',
          description: 'Prime pour l\'installation d\'une pompe à chaleur pour le chauffage ou combiné eau chaude sanitaire.',
          domains: ['energy'],
          maxAmount: 4000,
          percentage: 30,
          conditions: 'La pompe à chaleur doit respecter des exigences minimales de performance. L\'installation doit être réalisée par un installateur certifié.',
          documentationUrl: 'https://energie.wallonie.be/fr/prime-pompe-a-chaleur.html',
          applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
          expirationDate: null,
          active: true
        },
        {
          id: 'subsidy-3',
          name: 'Prime Energie - Panneaux Photovoltaïques',
          provider: 'Région Wallonne',
          description: 'Prime pour l\'installation de panneaux photovoltaïques pour la production d\'électricité.',
          domains: ['energy'],
          maxAmount: 1500,
          percentage: 20,
          conditions: 'L\'installation doit être réalisée par un installateur certifié. Les panneaux doivent avoir un rendement minimal.',
          documentationUrl: 'https://energie.wallonie.be/fr/prime-photovoltaique.html',
          applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
          expirationDate: null,
          active: true
        },
        {
          id: 'subsidy-4',
          name: 'Primes Rénovation - Audit Énergétique',
          provider: 'Région Wallonne',
          description: 'Prime pour la réalisation d\'un audit énergétique par un auditeur agréé.',
          domains: ['energy'],
          maxAmount: 900,
          percentage: 70,
          conditions: 'L\'audit doit être réalisé par un auditeur agréé PAE (Procédure d\'Avis Énergétique).',
          documentationUrl: 'https://energie.wallonie.be/fr/audit-energetique.html',
          applicationProcess: 'Demande en ligne via le portail Energie de la Région Wallonne.',
          expirationDate: null,
          active: true
        },
        {
          id: 'subsidy-5',
          name: 'Prime Eau - Récupération Eau de Pluie',
          provider: 'Région Wallonne',
          description: 'Prime pour l\'installation d\'un système de récupération et d\'utilisation de l\'eau de pluie.',
          domains: ['water'],
          maxAmount: 1000,
          percentage: 25,
          conditions: 'La citerne doit avoir une capacité minimale de 5000 litres et être raccordée à au moins un WC ou un lave-linge.',
          documentationUrl: 'https://environnement.wallonie.be/eau/prime-eau-pluie.html',
          applicationProcess: 'Demande auprès de la commune ou de l\'intercommunale compétente.',
          expirationDate: null,
          active: true
        }
      ];
      
      // Mock applications data
      const mockApplications: Application[] = [
        {
          id: 'app-1',
          subsidyId: 'subsidy-1',
          subsidyName: 'Prime Energie - Isolation Toiture',
          status: 'approved',
          submissionDate: '2025-03-15',
          responseDate: '2025-04-02',
          amountRequested: 1800,
          amountApproved: 1650
        },
        {
          id: 'app-2',
          subsidyId: 'subsidy-3',
          subsidyName: 'Prime Energie - Panneaux Photovoltaïques',
          status: 'pending',
          submissionDate: '2025-04-28',
          responseDate: null,
          amountRequested: 1200,
          amountApproved: null
        },
        {
          id: 'app-3',
          subsidyId: 'subsidy-5',
          subsidyName: 'Prime Eau - Récupération Eau de Pluie',
          status: 'draft',
          submissionDate: null,
          responseDate: null,
          amountRequested: 800,
          amountApproved: null
        }
      ];
      
      setSubsidies(mockSubsidies);
      setApplications(mockApplications);
      setLoading(false);
    };
    
    fetchData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleOpenDetails = (subsidy: Subsidy) => {
    setSelectedSubsidy(subsidy);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
  };

  const handleStartApplication = () => {
    setDetailsOpen(false);
    setApplicationOpen(true);
    setActiveStep(0);
  };

  const handleCloseApplication = () => {
    setApplicationOpen(false);
  };

  const handleNextStep = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBackStep = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmitApplication = () => {
    // In a real app, this would submit the application to the backend
    setApplicationOpen(false);
    // Would add the new application to the state
  };

  // Filter subsidies based on active tab
  const filteredSubsidies = subsidies.filter(sub => {
    if (activeTab === 0) return true; // All
    if (activeTab === 1) return sub.domains.includes('energy');
    if (activeTab === 2) return sub.domains.includes('water');
    return true;
  });

  // Get domain icon
  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'energy':
        return <EnergyIcon />;
      case 'water':
        return <WaterIcon />;
      case 'waste':
        return <WasteIcon />;
      case 'biodiversity':
        return <BiodiversityIcon />;
      default:
        return <EnergyIcon />;
    }
  };

  // Get status chip
  const getStatusChip = (status: string) => {
    let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';
    let label = status;
    
    switch (status) {
      case 'draft':
        color = 'default';
        label = 'Brouillon';
        break;
      case 'submitted':
        color = 'info';
        label = 'Soumise';
        break;
      case 'pending':
        color = 'warning';
        label = 'En attente';
        break;
      case 'approved':
        color = 'success';
        label = 'Approuvée';
        break;
      case 'rejected':
        color = 'error';
        label = 'Rejetée';
        break;
    }
    
    return <Chip label={label} color={color} size="small" />;
  };

  // Application form steps
  const steps = ['Informations personnelles', 'Détails du projet', 'Documents requis', 'Vérification'];

  return (
    <Box>
      {/* Header Section */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Subventions et Aides Financières
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Découvrez toutes les subventions disponibles pour vos projets de durabilité.
          Notre système intelligent identifie automatiquement les aides adaptées à votre profil et vous 
          accompagne dans toutes les démarches administratives.
        </Typography>
        
        {/* Tabs for filtering */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 2 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="subsidy filters">
            <Tab label="Toutes" />
            <Tab 
              label="Énergie" 
              icon={<EnergyIcon />} 
              iconPosition="start"
            />
            <Tab 
              label="Eau" 
              icon={<WaterIcon />} 
              iconPosition="start"
            />
          </Tabs>
        </Box>
      </Paper>

      {/* Content */}
      <Grid container spacing={3}>
        {/* Subsidies Section */}
        <Grid item xs={12} lg={8}>
          <Typography variant="h6" gutterBottom>
            Subventions disponibles
          </Typography>
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {filteredSubsidies.map((subsidy) => (
                <Grid item xs={12} md={6} key={subsidy.id}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Chip 
                          icon={getDomainIcon(subsidy.domains[0])}
                          label={subsidy.domains[0] === 'energy' ? 'Énergie' : 'Eau'} 
                          color={subsidy.domains[0] === 'energy' ? 'primary' : 'secondary'}
                          size="small"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {subsidy.expirationDate ? `Expire: ${new Date(subsidy.expirationDate).toLocaleDateString()}` : 'Sans expiration'}
                        </Typography>
                      </Box>
                      
                      <Typography variant="h6" component="div" gutterBottom>
                        {subsidy.name}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Fournisseur:</strong> {subsidy.provider}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {subsidy.description.length > 100
                          ? `${subsidy.description.substring(0, 100)}...`
                          : subsidy.description}
                      </Typography>
                      
                      <Divider sx={{ my: 2 }} />
                      
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Montant max
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {subsidy.maxAmount ? `${subsidy.maxAmount}€` : 'N/A'}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Pourcentage
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {subsidy.percentage ? `${subsidy.percentage}%` : 'N/A'}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                    <Divider />
                    <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
                      <Button 
                        variant="outlined" 
                        size="small"
                        onClick={() => handleOpenDetails(subsidy)}
                      >
                        Voir les détails
                      </Button>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
          
          {!loading && filteredSubsidies.length === 0 && (
            <Box sx={{ textAlign: 'center', my: 5, py: 5 }}>
              <Typography variant="h6" gutterBottom>
                Aucune subvention trouvée
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Aucune subvention ne correspond aux filtres sélectionnés.
              </Typography>
            </Box>
          )}
        </Grid>
        
        {/* My Applications Section */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mes demandes
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {applications.length > 0 ? (
                <List>
                  {applications.map((application) => (
                    <React.Fragment key={application.id}>
                      <ListItem>
                        <ListItemIcon>
                          <Assignment />
                        </ListItemIcon>
                        <ListItemText
                          primary={application.subsidyName}
                          secondary={
                            <>
                              <Typography component="span" variant="body2" color="text.primary">
                                {getStatusChip(application.status)}
                              </Typography>
                              <Typography component="span" variant="body2" display="block">
                                {application.submissionDate ? 
                                  `Soumise le: ${new Date(application.submissionDate).toLocaleDateString()}` : 
                                  'Non soumise'}
                              </Typography>
                              <Typography component="span" variant="body2" display="block">
                                {application.amountRequested ? `Montant: ${application.amountRequested}€` : ''}
                              </Typography>
                            </>
                          }
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end">
                            <ArrowForward />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <Divider component="li" />
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" gutterBottom>
                    Vous n'avez pas encore de demandes de subvention.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Explorez les subventions disponibles et commencez une demande.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Subsidy Details Dialog */}
      {selectedSubsidy && (
        <Dialog
          open={detailsOpen}
          onClose={handleCloseDetails}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Typography variant="h6">{selectedSubsidy.name}</Typography>
          </DialogTitle>
          <DialogContent dividers>
            <Box sx={{ mb: 3 }}>
              <Chip 
                icon={<AccountBalance />}
                label={selectedSubsidy.provider}
                variant="outlined"
                sx={{ mr: 1 }}
              />
              {selectedSubsidy.domains.map((domain) => (
                <Chip 
                  key={domain}
                  icon={getDomainIcon(domain)}
                  label={domain === 'energy' ? 'Énergie' : 'Eau'} 
                  color={domain === 'energy' ? 'primary' : 'secondary'}
                  sx={{ mr: 1 }}
                />
              ))}
              {selectedSubsidy.active && (
                <Chip 
                  icon={<CheckCircle />}
                  label="Active"
                  color="success"
                />
              )}
            </Box>
            
            <Typography variant="body1" paragraph>
              {selectedSubsidy.description}
            </Typography>
            
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Montant maximum
                    </Typography>
                    <Typography variant="h5" color="primary">
                      {selectedSubsidy.maxAmount ? `${selectedSubsidy.maxAmount}€` : 'Non plafonné'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Pourcentage couvert
                    </Typography>
                    <Typography variant="h5" color="primary">
                      {selectedSubsidy.percentage ? `${selectedSubsidy.percentage}%` : 'Non spécifié'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Typography variant="h6" gutterBottom>Conditions</Typography>
            <Typography variant="body2" paragraph>
              {selectedSubsidy.conditions}
            </Typography>
            
            <Typography variant="h6" gutterBottom>Processus de demande</Typography>
            <Typography variant="body2" paragraph>
              {selectedSubsidy.applicationProcess}
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <Button
                variant="outlined"
                startIcon={<Description />}
                href={selectedSubsidy.documentationUrl}
                target="_blank"
                rel="noopener noreferrer"
                sx={{ mr: 2 }}
              >
                Documentation officielle
              </Button>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDetails}>Fermer</Button>
            <Button 
              variant="contained" 
              color="primary"
              onClick={handleStartApplication}
              startIcon={<Assignment />}
            >
              Démarrer une demande
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {/* Application Form Dialog */}
      {selectedSubsidy && (
        <Dialog
          open={applicationOpen}
          onClose={handleCloseApplication}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Typography variant="h6">Demande de subvention: {selectedSubsidy.name}</Typography>
          </DialogTitle>
          <DialogContent dividers>
            <Stepper activeStep={activeStep} sx={{ py: 3 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            <Box sx={{ mt: 3 }}>
              {activeStep === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>Informations personnelles</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Nom"
                        defaultValue="Doe"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Prénom"
                        defaultValue="John"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Adresse email"
                        defaultValue="john.doe@example.com"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Adresse"
                        defaultValue="123 Rue de l'Exemple"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Code postal"
                        defaultValue="4000"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Ville"
                        defaultValue="Liège"
                        margin="normal"
                      />
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {activeStep === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>Détails du projet</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Description du projet"
                        multiline
                        rows={4}
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Coût estimé (€)"
                        type="number"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Date de début prévue"
                        type="date"
                        margin="normal"
                        InputLabelProps={{
                          shrink: true,
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Nom de l'entrepreneur"
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Numéro de TVA de l'entrepreneur"
                        margin="normal"
                      />
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {activeStep === 2 && (
                <Box>
                  <Typography variant="h6" gutterBottom>Documents requis</Typography>
                  <Typography variant="body2" paragraph>
                    Veuillez télécharger les documents suivants pour compléter votre demande:
                  </Typography>
                  
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <CloudDownload />
                      </ListItemIcon>
                      <ListItemText
                        primary="Devis détaillé"
                        secondary="Format PDF, JPG ou PNG"
                      />
                      <Button variant="outlined" size="small">
                        Télécharger
                      </Button>
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CloudDownload />
                      </ListItemIcon>
                      <ListItemText
                        primary="Preuve d'identité"
                        secondary="Carte d'identité, format PDF, JPG ou PNG"
                      />
                      <Button variant="outlined" size="small">
                        Télécharger
                      </Button>
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CloudDownload />
                      </ListItemIcon>
                      <ListItemText
                        primary="Preuve de propriété"
                        secondary="Acte notarié ou bail, format PDF"
                      />
                      <Button variant="outlined" size="small">
                        Télécharger
                      </Button>
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CloudDownload />
                      </ListItemIcon>
                      <ListItemText
                        primary="Fiche technique des matériaux"
                        secondary="Format PDF"
                      />
                      <Button variant="outlined" size="small">
                        Télécharger
                      </Button>
                    </ListItem>
                  </List>
                </Box>
              )}
              
              {activeStep === 3 && (
                <Box>
                  <Typography variant="h6" gutterBottom>Vérification des informations</Typography>
                  <Typography variant="body2" paragraph>
                    Veuillez vérifier les informations suivantes avant de soumettre votre demande:
                  </Typography>
                  
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableBody>
                        <TableRow>
                          <TableCell component="th" variant="head">Subvention</TableCell>
                          <TableCell>{selectedSubsidy.name}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell component="th" variant="head">Demandeur</TableCell>
                          <TableCell>John Doe</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell component="th" variant="head">Adresse</TableCell>
                          <TableCell>123 Rue de l'Exemple, 4000 Liège</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell component="th" variant="head">Montant estimé</TableCell>
                          <TableCell>1250€</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell component="th" variant="head">Documents fournis</TableCell>
                          <TableCell>4/4</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  <Typography variant="body2" sx={{ mt: 3, fontStyle: 'italic' }}>
                    En soumettant cette demande, vous certifiez que toutes les informations fournies sont exactes.
                  </Typography>
                </Box>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button 
              onClick={handleCloseApplication}
              color="inherit"
            >
              Annuler
            </Button>
            {activeStep > 0 && (
              <Button onClick={handleBackStep}>
                Précédent
              </Button>
            )}
            {activeStep < steps.length - 1 ? (
              <Button 
                variant="contained" 
                onClick={handleNextStep}
              >
                Suivant
              </Button>
            ) : (
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleSubmitApplication}
              >
                Soumettre la demande
              </Button>
            )}
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default Subsidies;

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Stepper,
  Step,
  StepLabel,
  LinearProgress,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import {
  Bolt as EnergyIcon,
  WaterDrop as WaterIcon,
  Delete as WasteIcon,
  Park as BiodiversityIcon,
  Add as AddIcon,
  PhotoCamera as CameraIcon,
  Description as DocumentIcon,
  AttachMoney as CostIcon,
  CalendarToday as DateIcon,
  Check as VerifyIcon,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { selectProjects, Project } from '../store/slices/projectsSlice';
import { selectRecommendations } from '../store/slices/recommendationsSlice';
import { selectSuppliers } from '../store/slices/suppliersSlice';
// Format date manually for now
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
};

const Projects: React.FC = () => {
  const projects = useSelector(selectProjects);
  const recommendations = useSelector(selectRecommendations);
  const suppliers = useSelector(selectSuppliers);
  
  const [openDialog, setOpenDialog] = useState(false);
  const [openProjectDialog, setOpenProjectDialog] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  
  // New project state
  const [newProject, setNewProject] = useState({
    recommendationId: '',
    supplierId: '',
    startDate: '',
  });

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleOpenProjectDialog = (project: Project) => {
    setSelectedProject(project);
    setOpenProjectDialog(true);
  };

  const handleCloseProjectDialog = () => {
    setOpenProjectDialog(false);
    setSelectedProject(null);
  };

  const handleCreateProject = () => {
    // Here you would dispatch an action to create a project
    console.log('Creating project:', newProject);
    handleCloseDialog();
  };

  const handleSelectChange = (event: SelectChangeEvent<string>) => {
    const name = event.target.name as string;
    const value = event.target.value as string;
    setNewProject(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name as string;
    const value = event.target.value as string;
    setNewProject(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const getDomainIcon = (domain: string) => {
    switch(domain) {
      case 'energy':
        return <EnergyIcon sx={{ color: 'primary.main' }} />;
      case 'water':
        return <WaterIcon sx={{ color: 'info.main' }} />;
      case 'waste':
        return <WasteIcon sx={{ color: 'warning.main' }} />;
      case 'biodiversity':
        return <BiodiversityIcon sx={{ color: 'success.main' }} />;
      default:
        return <EnergyIcon sx={{ color: 'primary.main' }} />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch(status) {
      case 'planning':
        return { label: 'Planification', color: 'info' };
      case 'in_progress':
        return { label: 'En cours', color: 'warning' };
      case 'completed':
        return { label: 'Terminé', color: 'success' };
      case 'cancelled':
        return { label: 'Annulé', color: 'error' };
      default:
        return { label: 'Inconnu', color: 'default' };
    }
  };

  const getSteps = () => {
    return ['Planification', 'En cours', 'Terminé', 'Vérifié'];
  };

  const getActiveStep = (project: Project) => {
    if (project.verificationStatus === 'verified') return 3;
    switch(project.status) {
      case 'planning': return 0;
      case 'in_progress': return 1;
      case 'completed': return 2;
      case 'cancelled': return -1;
      default: return 0;
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" gutterBottom>
            Mes Projets
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
          >
            Nouveau Projet
          </Button>
        </Box>
        <Typography variant="body1" color="textSecondary" paragraph>
          Suivez l'avancement de vos projets de durabilité et mesurez leur impact.
        </Typography>

        {/* Projects List */}
        <Grid container spacing={3}>
          {projects.length > 0 ? (
            projects.map((project) => (
              <Grid item xs={12} md={6} key={project.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getDomainIcon(project.domain)}
                        <Typography variant="h6" component="div" sx={{ ml: 1 }}>
                          {project.recommendationTitle}
                        </Typography>
                      </Box>
                      <Chip
                        label={getStatusLabel(project.status).label}
                        color={getStatusLabel(project.status).color as any}
                        size="small"
                      />
                    </Box>

                    {project.supplierName && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Fournisseur: {project.supplierName}
                      </Typography>
                    )}

                    <Box sx={{ my: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2">Progression:</Typography>
                        <Typography variant="body2">{project.progress}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={project.progress} 
                        sx={{ height: 8, borderRadius: 5 }}
                      />
                    </Box>

                    <Stepper activeStep={getActiveStep(project)} alternativeLabel sx={{ mb: 2 }}>
                      {getSteps().map((label) => (
                        <Step key={label}>
                          <StepLabel>{label}</StepLabel>
                        </Step>
                      ))}
                    </Stepper>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <DateIcon fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            Début: {project.startDate ? formatDate(project.startDate) : 'Non défini'}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <CostIcon fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            Coût: {project.actualCost ? `${project.actualCost} €` : 'Non défini'}
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>

                  <CardActions>
                    <Button size="small" onClick={() => handleOpenProjectDialog(project)}>
                      Voir détails
                    </Button>
                    {project.status === 'completed' && project.verificationStatus === 'pending' && (
                      <Button size="small" startIcon={<VerifyIcon />} color="success">
                        Vérifier
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Vous n'avez pas encore de projets
                </Typography>
                <Typography variant="body1" color="textSecondary" paragraph>
                  Créez votre premier projet en cliquant sur le bouton "Nouveau Projet"
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleOpenDialog}
                >
                  Nouveau Projet
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* Create Project Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Créer un nouveau projet</DialogTitle>
        <DialogContent>
          <Box sx={{ py: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="recommendation-label">Recommandation</InputLabel>
              <Select
                labelId="recommendation-label"
                name="recommendationId"
                value={newProject.recommendationId}
                label="Recommandation"
                onChange={handleSelectChange}
              >
                {recommendations.map((recommendation) => (
                  <MenuItem key={recommendation.id} value={recommendation.id}>
                    {recommendation.title}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="supplier-label">Fournisseur</InputLabel>
              <Select
                labelId="supplier-label"
                name="supplierId"
                value={newProject.supplierId}
                label="Fournisseur"
                onChange={handleSelectChange}
              >
                {suppliers.map((supplier) => (
                  <MenuItem key={supplier.id} value={supplier.id}>
                    {supplier.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Date de début"
              type="date"
              name="startDate"
              value={newProject.startDate}
              onChange={handleInputChange}
              InputLabelProps={{
                shrink: true,
              }}
              sx={{ mb: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Annuler</Button>
          <Button variant="contained" onClick={handleCreateProject}>Créer</Button>
        </DialogActions>
      </Dialog>

      {/* Project Details Dialog */}
      {selectedProject && (
        <Dialog open={openProjectDialog} onClose={handleCloseProjectDialog} maxWidth="md" fullWidth>
          <DialogTitle>{selectedProject.recommendationTitle}</DialogTitle>
          <DialogContent>
            <Box sx={{ py: 1 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Informations générales
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Statut:</Typography>
                        <Chip
                          label={getStatusLabel(selectedProject.status).label}
                          color={getStatusLabel(selectedProject.status).color as any}
                          size="small"
                        />
                      </Box>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Fournisseur:</Typography>
                        <Typography variant="body2">{selectedProject.supplierName || 'Non défini'}</Typography>
                      </Box>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Date de début:</Typography>
                        <Typography variant="body2">
                          {selectedProject.startDate 
                            ? formatDate(selectedProject.startDate) 
                            : 'Non définie'}
                        </Typography>
                      </Box>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Date de fin:</Typography>
                        <Typography variant="body2">
                          {selectedProject.completionDate 
                            ? formatDate(selectedProject.completionDate) 
                            : 'Non définie'}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="subtitle2">Coût réel:</Typography>
                        <Typography variant="body2">
                          {selectedProject.actualCost 
                            ? `${selectedProject.actualCost} €` 
                            : 'Non défini'}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>

                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Notes
                      </Typography>
                      <Typography variant="body2">
                        {selectedProject.notes || 'Aucune note pour ce projet.'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Impact
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Économies annuelles estimées:</Typography>
                        <Typography variant="body2">{selectedProject.estimatedAnnualSavings} €</Typography>
                      </Box>
                      <Box>
                        <Typography variant="subtitle2">Réduction CO2 estimée:</Typography>
                        <Typography variant="body2">{selectedProject.estimatedCo2Reduction} kg</Typography>
                      </Box>
                    </CardContent>
                  </Card>

                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Vérification
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Statut:</Typography>
                        <Chip
                          label={selectedProject.verificationStatus === 'verified' ? 'Vérifié' : 'En attente'}
                          color={selectedProject.verificationStatus === 'verified' ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                      {selectedProject.verificationDate && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="subtitle2">Date de vérification:</Typography>
                          <Typography variant="body2">
                            {formatDate(selectedProject.verificationDate)}
                          </Typography>
                        </Box>
                      )}
                      {selectedProject.verificationDocuments.length > 0 ? (
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>Documents:</Typography>
                          {selectedProject.verificationDocuments.map((doc, index) => (
                            <Chip
                              key={doc}
                              icon={<DocumentIcon />}
                              label={`Document ${index + 1}`}
                              variant="outlined"
                              sx={{ mr: 0.5, mb: 0.5 }}
                            />
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2">
                          Aucun document de vérification disponible.
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {selectedProject.status === 'completed' && selectedProject.verificationStatus === 'pending' && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" gutterBottom>
                    Soumettre une vérification
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Button
                        variant="outlined"
                        startIcon={<CameraIcon />}
                        sx={{ mr: 1 }}
                      >
                        Ajouter une photo
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<DocumentIcon />}
                      >
                        Ajouter un document
                      </Button>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Commentaires"
                        placeholder="Ajoutez des détails sur l'achèvement du projet..."
                      />
                    </Grid>
                  </Grid>
                </>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseProjectDialog}>Fermer</Button>
            {selectedProject.status === 'completed' && selectedProject.verificationStatus === 'pending' && (
              <Button variant="contained" color="success" startIcon={<VerifyIcon />}>
                Soumettre la vérification
              </Button>
            )}
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default Projects;

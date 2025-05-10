import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Breadcrumbs, 
  Link, 
  CircularProgress,
  Alert,
  AlertTitle,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar
} from '@mui/material';
import { NavigateNext, ArrowBack, CheckCircle } from '@mui/icons-material';
import { Link as RouterLink, useParams, useNavigate, useLocation } from 'react-router-dom';
import SubsidyApplicationForm, { FormData } from '../components/subsidies/SubsidyApplicationForm';
import subsidyService, { SubsidyDetail } from '../services/SubsidyService';

interface SubsidyApplicationPageProps {}

const SubsidyApplicationPage: React.FC<SubsidyApplicationPageProps> = () => {
  const { subsidyId } = useParams<{ subsidyId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [initialData, setInitialData] = useState<Partial<FormData> | undefined>(undefined);
  const [confirmLeave, setConfirmLeave] = useState(false);
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [subsidyDetails, setSubsidyDetails] = useState<SubsidyDetail | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showSuccessSnackbar, setShowSuccessSnackbar] = useState(false);

  // Récupérer l'ID de l'application s'il existe (pour les brouillons)
  const queryParams = new URLSearchParams(location.search);
  const applicationId = queryParams.get('applicationId');
  const recommendationId = queryParams.get('recommendationId');

  useEffect(() => {
    if (!subsidyId) {
      setError("ID de subvention non spécifié");
      setLoading(false);
      return;
    }

    const fetchInitialData = async () => {
      try {
        setLoading(true);
        
        // Récupérer les détails de la subvention depuis l'API
        const subsidy = await subsidyService.getSubsidyById(subsidyId);
        setSubsidyDetails(subsidy);
        
        // Si nous avons un ID d'application (brouillon), récupérer les données existantes
        if (applicationId) {
          try {
            // Dans une implémentation réelle, nous ferions un appel API pour récupérer les données du brouillon
            // Pour l'instant, nous utilisons des données mockées
            
            // Exemple de données initiales
            const mockDraftData: Partial<FormData> = {
              applicant: {
                name: 'Jean Dupont',
                email: 'jean.dupont@example.com',
                phone: '+32 470 12 34 56',
                address: 'Rue de la Science 123, 1040 Bruxelles',
                userType: 'individual'
              },
              property: {
                address: 'Rue de la Science 123, 1040 Bruxelles',
                type: 'house',
                yearBuilt: '1975'
              },
              project: {
                description: 'Isolation de la toiture avec des matériaux écologiques',
                estimatedCost: '5000',
                estimatedCompletionDate: '2025-09-15',
                workStarted: 'no',
                contractorSelected: 'yes',
                contractorName: 'Iso-Pro SPRL'
              },
              bankDetails: {
                accountHolder: 'Jean Dupont',
                iban: 'BE68 5390 0754 7034'
              }
            };
            
            setInitialData(mockDraftData);
          } catch (draftError) {
            console.error('Erreur lors de la récupération du brouillon:', draftError);
            // On continue même si on ne peut pas récupérer le brouillon
          }
        }
        
        setError(null);
        setLoading(false);
      } catch (err) {
        console.error('Erreur lors du chargement des données:', err);
        setError("Erreur lors du chargement des détails de la subvention. Veuillez réessayer.");
        setLoading(false);
      }
    };
    
    fetchInitialData();
  }, [subsidyId, applicationId]);

  const handleSubmit = async (data: FormData) => {
    try {
      // Dans une implémentation réelle, nous ferions un appel API pour soumettre le formulaire
      // Pour l'instant, nous simulons l'appel API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log('Formulaire soumis:', data);
      
      // Générer un ID d'application fictif pour la démonstration
      const applicationId = 'APP-' + Math.random().toString(36).substring(2, 10).toUpperCase();
      
      // Afficher un message de succès et rediriger vers la page de suivi
      setSuccessMessage(`Votre demande a été soumise avec succès. Numéro de référence: ${applicationId}`);
      setShowSuccessSnackbar(true);
      setUnsavedChanges(false);
      
      // Rediriger vers la page de suivi après un court délai
      setTimeout(() => {
        navigate(`/subsidies/track/${applicationId}`);
      }, 2000);
      
      return Promise.resolve();
    } catch (err) {
      console.error(err);
      return Promise.reject("Erreur lors de la soumission du formulaire. Veuillez réessayer.");
    }
  };

  const handleSaveDraft = async (data: FormData) => {
    try {
      // Dans une implémentation réelle, nous ferions un appel API pour sauvegarder le brouillon
      // Pour l'instant, nous simulons l'appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      console.log('Brouillon sauvegardé:', data);
      
      // Générer un ID d'application fictif pour la démonstration si nous n'en avons pas déjà un
      const draftId = applicationId || 'DRAFT-' + Math.random().toString(36).substring(2, 10).toUpperCase();
      
      // Afficher un message de succès
      setSuccessMessage(`Brouillon sauvegardé avec succès. Vous pourrez reprendre cette demande plus tard.`);
      setShowSuccessSnackbar(true);
      setUnsavedChanges(false);
      
      // Mettre à jour l'URL avec l'ID du brouillon sans recharger la page
      if (!applicationId) {
        const newUrl = `${location.pathname}?applicationId=${draftId}`;
        window.history.pushState({}, '', newUrl);
      }
      
      return Promise.resolve();
    } catch (err) {
      console.error(err);
      return Promise.reject("Erreur lors de la sauvegarde du brouillon. Veuillez réessayer.");
    }
  };

  const handleBack = () => {
    if (unsavedChanges) {
      setConfirmLeave(true);
    } else {
      navigate('/subsidies');
    }
  };

  const handleConfirmLeave = () => {
    setConfirmLeave(false);
    navigate('/subsidies');
  };

  const handleCancelLeave = () => {
    setConfirmLeave(false);
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !subsidyId) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error || "ID de subvention non spécifié"}
        </Alert>
        <Box mt={2}>
          <Button 
            variant="outlined" 
            component={RouterLink} 
            to="/subsidies"
            startIcon={<ArrowBack />}
          >
            Retour aux subventions
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Breadcrumbs separator={<NavigateNext fontSize="small" />} aria-label="breadcrumb">
          <Link color="inherit" component={RouterLink} to="/dashboard">
            Tableau de bord
          </Link>
          <Link color="inherit" component={RouterLink} to="/subsidies">
            Subventions
          </Link>
          <Typography color="text.primary">Demande</Typography>
        </Breadcrumbs>
      </Box>
      
      <Box display="flex" alignItems="center" mb={4}>
        <Button 
          variant="outlined" 
          startIcon={<ArrowBack />} 
          onClick={handleBack}
          sx={{ mr: 2 }}
        >
          Retour
        </Button>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Demande de subvention
        </Typography>
      </Box>
      
      {subsidyDetails && (
        <Paper elevation={1} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" color="primary" gutterBottom>
            {subsidyDetails.name}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Fournie par: {subsidyDetails.provider}
          </Typography>
          <Typography variant="body2" paragraph>
            {subsidyDetails.description}
          </Typography>
          {subsidyDetails.max_amount && (
            <Typography variant="body2">
              <strong>Montant maximal:</strong> {subsidyDetails.max_amount.toLocaleString()}€
              {subsidyDetails.percentage && ` (${subsidyDetails.percentage}% des coûts éligibles)`}
            </Typography>
          )}
        </Paper>
      )}
      
      <Paper elevation={2} sx={{ p: { xs: 2, md: 4 } }}>
        <SubsidyApplicationForm 
          subsidyId={subsidyId}
          recommendationId={recommendationId || undefined}
          initialData={initialData}
          onSubmit={handleSubmit}
          onSaveDraft={handleSaveDraft}
          subsidyDetails={subsidyDetails}
        />
      </Paper>
      
      {/* Dialogue de confirmation pour quitter sans sauvegarder */}
      <Dialog
        open={confirmLeave}
        onClose={handleCancelLeave}
      >
        <DialogTitle>Quitter sans sauvegarder ?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Vous avez des modifications non sauvegardées. Si vous quittez maintenant, ces modifications seront perdues.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelLeave} color="primary">
            Annuler
          </Button>
          <Button onClick={handleConfirmLeave} color="error">
            Quitter sans sauvegarder
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar pour les messages de succès */}
      <Snackbar
        open={showSuccessSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowSuccessSnackbar(false)}
        message={successMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        action={
          <React.Fragment>
            <CheckCircle color="success" style={{ marginRight: 8 }} />
            <Button color="inherit" size="small" onClick={() => setShowSuccessSnackbar(false)}>
              Fermer
            </Button>
          </React.Fragment>
        }
      />
    </Container>
  );
};

export default SubsidyApplicationPage;

import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Breadcrumbs,
  Link,
  Button,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  NavigateNext,
  ArrowBack,
  CheckCircle,
  Cancel,
  Description,
  Info,
  Error as ErrorIcon,
  PendingOutlined,
  AttachFile,
  Chat,
  Send,
  ArrowCircleRight,
  VisibilityOutlined
} from '@mui/icons-material';
import { Link as RouterLink, useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useSelector } from 'react-redux';
import { selectUser } from '../store/slices/authSlice';
import { applicationService } from '../services/ApplicationService';
import { ApplicationResponse, ApplicationStatus, ApplicationDocument, ApplicationNote, ApplicationHistory, DocumentStatus } from '../types/api';

// Interface pour mapper les données de l'API au format attendu par le composant
interface SubsidyApplication {
  id: string;
  subsidyId: string;
  subsidyName: string;
  status: ApplicationStatus;
  statusLabel: string;
  submissionDate: string;
  lastUpdated: string;
  referenceNumber: string;
  applicant: {
    name: string;
    email: string;
    phone: string;
  };
  property: {
    address: string;
    type: string;
  };
  project: {
    description: string;
    estimatedCost: number;
    estimatedCompletionDate: string;
  };
  subsidy: {
    maxAmount: number | null;
    percentage: number | null;
    calculatedAmount: number | null;
  };
  documents: SubsidyDocument[];
  notes: ApplicationNote[];
  history: ApplicationHistory[];
  nextSteps?: string[];
}

// Define the specific set of statuses expected by this page's state
type DisplayableDocumentStatusLiteral = "pending" | "validated" | "rejected" | "requested";

// Interface pour les documents dans l'application
interface SubsidyDocument {
  id: string;
  document_id?: string;
  name: string;
  status: DisplayableDocumentStatusLiteral; // Changed from DocumentStatus to the literal union
  uploadDate?: string;
  uploaded_at?: string | null;
  validationDate?: string;
  file_url?: string | null;
  comments?: string;
  size: number;
}

// Type utilitaire pour la conversion des statuts de document
const convertToDocumentStatus = (status: string | DocumentStatus): DisplayableDocumentStatusLiteral => {
  const normalizedStatus = typeof status === 'string' ? status.toLowerCase() : status;

  switch(normalizedStatus) {
    case DocumentStatus.PENDING:
    case 'pending':
    case DocumentStatus.UPLOADED: // Map 'uploaded' to 'pending' for display
    case 'uploaded':
    case 'processing': // 'processing' n'existe pas dans l'enum mais peut venir de l'API
      return "pending";
    case DocumentStatus.VALIDATED:
    case 'validated':
      return "validated";
    case DocumentStatus.REJECTED:
    case 'rejected':
      return "rejected";
    case 'requested_changes': // Ces valeurs n'existent pas dans l'enum mais peuvent venir de l'API
    case 'requested':
      return "requested";
    default:
      // Fallback pour tout statut inattendu
      console.warn(`Unknown document status received: ${status}, defaulting to 'pending'.`);
      return "pending";
  }
};

const SubsidyTrackingPage: React.FC = () => {
  const { applicationId } = useParams<{ applicationId: string }>();
  const navigate = useNavigate();
  const [application, setApplication] = useState<SubsidyApplication | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newNote, setNewNote] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [uploadingDocument, setUploadingDocument] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);

  // Récupérer l'utilisateur connecté depuis le store Redux
  const user = useSelector(selectUser);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadingStatus, setUploadingStatus] = useState<{ loading: boolean; error: string | null; success: boolean }>({ 
    loading: false, 
    error: null, 
    success: false 
  });
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  useEffect(() => {
    fetchApplicationDetails();
  }, [applicationId]);

  const fetchApplicationDetails = async () => {
    if (!applicationId) {
      setError("ID d'application non spécifié");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Appel à l'API pour récupérer les détails de l'application
      const response = await applicationService.getApplication(applicationId);
      
      // Mapper les données de l'API au format attendu par le composant
      // Mapper les documents de la réponse API pour s'assurer que le statut est de type DocumentStatus
      const mappedDocuments: SubsidyDocument[] = response.documents.map((doc: any) => ({
        id: doc.id,
        document_id: doc.document_id,
        name: doc.name,
        status: convertToDocumentStatus(doc.status),
        uploadDate: doc.uploaded_at,
        uploaded_at: doc.uploaded_at,
        validationDate: doc.validated_at,
        file_url: doc.file_url,
        comments: doc.comments,
        size: doc.size || 0
      }));
      
      const mappedApplication: SubsidyApplication = {
        id: response.id,
        subsidyId: response.subsidy_id,
        subsidyName: response.subsidy.name,
        status: response.status,
        statusLabel: getStatusLabel(response.status),
        submissionDate: response.created_at,
        lastUpdated: response.updated_at,
        referenceNumber: `REF-${response.id}`,
        applicant: {
          name: user?.fullName || user?.name || 'Utilisateur',
          email: user?.email || 'email@exemple.com',
          phone: '+32 470 00 00 00' // Propriété non disponible dans le type User actuel
        },
        property: {
          address: 'Adresse de la propriété', // Ces informations devraient venir de l'API
          type: 'Type de propriété'
        },
        project: {
          description: 'Description du projet', // Ces informations devraient venir de l'API
          estimatedCost: 0,
          estimatedCompletionDate: new Date().toISOString()
        },
        subsidy: {
          maxAmount: response.subsidy.max_amount,
          percentage: response.subsidy.percentage,
          calculatedAmount: response.subsidy.max_amount // Calcul à faire en fonction des règles métier
        },
        // Convertir les documents de l'API au format SubsidyDocument en utilisant le mappage déjà défini
        documents: mappedDocuments,
        notes: response.notes,
        history: response.history,
        nextSteps: response.nextSteps
      };
      
      // Calculer l'étape active dans le stepper
      const statusToStep: Record<string, number> = {
        [ApplicationStatus.DRAFT]: 0,
        [ApplicationStatus.SUBMITTED]: 1,
        [ApplicationStatus.PROCESSING]: 2,
        [ApplicationStatus.ADDITIONAL_INFO]: 2,
        [ApplicationStatus.APPROVED]: 3,
        [ApplicationStatus.REJECTED]: 3,
        [ApplicationStatus.PAID]: 4,
        [ApplicationStatus.CANCELLED]: 4
      };
      setActiveStep(statusToStep[mappedApplication.status] || 0);
      
      setApplication(mappedApplication);
      setLoading(false);
    } catch (error: any) {
      console.error('Error fetching application details:', error);
      setError(error.message || 'Erreur lors du chargement des détails de la demande. Veuillez réessayer.');
      setLoading(false);
    }
  };

  // Fonction pour obtenir le libellé du statut
  const getStatusLabel = (status: ApplicationStatus): string => {
    const statusLabels: Record<ApplicationStatus, string> = {
      [ApplicationStatus.DRAFT]: 'Brouillon',
      [ApplicationStatus.SUBMITTED]: 'Soumise',
      [ApplicationStatus.PROCESSING]: 'En cours de traitement',
      [ApplicationStatus.ADDITIONAL_INFO]: 'Informations complémentaires demandées',
      [ApplicationStatus.APPROVED]: 'Approuvée',
      [ApplicationStatus.REJECTED]: 'Rejetée',
      [ApplicationStatus.PAID]: 'Payée',
      [ApplicationStatus.CANCELLED]: 'Annulée'
    };
    return statusLabels[status] || 'Statut inconnu';
  };

  const handleAddNote = async () => {
    if (!application || !newNote.trim() || !applicationId) return;
    
    try {
      // Appel à l'API réelle
      // Simuler un appel API
      // Dans une implémentation réelle, cela serait:
      // const response = await applicationService.addNote(applicationId, newNote);
      
      // Créer un objet note à partir de la réponse de l'API
      const newNoteObj: ApplicationNote = {
        id: `note${application.notes.length + 1}`,
        date: format(new Date(), 'yyyy-MM-dd'),
        author: user?.name || 'Utilisateur',
        authorType: (user?.userType === 'admin' ? 'admin' : 'user') as 'admin' | 'user' | 'system',
        content: newNote
      };
      
      // Mettre à jour l'état local
      setApplication(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          notes: [...prev.notes, newNoteObj],
          lastUpdated: format(new Date(), 'yyyy-MM-dd')
        };
      });
      
      // Réinitialiser le champ de saisie
      setNewNote('');
      
      // Afficher un message de succès
      setSnackbarMessage('Votre message a été envoyé avec succès');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Erreur lors de l\'ajout de la note:', error);
      setSnackbarMessage('Erreur lors de l\'envoi du message. Veuillez réessayer.');
      setSnackbarOpen(true);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUploadDocument = (documentId: string) => {
    // Simuler le téléchargement d'un document
    // Dans une implémentation réelle, cela appellerait applicationService.uploadDocument
    setUploadingDocument(documentId);
    setDialogOpen(true);
    setSelectedFile(null);
    setUploadingStatus({ loading: false, error: null, success: false });
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    
    if (application) {
      // Utiliser prev => pour satisfaire le typechecking sans mutation directe
      setApplication(prev => {
        if (!prev) return null;
        
        // Convertir explicitement chaque document pour s'assurer que le statut est de type DisplayableDocumentStatusLiteral
        const updatedDocuments: SubsidyDocument[] = prev.documents.map(d => ({
          ...d,
          status: d.id === uploadingDocument 
            ? "pending" as DisplayableDocumentStatusLiteral
            : convertToDocumentStatus(d.status),
          uploadDate: d.id === uploadingDocument 
            ? new Date().toISOString() 
            : d.uploadDate,
          size: d.id === uploadingDocument 
            ? (selectedFile?.size || 0) 
            : d.size
        }));
        
        return {
          ...prev,
          documents: updatedDocuments
        };
      });
      
      // Ajouter une note système
      const newNoteObject: ApplicationNote = {
        id: `note${application?.notes?.length ? application.notes.length + 1 : 1}`,
        date: format(new Date(), 'yyyy-MM-dd'),
        author: "Système",
        authorType: "admin",
        content: `Le document "${application?.documents.find(d => d.id === uploadingDocument)?.name}" a été téléchargé et est en attente de validation.`
      };
      
      setApplication(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          notes: [...prev.notes, newNoteObject]
        };
      });
      
      // Ajouter à l'historique
      const newHistoryItem = {
        id: `hist${application?.history?.length ? application.history.length + 1 : 1}`,
        date: format(new Date(), 'yyyy-MM-dd'),
        status: ApplicationStatus.PROCESSING,
        description: "Document téléchargé"
      } as ApplicationHistory;
      
      setApplication(prev => {
        if (!prev) return null;
        return {
          ...prev,
          history: [...prev.history, newHistoryItem]
        };
      });
    }
    
    // Réinitialiser l'état du document en cours de téléchargement
    setUploadingDocument(null);
    setSelectedFile(null);
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile || !uploadingDocument || !applicationId) return;
    
    setUploadingStatus({
      loading: true,
      error: null,
      success: false
    });
    
    try {
      // Appel à l'API pour télécharger le document
      const response = await applicationService.uploadDocument(applicationId, uploadingDocument, selectedFile);
      
      // Mettre à jour l'état local avec le document mis à jour
      if (application) {
        const documentIndex = application.documents.findIndex(doc => doc.id === uploadingDocument);
        
        if (documentIndex !== -1) {
          // Utiliser prev => pour satisfaire le typechecking
          setApplication(prev => {
            if (!prev) return null;
            
            // Convertir la réponse API en format SubsidyDocument avec le bon type pour status
            const updatedDocument: SubsidyDocument = {
              id: response.id,
              document_id: response.document_id,
              name: response.name,
              status: convertToDocumentStatus(response.status),
              uploadDate: response.uploaded_at || new Date().toISOString(),
              uploaded_at: response.uploaded_at,
              file_url: response.file_url,
              size: selectedFile.size
            };
            
            // Créer un nouveau tableau de documents avec le document mis à jour
            const updatedDocuments = prev.documents.map((doc, index) => 
              index === documentIndex 
                ? updatedDocument
                : { ...doc, status: convertToDocumentStatus(doc.status) }
            );
            
            return {
              ...prev,
              documents: updatedDocuments
            };
          });
        }
      }
      
      setUploadingStatus({
        loading: false,
        error: null,
        success: true
      });
      
      // Afficher une notification de succès
      setSnackbarMessage('Document téléchargé avec succès.');
      setSnackbarOpen(true);
      
      // Fermer le dialogue après un court délai
      setTimeout(() => {
        handleCloseDialog();
      }, 1500);
    } catch (error: any) {
      console.error('Error uploading document:', error);
      setUploadingStatus({
        loading: false,
        error: error.message || 'Erreur lors du téléchargement du document. Veuillez réessayer.',
        success: false
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  const formatDate = (dateString: string): string => {
    try {
      return format(new Date(dateString), 'dd MMMM yyyy', { locale: fr });
    } catch (error) {
      return dateString;
    }
  };

  const getDocumentStatusChip = (status: DisplayableDocumentStatusLiteral) => {
    switch(status) {
      case "pending":
        return <Chip size="small" label="En attente" color="warning" icon={<PendingOutlined />} />;
      case "validated":
        return <Chip size="small" label="Validé" color="success" icon={<CheckCircle />} />;
      case "rejected":
        return <Chip size="small" label="Rejeté" color="error" icon={<Cancel />} />;
      case "requested":
        return <Chip size="small" label="Demandé" color="info" icon={<ArrowCircleRight />} />;
      default:
        return <Chip size="small" label="Inconnu" color="default" />;
    }
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

  if (error || !application) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error || "Impossible de charger les détails de la demande"}
        </Alert>
        <Box mt={2} display="flex" justifyContent="center">
          <Button 
            variant="contained" 
            startIcon={<ArrowBack />}
            onClick={() => navigate('/subsidies')}
          >
            Retour aux subventions
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Fil d'Ariane */}
      <Breadcrumbs separator={<NavigateNext fontSize="small" />} sx={{ mb: 2, mt: 2 }}>
        <Link component={RouterLink} to="/" color="inherit">
          Accueil
        </Link>
        <Link component={RouterLink} to="/subsidies" color="inherit">
          Subventions
        </Link>
        <Typography color="text.primary">Suivi de demande</Typography>
      </Breadcrumbs>
      
      {/* En-tête */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h5" gutterBottom>
              Demande de {application.subsidyName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Référence: {application.referenceNumber}
            </Typography>
          </Box>
          <Chip 
            label={application.statusLabel}
            color={
              application.status === 'approved' ? 'success' :
              application.status === 'rejected' ? 'error' :
              application.status === 'additional_info' ? 'warning' : 'info'
            }
            sx={{ fontWeight: 'medium' }}
          />
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          <Step>
            <StepLabel>Soumission</StepLabel>
          </Step>
          <Step>
            <StepLabel>Vérification</StepLabel>
          </Step>
          <Step>
            <StepLabel>Traitement</StepLabel>
          </Step>
          <Step>
            <StepLabel>Décision</StepLabel>
          </Step>
        </Stepper>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Date de soumission
            </Typography>
            <Typography variant="body2" paragraph>
              {formatDate(application.submissionDate)}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Dernière mise à jour
            </Typography>
            <Typography variant="body2" paragraph>
              {formatDate(application.lastUpdated)}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          {/* Détails de la demande */}
          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Détails de la demande
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Demandeur
                </Typography>
                <Typography variant="body2" paragraph>
                  {application.applicant.name}
                </Typography>
                <Typography variant="body2" paragraph>
                  {application.applicant.email}
                </Typography>
                <Typography variant="body2" paragraph>
                  {application.applicant.phone}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Propriété
                </Typography>
                <Typography variant="body2" paragraph>
                  {application.property.address}
                </Typography>
                <Typography variant="body2" paragraph>
                  Type: {application.property.type}
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Projet
                </Typography>
                <Typography variant="body2" paragraph>
                  {application.project.description}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" paragraph>
                      Coût estimé: {application.project.estimatedCost.toLocaleString('fr-BE')} €
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" paragraph>
                      Date d'achèvement prévue: {formatDate(application.project.estimatedCompletionDate)}
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Subvention
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" paragraph>
                      Montant maximum: {application.subsidy.maxAmount?.toLocaleString('fr-BE')} €
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" paragraph>
                      Pourcentage: {application.subsidy.percentage}%
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" paragraph>
                      Montant calculé: {application.subsidy.calculatedAmount?.toLocaleString('fr-BE')} €
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Documents */}
          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Documents
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <List>
              {application.documents.map((doc: SubsidyDocument) => (
                <ListItem 
                  key={doc.id}
                  sx={{ 
                    borderBottom: '1px solid #f0f0f0',
                    py: 2
                  }}
                  secondaryAction={
                    doc.status === "pending" || doc.status === "requested" ? (
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<AttachFile />}
                        onClick={() => handleUploadDocument(doc.id)}
                      >
                        Télécharger
                      </Button>
                    ) : (
                      <Tooltip title="Voir le document">
                        <IconButton edge="end" aria-label="view">
                          <VisibilityOutlined />
                        </IconButton>
                      </Tooltip>
                    )
                  }
                >
                  <ListItemIcon>
                    <Description color={(doc.status === "pending" || doc.status === "requested") ? 'action' : 'primary'} />
                  </ListItemIcon>
                  <ListItemText
                    primary={doc.name}
                    secondary={
                      <>
                        {getDocumentStatusChip(doc.status)}
                        {doc.uploadDate && (
                          <Typography variant="caption" sx={{ ml: 1 }}>
                            Téléchargé le {formatDate(doc.uploadDate)}
                          </Typography>
                        )}
                        {doc.comments && (
                          <Typography variant="body2" color="error" sx={{ mt: 0.5 }}>
                            {doc.comments}
                          </Typography>
                        )}
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
          
          {/* Historique */}
          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Historique
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <List>
              {application.history.map((hist: ApplicationHistory, index: number) => (
                <ListItem key={hist.id} divider={index < application.history.length - 1}>
                  <ListItemText 
                    primary={hist.description}
                    secondary={formatDate(hist.date)}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          {/* Prochaines étapes */}
          {application.nextSteps && application.nextSteps.length > 0 && (
            <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Prochaines étapes
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <List>
                {application.nextSteps.map((step, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <ArrowCircleRight color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={step} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
          
          {/* Messages */}
          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Messages
            </Typography>
            
            <Box sx={{ maxHeight: '400px', overflowY: 'auto', mb: 3 }}>
              {application.notes.map((note: ApplicationNote) => (
                <Card 
                  key={note.id} 
                  variant="outlined" 
                  sx={{ 
                    mb: 2,
                    bgcolor: note.authorType === 'admin' ? '#f5f5f5' : 'primary.50'
                  }}
                >
                  <CardContent sx={{ pb: 1 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {note.author}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(note.date)}
                      </Typography>
                    </Box>
                    <Typography variant="body2">{note.content}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box display="flex" gap={1}>
              <TextField
                fullWidth
                label="Votre message"
                variant="outlined"
                multiline
                rows={2}
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Écrivez un message concernant votre demande..."
                size="small"
              />
              <Button
                variant="contained"
                startIcon={<Send />}
                onClick={handleAddNote}
                disabled={newNote.trim() === ''}
                sx={{ alignSelf: 'flex-end' }}
              >
                Envoyer
              </Button>
            </Box>
          </Paper>
          
          <Box sx={{ position: { md: 'sticky' }, top: { md: '100px' } }}>
            <Alert severity="info" sx={{ mb: 4 }}>
              <Typography variant="subtitle2" gutterBottom>
                Besoin d'aide ?
              </Typography>
              <Typography variant="body2">
                Si vous avez des questions sur votre demande, n'hésitez pas à nous contacter par message ci-dessus
                ou via le service client.
              </Typography>
              <Button 
                variant="outlined" 
                size="small" 
                startIcon={<Chat />}
                sx={{ mt: 2 }}
                component={RouterLink}
                to="/contact"
              >
                Contacter le service client
              </Button>
            </Alert>
          </Box>
        </Grid>
      </Grid>
      
      {/* Dialogue de téléchargement de document */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>
          Télécharger le document
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Sélectionnez le document à télécharger. Formats acceptés: PDF, PNG, JPG.
          </DialogContentText>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.png,.jpg,.jpeg"
            style={{ display: 'none' }}
          />
          <Button
            variant="contained"
            component="label"
            sx={{ mt: 2 }}
            startIcon={<AttachFile />}
            onClick={() => fileInputRef.current?.click()}
          >
            Choisir un fichier
          </Button>
          {selectedFile && (
            <Typography variant="body2" sx={{ mt: 2 }}>
              Fichier sélectionné: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} Ko)
            </Typography>
          )}
          {uploadingStatus.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {uploadingStatus.error}
            </Alert>
          )}
          {uploadingStatus.success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Document téléchargé avec succès!
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Annuler
          </Button>
          <Button 
            onClick={handleUploadSubmit} 
            color="primary" 
            variant="contained"
            disabled={!selectedFile || uploadingStatus.loading || uploadingStatus.success}
          >
            {uploadingStatus.loading ? (
              <>
                <CircularProgress size={24} sx={{ mr: 1 }} />
                Téléchargement...
              </>
            ) : 'Télécharger'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar pour les notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default SubsidyTrackingPage;

import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Button, 
  Card, 
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { 
  CloudUpload, 
  InsertDriveFile, 
  CheckCircle, 
  Delete, 
  Refresh, 
  Warning, 
  HelpOutline,
  Description,
  PictureAsPdf
} from '@mui/icons-material';

interface DocumentInfo {
  file: File | null;
  uploaded: boolean;
  validated: boolean;
  name: string;
}

interface DocumentsState {
  [key: string]: DocumentInfo;
}

interface DocumentType {
  id: string;
  name: string;
  description: string;
  required: boolean;
  type: string;
}

interface DocumentsUploadFormProps {
  documents: DocumentsState;
  requiredDocuments: DocumentType[];
  onChange: (documents: DocumentsState) => void;
}

const DocumentsUploadForm: React.FC<DocumentsUploadFormProps> = ({ 
  documents, 
  requiredDocuments, 
  onChange 
}) => {
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});
  const [openDialog, setOpenDialog] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>, docId: string) => {
    const file = event.target.files?.[0];
    if (file) {
      // Simuler le téléchargement et le traitement du fichier
      setLoading(prev => ({ ...prev, [docId]: true }));
      
      setTimeout(() => {
        const updatedDocuments = { ...documents };
        updatedDocuments[docId] = {
          ...updatedDocuments[docId],
          file: file,
          uploaded: true,
          validated: true  // Dans une implémentation réelle, cela serait validé par le backend
        };
        
        onChange(updatedDocuments);
        setLoading(prev => ({ ...prev, [docId]: false }));
      }, 1500); // Simuler un délai de traitement
    }
  };

  const handleDeleteFile = (docId: string) => {
    const updatedDocuments = { ...documents };
    updatedDocuments[docId] = {
      ...updatedDocuments[docId],
      file: null,
      uploaded: false,
      validated: false
    };
    
    onChange(updatedDocuments);
    // Si un aperçu est ouvert pour ce document, le fermer
    if (openDialog === docId) {
      handleClosePreview();
    }
  };

  const handlePreviewFile = (docId: string) => {
    const file = documents[docId]?.file;
    if (file) {
      setOpenDialog(docId);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleClosePreview = () => {
    setOpenDialog(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
  };

  // Fonction pour obtenir l'icône en fonction du type de fichier
  const getFileIcon = (file: File | null) => {
    if (!file) return <InsertDriveFile />;
    
    if (file.type.includes('pdf')) {
      return <PictureAsPdf color="error" />;
    } else if (file.type.includes('image')) {
      return <Description color="primary" />;
    } else {
      return <InsertDriveFile color="action" />;
    }
  };

  // Vérifier si tous les documents requis sont téléchargés
  const allRequiredUploaded = requiredDocuments
    .filter(doc => doc.required)
    .every(doc => documents[doc.id]?.uploaded);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Documents requis
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Veuillez télécharger tous les documents requis pour votre demande de subvention. 
        Les documents doivent être au format PDF, PNG ou JPG et ne pas dépasser 10 Mo.
      </Typography>

      {!allRequiredUploaded && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Veuillez télécharger tous les documents marqués comme obligatoires pour pouvoir finaliser votre demande.
        </Alert>
      )}

      <List>
        {requiredDocuments.map((doc) => (
          <Card key={doc.id} sx={{ mb: 2, border: doc.required ? '1px solid rgba(25, 118, 210, 0.3)' : 'none' }}>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={7}>
                  <ListItem disablePadding>
                    <ListItemIcon>
                      {documents[doc.id]?.file ? (
                        getFileIcon(documents[doc.id].file)
                      ) : (
                        <InsertDriveFile color="action" />
                      )}
                    </ListItemIcon>
                    <ListItemText 
                      primary={
                        <Box display="flex" alignItems="center">
                          {doc.name}
                          {doc.required && (
                            <Chip 
                              label="Obligatoire" 
                              size="small" 
                              color="primary" 
                              variant="outlined" 
                              sx={{ ml: 1, height: 20 }}
                            />
                          )}
                        </Box>
                      }
                      secondary={doc.description}
                    />
                    <Tooltip title="Plus d'informations">
                      <IconButton size="small" edge="end">
                        <HelpOutline fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItem>
                </Grid>
                
                <Grid item xs={12} md={5}>
                  <CardActions sx={{ display: 'flex', justifyContent: 'flex-end', p: 0 }}>
                    {documents[doc.id]?.uploaded ? (
                      <>
                        <Chip 
                          icon={<CheckCircle />} 
                          label="Téléchargé" 
                          color="success" 
                          size="small" 
                          sx={{ mr: 1 }}
                        />
                        <Button 
                          size="small" 
                          onClick={() => handlePreviewFile(doc.id)}
                          disabled={!documents[doc.id].file}
                        >
                          Aperçu
                        </Button>
                        <IconButton 
                          size="small" 
                          color="primary" 
                          onClick={() => handleDeleteFile(doc.id)}
                        >
                          <Delete />
                        </IconButton>
                      </>
                    ) : (
                      <Button
                        variant="contained"
                        component="label"
                        startIcon={loading[doc.id] ? <CircularProgress size={16} /> : <CloudUpload />}
                        disabled={loading[doc.id]}
                        size="small"
                      >
                        {loading[doc.id] ? 'Téléchargement...' : 'Télécharger'}
                        <input
                          type="file"
                          hidden
                          accept=".pdf,.png,.jpg,.jpeg"
                          onChange={(e) => handleFileChange(e, doc.id)}
                        />
                      </Button>
                    )}
                  </CardActions>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        ))}
      </List>

      {/* Dialogue d'aperçu du document */}
      <Dialog
        open={openDialog !== null}
        onClose={handleClosePreview}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {openDialog && documents[openDialog]?.file?.name}
        </DialogTitle>
        <DialogContent dividers>
          {previewUrl && openDialog && (
            documents[openDialog]?.file?.type.includes('image') ? (
              <Box display="flex" justifyContent="center">
                <img 
                  src={previewUrl} 
                  alt="Document preview" 
                  style={{ maxWidth: '100%', maxHeight: '70vh' }} 
                />
              </Box>
            ) : documents[openDialog]?.file?.type.includes('pdf') ? (
              <Box height="70vh">
                <iframe 
                  src={previewUrl} 
                  width="100%" 
                  height="100%" 
                  title="PDF preview"
                />
              </Box>
            ) : (
              <Alert severity="info">
                L'aperçu n'est pas disponible pour ce type de fichier. Téléchargez-le pour le consulter.
              </Alert>
            )
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreview}>Fermer</Button>
          {openDialog && (
            <Button 
              color="error" 
              onClick={() => {
                handleDeleteFile(openDialog);
                handleClosePreview();
              }}
            >
              Supprimer
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentsUploadForm;

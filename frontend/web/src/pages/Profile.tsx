import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Divider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  MenuItem,
  Avatar,
  InputAdornment,
  Badge,
  IconButton,
  CircularProgress
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { selectProfile, fetchUserAudits } from '../store/slices/profileSlice';
import { RootState, AppDispatch } from '../store'; 

interface EditableProfileData {
  name: string;
  email: string;
}

const Profile: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>(); 
  const profile = useSelector(selectProfile); 
  const isLoading = useSelector((state: RootState) => state.profile.loading);
  const profileError = useSelector((state: RootState) => state.profile.error);

  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState<EditableProfileData | null>(
    profile ? { name: profile.name, email: profile.email } : null
  );

  useEffect(() => {
    if (profile?.id && !isLoading && !profile.auditData) {
      dispatch(fetchUserAudits(profile.id));
    }
    if (profile && (!formData || formData.name !== profile.name || formData.email !== profile.email)) {
      setFormData({ name: profile.name, email: profile.email });
    }
  }, [dispatch, profile, isLoading, formData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => prev ? { ...prev, [name]: value } : null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData && profile?.id) {
      // dispatch(updateGeneralProfile({ userId: profile.id, ...formData }));
    }
    setEditMode(false);
  };

  const handleCancel = () => {
    if (profile) {
      setFormData({ name: profile.name, email: profile.email });
    }
    setEditMode(false);
  };

  if (isLoading && !profile?.auditData) { 
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Chargement du profil...</Typography>
      </Box>
    );
  }

  if (!profile) { 
    return (
      <Box sx={{ textAlign: 'center', py: 3 }}>
        <Typography variant="h6" paragraph>
          {profileError ? "Erreur lors du chargement du profil." : "Chargement du profil..."}
        </Typography>
        {profileError && (
          <Typography color="error" paragraph>
            Erreur: {profileError}
          </Typography>
        )}
        {!profileError && !isLoading && <Typography>Aucune donnée de profil disponible.</Typography>}
      </Box>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" gutterBottom>
            Mon Profil
          </Typography>
          {!editMode ? (
            <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setEditMode(true)}>
              Modifier
            </Button>
          ) : (
            <Box>
              <Button variant="outlined" startIcon={<CancelIcon />} onClick={handleCancel} sx={{ mr: 1 }}>
                Annuler
              </Button>
              <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSubmit}>
                Enregistrer
              </Button>
            </Box>
          )}
        </Box>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Badge
                overlap="circular"
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                badgeContent={editMode ? <IconButton sx={{ backgroundColor: 'primary.main', color: 'white', '&:hover': { backgroundColor: 'primary.dark' }}} size="small"> <EditIcon fontSize="small" /> </IconButton> : null}
              >
                <Avatar sx={{ width: 120, height: 120, mb: 2 }} src="/static/images/avatar/1.jpg" />
              </Badge>
              {profile.subscriptionType === 'premium' && (
                <Box sx={{ backgroundColor: 'success.main', color: 'white', px: 2, py: 0.5, borderRadius: 5, fontSize: '0.75rem', fontWeight: 'bold', textTransform: 'uppercase' }}>
                  Premium
                </Box>
              )}
            </Grid>

            <Grid item xs={12} md={8}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Nom"
                    name="name"
                    value={formData?.name || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                    variant={editMode ? "outlined" : "filled"}
                    InputProps={{ readOnly: !editMode }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={formData?.email || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                    variant={editMode ? "outlined" : "filled"}
                    InputProps={{ readOnly: !editMode }}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </form>

        <Divider sx={{ my: 3 }} />

        {isLoading && !profile.auditData && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2}}><CircularProgress size={24} /><Typography sx={{ml:1}}>Chargement des données d'audit...</Typography></Box>
        )}
        {profileError && !profile.auditData && (
          <Typography color="error">Erreur lors du chargement des données d'audit: {profileError}</Typography>
        )}
        {!isLoading && !profileError && !profile.auditData && (
          <Typography>Aucun audit énergétique trouvé pour ce profil.</Typography>
        )}

        {profile.auditData ? (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Détails du Dernier Audit Énergétique
              </Typography>
              {profile.lastAuditUpdateTimestamp && (
                <Typography variant="caption" color="text.secondary">
                  Mis à jour le: {new Date(profile.lastAuditUpdateTimestamp).toLocaleDateString()}
                </Typography>
              )}
            </Box>
            
            <Typography variant="subtitle1" gutterBottom>
              Profil Utilisateur (de l'audit)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Type d'utilisateur:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.profile?.userType || 'Non spécifié'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Région:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.profile?.region === 'wallonie' ? 'Wallonie' :
                   profile.auditData.profile?.region === 'bruxelles' ? 'Bruxelles' :
                   profile.auditData.profile?.region === 'flandre' ? 'Flandre' :
                   profile.auditData.profile?.region || 'Non spécifiée'}
                </Typography>
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" gutterBottom>
              Consommation
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Consommation d'électricité:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.consumption?.electricityUsage ? `${profile.auditData.consumption.electricityUsage} kWh/an` : 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Consommation de gaz:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.consumption?.gasUsage ? 
                    (profile.auditData.consumption.gasConsumption ? `${profile.auditData.consumption.gasConsumption} m³/an` : 'Oui (quantité non spécifiée)') : 
                    'Non'}
                </Typography>
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" gutterBottom>
              Propriété
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Type de propriété:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.property?.propertyType || 'Non spécifié'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Surface:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.property?.area ? `${profile.auditData.property.area} m²` : 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Année de construction:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.property?.constructionYear || 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  État de l'isolation:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.property?.insulationStatus || 'Non spécifié'}
                </Typography>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={() => window.location.href = '/recommendations'}
              >
                Voir mes recommandations
              </Button>
            </Box>
          </>
        ) : (
          !isLoading && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" paragraph>
                Vous n'avez pas encore effectué d'audit énergétique ou les données ne sont pas disponibles.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={() => window.location.href = '/audit'}
              >
                Effectuer un audit
              </Button>
            </Box>
          )
        )}
      </Paper>
    </Box>
  );
};

export default Profile;

import React, { useState } from 'react';
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
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { selectProfile } from '../store/slices/profileSlice';

const Profile: React.FC = () => {
  const profile = useSelector(selectProfile);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState(profile);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        [name]: value,
      };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would dispatch an action to update the profile
    // dispatch(updateProfile(formData));
    setEditMode(false);
  };

  const handleCancel = () => {
    setFormData(profile);
    setEditMode(false);
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" gutterBottom>
            Mon Profil
          </Typography>
          {!editMode ? (
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => setEditMode(true)}
            >
              Modifier
            </Button>
          ) : (
            <Box>
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
                sx={{ mr: 1 }}
              >
                Annuler
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSubmit}
              >
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
                badgeContent={
                  editMode ? (
                    <IconButton
                      sx={{
                        backgroundColor: 'primary.main',
                        color: 'white',
                        '&:hover': { backgroundColor: 'primary.dark' },
                      }}
                      size="small"
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                  ) : null
                }
              >
                <Avatar
                  sx={{ width: 120, height: 120, mb: 2 }}
                  src="/static/images/avatar/1.jpg"
                />
              </Badge>
              {profile?.subscriptionType === 'premium' && (
                <Box sx={{ 
                  backgroundColor: 'success.main', 
                  color: 'white', 
                  px: 2, 
                  py: 0.5, 
                  borderRadius: 5,
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  textTransform: 'uppercase'
                }}>
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
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Téléphone"
                    name="phone"
                    value={formData?.phone || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Code postal"
                    name="postalCode"
                    value={formData?.postalCode || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Adresse"
                    name="address"
                    value={formData?.address || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editMode}>
                    <FormLabel id="region-label">Région</FormLabel>
                    <RadioGroup
                      aria-labelledby="region-label"
                      name="region"
                      value={formData?.region || 'wallonie'}
                      onChange={handleChange}
                      row
                    >
                      <FormControlLabel value="wallonie" control={<Radio />} label="Wallonie" />
                      <FormControlLabel value="bruxelles" control={<Radio />} label="Bruxelles" />
                      <FormControlLabel value="flandre" control={<Radio />} label="Flandre" />
                    </RadioGroup>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    fullWidth
                    label="Langue"
                    name="language"
                    value={formData?.language || 'fr'}
                    onChange={handleChange}
                    disabled={!editMode}
                  >
                    <MenuItem value="fr">Français</MenuItem>
                    <MenuItem value="nl">Nederlands</MenuItem>
                    <MenuItem value="de">Deutsch</MenuItem>
                    <MenuItem value="en">English</MenuItem>
                  </TextField>
                </Grid>
              </Grid>
            </Grid>
          </Grid>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h6" gutterBottom>
            Informations professionnelles
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Type d'utilisateur"
                name="userType"
                value={formData?.userType || 'individual'}
                onChange={handleChange}
                disabled={!editMode}
              >
                <MenuItem value="individual">Particulier</MenuItem>
                <MenuItem value="self_employed">Indépendant</MenuItem>
                <MenuItem value="small_business">Petite entreprise</MenuItem>
                <MenuItem value="medium_business">Moyenne entreprise</MenuItem>
                <MenuItem value="large_business">Grande entreprise</MenuItem>
              </TextField>
            </Grid>
            {formData?.userType !== 'individual' && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Nom de l'entreprise"
                    name="companyName"
                    value={formData?.companyName || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Numéro de TVA"
                    name="companyVat"
                    value={formData?.companyVat || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Nombre d'employés"
                    name="companySize"
                    type="number"
                    InputProps={{
                      inputProps: { min: 1 }
                    }}
                    value={formData?.companySize || ''}
                    onChange={handleChange}
                    disabled={!editMode}
                  />
                </Grid>
              </>
            )}
          </Grid>
        </form>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Abonnement
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="body1">
            Type d'abonnement:
          </Typography>
          <Typography variant="body1" fontWeight="bold" sx={{ ml: 1 }}>
            {profile?.subscriptionType === 'premium' ? 'Premium' : 'Gratuit'}
          </Typography>
        </Box>
        {profile?.subscriptionType !== 'premium' && (
          <Button variant="contained" color="primary">
            Passer à Premium (9.99€)
          </Button>
        )}
      </Paper>

      {/* Nouvelle section pour les données d'audit */}
      <Paper sx={{ p: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Données d'audit énergétique
          </Typography>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => window.location.href = '/audit'}
          >
            Nouvel audit
          </Button>
        </Box>
        
        {profile?.auditData ? (
          <>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Dernière mise à jour: {new Date(profile.auditData.lastUpdated).toLocaleDateString()}
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle1" gutterBottom>
              Profil
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Type d'utilisateur:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.userType === 'individual' ? 'Particulier' :
                   profile.auditData.userType === 'self_employed' ? 'Indépendant' :
                   profile.auditData.userType === 'small_business' ? 'Petite entreprise' :
                   profile.auditData.userType === 'medium_business' ? 'Moyenne entreprise' :
                   profile.auditData.userType === 'large_business' ? 'Grande entreprise' :
                   profile.auditData.userType || 'Non spécifié'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Région:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.region === 'wallonie' ? 'Wallonie' :
                   profile.auditData.region === 'bruxelles' ? 'Bruxelles' :
                   profile.auditData.region === 'flandre' ? 'Flandre' :
                   profile.auditData.region || 'Non spécifiée'}
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
                  {profile.auditData.electricityUsage ? `${profile.auditData.electricityUsage} kWh/an` : 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Consommation de gaz:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.gasUsage ? 
                    (profile.auditData.gasConsumption ? `${profile.auditData.gasConsumption} m³/an` : 'Oui (quantité non spécifiée)') : 
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
                  {profile.auditData.propertyType || 'Non spécifié'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Surface:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.area ? `${profile.auditData.area} m²` : 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Année de construction:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.constructionYear || 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  État de l'isolation:
                </Typography>
                <Typography variant="body1">
                  {profile.auditData.insulationStatus || 'Non spécifié'}
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
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Typography variant="body1" paragraph>
              Vous n'avez pas encore effectué d'audit énergétique.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => window.location.href = '/audit'}
            >
              Effectuer un audit
            </Button>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default Profile;

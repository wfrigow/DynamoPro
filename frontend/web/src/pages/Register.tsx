import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Link,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  SelectChangeEvent,
  Stepper,
  Step,
  StepLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Divider,
  Checkbox,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { ArrowForward, ArrowBack } from '@mui/icons-material';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    userType: 'individual',
    region: 'wallonie',
    postalCode: '',
    address: '',
    phone: '',
    language: 'fr',
    companyName: '',
    companySize: '',
    companyVat: '',
    termsAccepted: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const name = e.target.name as string;
    const value = e.target.value as string;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateStep = () => {
    const newErrors: Record<string, string> = {};
    
    if (activeStep === 0) {
      if (!formData.email) newErrors.email = 'L\'email est requis';
      else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Format d\'email invalide';
      
      if (!formData.password) newErrors.password = 'Le mot de passe est requis';
      else if (formData.password.length < 8) newErrors.password = 'Le mot de passe doit comporter au moins 8 caractères';
      
      if (!formData.confirmPassword) newErrors.confirmPassword = 'Veuillez confirmer votre mot de passe';
      else if (formData.confirmPassword !== formData.password) newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    } else if (activeStep === 1) {
      if (!formData.name) newErrors.name = 'Le nom est requis';
      if (!formData.postalCode) newErrors.postalCode = 'Le code postal est requis';
      if (formData.userType !== 'individual') {
        if (!formData.companyName) newErrors.companyName = 'Le nom de l\'entreprise est requis';
        if (!formData.companyVat) newErrors.companyVat = 'Le numéro de TVA est requis';
      }
    } else if (activeStep === 2) {
      if (!formData.termsAccepted) newErrors.termsAccepted = 'Vous devez accepter les conditions d\'utilisation';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      if (activeStep === 2) {
        handleSubmit();
      } else {
        setActiveStep(prev => prev + 1);
      }
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = () => {
    // Here you would dispatch an action to register the user
    console.log('Submitting registration:', formData);
    // Redirect to login after successful registration
    navigate('/login');
  };

  const steps = ['Compte', 'Profil', 'Finalisation'];

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Créez votre compte
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  error={!!errors.email}
                  helperText={errors.email}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Mot de passe"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  error={!!errors.password}
                  helperText={errors.password}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Confirmez le mot de passe"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword}
                  required
                />
              </Grid>
            </Grid>
          </Box>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Informations personnelles
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Nom complet"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  error={!!errors.name}
                  helperText={errors.name}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel id="userType-label">Type d'utilisateur</InputLabel>
                  <Select
                    labelId="userType-label"
                    name="userType"
                    value={formData.userType}
                    label="Type d'utilisateur"
                    onChange={handleSelectChange}
                  >
                    <MenuItem value="individual">Particulier</MenuItem>
                    <MenuItem value="self_employed">Indépendant</MenuItem>
                    <MenuItem value="small_business">Petite entreprise</MenuItem>
                    <MenuItem value="medium_business">Moyenne entreprise</MenuItem>
                    <MenuItem value="large_business">Grande entreprise</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel id="region-label">Région</InputLabel>
                  <Select
                    labelId="region-label"
                    name="region"
                    value={formData.region}
                    label="Région"
                    onChange={handleSelectChange}
                  >
                    <MenuItem value="wallonie">Wallonie</MenuItem>
                    <MenuItem value="bruxelles">Bruxelles</MenuItem>
                    <MenuItem value="flandre">Flandre</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Code postal"
                  name="postalCode"
                  value={formData.postalCode}
                  onChange={handleChange}
                  error={!!errors.postalCode}
                  helperText={errors.postalCode}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="language-label">Langue préférée</InputLabel>
                  <Select
                    labelId="language-label"
                    name="language"
                    value={formData.language}
                    label="Langue préférée"
                    onChange={handleSelectChange}
                  >
                    <MenuItem value="fr">Français</MenuItem>
                    <MenuItem value="nl">Nederlands</MenuItem>
                    <MenuItem value="de">Deutsch</MenuItem>
                    <MenuItem value="en">English</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Adresse"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Téléphone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                />
              </Grid>
              
              {formData.userType !== 'individual' && (
                <>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Informations professionnelles
                      </Typography>
                    </Divider>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Nom de l'entreprise"
                      name="companyName"
                      value={formData.companyName}
                      onChange={handleChange}
                      error={!!errors.companyName}
                      helperText={errors.companyName}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Numéro de TVA"
                      name="companyVat"
                      value={formData.companyVat}
                      onChange={handleChange}
                      error={!!errors.companyVat}
                      helperText={errors.companyVat}
                      required
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
                      value={formData.companySize}
                      onChange={handleChange}
                    />
                  </Grid>
                </>
              )}
            </Grid>
          </Box>
        );
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Finaliser votre inscription
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body1" gutterBottom>
                Récapitulatif de vos informations:
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Email:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">{formData.email}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Nom:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">{formData.name}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Type d'utilisateur:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    {formData.userType === 'individual' ? 'Particulier' : 
                     formData.userType === 'self_employed' ? 'Indépendant' :
                     formData.userType === 'small_business' ? 'Petite entreprise' :
                     formData.userType === 'medium_business' ? 'Moyenne entreprise' : 'Grande entreprise'}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Région:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    {formData.region === 'wallonie' ? 'Wallonie' : 
                     formData.region === 'bruxelles' ? 'Bruxelles' : 'Flandre'}
                  </Typography>
                </Grid>
                {formData.userType !== 'individual' && (
                  <>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">Entreprise:</Typography>
                    </Grid>
                    <Grid item xs={8}>
                      <Typography variant="body2">{formData.companyName}</Typography>
                    </Grid>
                  </>
                )}
              </Grid>
            </Box>
            
            <FormControl error={!!errors.termsAccepted} required>
              <FormControlLabel
                control={
                  <Checkbox
                    name="termsAccepted"
                    checked={formData.termsAccepted}
                    onChange={handleChange}
                  />
                }
                label="J'accepte les conditions d'utilisation et la politique de confidentialité"
              />
              {errors.termsAccepted && (
                <FormHelperText>{errors.termsAccepted}</FormHelperText>
              )}
            </FormControl>
          </Box>
        );
      default:
        return <Typography>Étape inconnue</Typography>;
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', pt: 4, pb: 8 }}>
        <Typography
          component="h1"
          variant="h4"
          sx={{ mb: 4, fontWeight: 'bold', color: 'primary.main' }}
        >
          DynamoPro
        </Typography>
        
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {getStepContent(activeStep)}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button 
              variant="outlined"
              onClick={handleBack}
              startIcon={<ArrowBack />}
              disabled={activeStep === 0}
            >
              Retour
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              endIcon={activeStep === steps.length - 1 ? undefined : <ArrowForward />}
            >
              {activeStep === steps.length - 1 ? 'S\'inscrire' : 'Suivant'}
            </Button>
          </Box>
        </Paper>
        
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2">
            Vous avez déjà un compte? {' '}
            <Link component={RouterLink} to="/login" variant="body2">
              Se connecter
            </Link>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default Register;

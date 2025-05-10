import React from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Grid, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  SelectChangeEvent 
} from '@mui/material';

interface ApplicantData {
  name: string;
  email: string;
  phone: string;
  address: string;
  userType: string;
  [key: string]: any;
}

interface ApplicantInfoFormProps {
  data: ApplicantData;
  onChange: (data: Partial<ApplicantData>) => void;
}

const ApplicantInfoForm: React.FC<ApplicantInfoFormProps> = ({ data, onChange }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Informations personnelles
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Veuillez fournir les informations concernant le demandeur de la subvention.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            label="Nom complet"
            name="name"
            value={data.name}
            onChange={handleChange}
            helperText="Nom et prénom du demandeur"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={data.email}
            onChange={handleChange}
            helperText="L'adresse email sera utilisée pour les communications"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            label="Téléphone"
            name="phone"
            value={data.phone}
            onChange={handleChange}
            helperText="Format: +32 xxx xx xx xx"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            label="Adresse"
            name="address"
            value={data.address}
            onChange={handleChange}
            helperText="Adresse complète du demandeur"
            multiline
            rows={2}
          />
        </Grid>

        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel>Type de demandeur</InputLabel>
            <Select
              name="userType"
              value={data.userType}
              label="Type de demandeur"
              onChange={handleSelectChange}
            >
              <MenuItem value="individual">Particulier</MenuItem>
              <MenuItem value="self_employed">Indépendant</MenuItem>
              <MenuItem value="small_business">Petite entreprise (&lt; 50 employés)</MenuItem>
              <MenuItem value="medium_business">Moyenne entreprise (50-250 employés)</MenuItem>
              <MenuItem value="large_business">Grande entreprise (&gt; 250 employés)</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {(data.userType === 'self_employed' || data.userType.includes('business')) && (
          <>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Nom de l'entreprise"
                name="companyName"
                value={data.companyName || ''}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Numéro d'entreprise (BCE)"
                name="companyNumber"
                value={data.companyNumber || ''}
                onChange={handleChange}
                helperText="Format: 0XXX.XXX.XXX"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Secteur d'activité"
                name="businessSector"
                value={data.businessSector || ''}
                onChange={handleChange}
              />
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
};

export default ApplicantInfoForm;

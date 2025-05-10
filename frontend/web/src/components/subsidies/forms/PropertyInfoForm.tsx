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
  SelectChangeEvent,
  FormHelperText
} from '@mui/material';

interface PropertyData {
  address: string;
  type: string;
  yearBuilt: string;
  surfaceArea?: string;
  energyClass?: string;
  [key: string]: any;
}

interface PropertyInfoFormProps {
  data: PropertyData;
  onChange: (data: Partial<PropertyData>) => void;
}

const PropertyInfoForm: React.FC<PropertyInfoFormProps> = ({ data, onChange }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  const validateNumericInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    // Autoriser uniquement les chiffres et le point pour les décimaux
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      onChange({ [name]: value });
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Informations sur le bien immobilier
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Veuillez fournir les informations concernant le bien pour lequel vous demandez une subvention.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            label="Adresse du bien"
            name="address"
            value={data.address}
            onChange={handleChange}
            helperText="Adresse complète où les travaux seront réalisés"
            multiline
            rows={2}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth required>
            <InputLabel>Type de bien</InputLabel>
            <Select
              name="type"
              value={data.type}
              label="Type de bien"
              onChange={handleSelectChange}
            >
              <MenuItem value="house">Maison unifamiliale</MenuItem>
              <MenuItem value="apartment">Appartement</MenuItem>
              <MenuItem value="duplex">Duplex/Triplex</MenuItem>
              <MenuItem value="commercial">Local commercial</MenuItem>
              <MenuItem value="office">Bureau</MenuItem>
              <MenuItem value="industrial">Bâtiment industriel</MenuItem>
              <MenuItem value="other">Autre</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            label="Année de construction"
            name="yearBuilt"
            value={data.yearBuilt}
            onChange={validateNumericInput}
            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
            helperText="Ex: 1985"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Surface habitable (m²)"
            name="surfaceArea"
            value={data.surfaceArea || ''}
            onChange={validateNumericInput}
            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
            helperText="Surface totale du bien en mètres carrés"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Classe énergétique</InputLabel>
            <Select
              name="energyClass"
              value={data.energyClass || ''}
              label="Classe énergétique"
              onChange={handleSelectChange}
            >
              <MenuItem value="">Non connue</MenuItem>
              <MenuItem value="A+">A+</MenuItem>
              <MenuItem value="A">A</MenuItem>
              <MenuItem value="B">B</MenuItem>
              <MenuItem value="C">C</MenuItem>
              <MenuItem value="D">D</MenuItem>
              <MenuItem value="E">E</MenuItem>
              <MenuItem value="F">F</MenuItem>
              <MenuItem value="G">G</MenuItem>
            </Select>
            <FormHelperText>Si vous disposez d'un certificat PEB</FormHelperText>
          </FormControl>
        </Grid>

        {data.type === 'house' && (
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Type de maison</InputLabel>
              <Select
                name="houseType"
                value={data.houseType || ''}
                label="Type de maison"
                onChange={handleSelectChange}
              >
                <MenuItem value="detached">Maison 4 façades</MenuItem>
                <MenuItem value="semi_detached">Maison 3 façades</MenuItem>
                <MenuItem value="terraced">Maison mitoyenne</MenuItem>
                <MenuItem value="bungalow">Bungalow</MenuItem>
                <MenuItem value="villa">Villa</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        )}

        {data.type === 'apartment' && (
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Étage"
              name="floor"
              value={data.floor || ''}
              onChange={validateNumericInput}
              inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
              helperText="Étage où se situe l'appartement"
            />
          </Grid>
        )}

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Informations complémentaires"
            name="additionalInfo"
            value={data.additionalInfo || ''}
            onChange={handleChange}
            multiline
            rows={3}
            helperText="Précisions utiles sur le bien (état général, rénovations précédentes, etc.)"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default PropertyInfoForm;

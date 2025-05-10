import React, { useState, useEffect } from 'react';
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
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormHelperText
} from '@mui/material';
import { ExpandMore, Euro } from '@mui/icons-material';

interface ProjectData {
  description: string;
  estimatedCost: number | string;
  estimatedCompletionDate: string;
  [key: string]: any;
}

interface TechnicalDetails {
  [key: string]: any;
}

interface ProjectInfoFormProps {
  data: ProjectData;
  subsidyType: string[];
  technicalDetails?: TechnicalDetails;
  onChange: (data: Partial<ProjectData> | { technicalDetails: TechnicalDetails }) => void;
}

const ProjectInfoForm: React.FC<ProjectInfoFormProps> = ({ 
  data, 
  subsidyType, 
  technicalDetails,
  onChange 
}) => {
  const [expanded, setExpanded] = useState(true);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  const handleTechnicalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (technicalDetails) {
      onChange({ 
        technicalDetails: { 
          ...technicalDetails, 
          [name]: value 
        } 
      });
    }
  };

  const handleTechnicalSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    
    if (technicalDetails) {
      onChange({ 
        technicalDetails: { 
          ...technicalDetails, 
          [name]: value 
        } 
      });
    }
  };

  const validateNumericInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    // Autoriser uniquement les chiffres et le point pour les décimaux
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      onChange({ [name]: value });
    }
  };

  // Définir la date minimale à aujourd'hui
  const today = new Date().toISOString().split('T')[0];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Informations sur le projet
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Veuillez décrire le projet pour lequel vous demandez une subvention et fournir les détails techniques requis.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            label="Description du projet"
            name="description"
            value={data.description}
            onChange={handleChange}
            multiline
            rows={3}
            helperText="Décrivez brièvement les travaux prévus"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            label="Coût estimé"
            name="estimatedCost"
            value={data.estimatedCost}
            onChange={validateNumericInput}
            InputProps={{
              startAdornment: <InputAdornment position="start"><Euro /></InputAdornment>,
              inputMode: 'decimal',
            }}
            helperText="Montant total estimé des travaux (TVAC)"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            label="Date prévue d'achèvement"
            name="estimatedCompletionDate"
            type="date"
            value={data.estimatedCompletionDate}
            onChange={handleChange}
            InputLabelProps={{ shrink: true }}
            inputProps={{ min: today }}
            helperText="Date prévue de fin des travaux"
          />
        </Grid>

        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel>Travaux déjà commencés ?</InputLabel>
            <Select
              name="workStarted"
              value={data.workStarted || 'no'}
              label="Travaux déjà commencés ?"
              onChange={handleSelectChange}
            >
              <MenuItem value="no">Non, pas encore</MenuItem>
              <MenuItem value="yes">Oui, en cours</MenuItem>
              <MenuItem value="completed">Oui, terminés</MenuItem>
            </Select>
            <FormHelperText>Pour certaines subventions, les travaux doivent être demandés avant leur démarrage</FormHelperText>
          </FormControl>
        </Grid>

        {data.workStarted === 'yes' && (
          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              label="Date de début des travaux"
              name="workStartDate"
              type="date"
              value={data.workStartDate || ''}
              onChange={handleChange}
              InputLabelProps={{ shrink: true }}
              helperText="Date à laquelle les travaux ont commencé"
            />
          </Grid>
        )}

        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel>Entrepreneur sélectionné ?</InputLabel>
            <Select
              name="contractorSelected"
              value={data.contractorSelected || 'no'}
              label="Entrepreneur sélectionné ?"
              onChange={handleSelectChange}
            >
              <MenuItem value="no">Non, pas encore</MenuItem>
              <MenuItem value="yes">Oui</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {data.contractorSelected === 'yes' && (
          <>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Nom de l'entrepreneur"
                name="contractorName"
                value={data.contractorName || ''}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Numéro d'entreprise (BCE)"
                name="contractorBCE"
                value={data.contractorBCE || ''}
                onChange={handleChange}
                helperText="Format: 0XXX.XXX.XXX"
              />
            </Grid>
          </>
        )}
      </Grid>

      {/* Section pour les détails techniques spécifiques au type de subvention */}
      {technicalDetails && (
        <Accordion 
          expanded={expanded} 
          onChange={() => setExpanded(!expanded)}
          sx={{ mt: 4 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">Détails techniques</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Détails pour isolation */}
              {subsidyType.includes('Isolation') && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Spécifications de l'isolation
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Matériau isolant"
                      name="insulationMaterial"
                      value={technicalDetails.insulationMaterial || ''}
                      onChange={handleTechnicalChange}
                      helperText="Ex: Laine minérale, Polystyrène expansé, etc."
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Surface à isoler (m²)"
                      name="surfaceArea"
                      value={technicalDetails.surfaceArea || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'numeric' }}
                      helperText="Surface en mètres carrés"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Valeur R (m²K/W)"
                      name="rValue"
                      value={technicalDetails.rValue || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'decimal' }}
                      helperText="Coefficient de résistance thermique du matériau (minimum 4.5 m²K/W requis)"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Épaisseur (mm)"
                      name="thickness"
                      value={technicalDetails.thickness || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'numeric' }}
                    />
                  </Grid>
                </>
              )}

              {/* Détails pour les panneaux solaires */}
              {subsidyType.includes('Solaire') && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Spécifications des panneaux photovoltaïques
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Puissance crête totale (kWc)"
                      name="peakPower"
                      value={technicalDetails.peakPower || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'decimal' }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Nombre de panneaux"
                      name="panelCount"
                      value={technicalDetails.panelCount || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'numeric' }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Rendement des panneaux (%)"
                      name="efficiency"
                      value={technicalDetails.efficiency || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'decimal' }}
                      helperText="Minimum 21% requis pour certaines subventions"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Orientation principale</InputLabel>
                      <Select
                        name="orientation"
                        value={technicalDetails.orientation || ''}
                        label="Orientation principale"
                        onChange={handleTechnicalSelectChange}
                      >
                        <MenuItem value="north">Nord</MenuItem>
                        <MenuItem value="north-east">Nord-Est</MenuItem>
                        <MenuItem value="east">Est</MenuItem>
                        <MenuItem value="south-east">Sud-Est</MenuItem>
                        <MenuItem value="south">Sud</MenuItem>
                        <MenuItem value="south-west">Sud-Ouest</MenuItem>
                        <MenuItem value="west">Ouest</MenuItem>
                        <MenuItem value="north-west">Nord-Ouest</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </>
              )}

              {/* Détails pour pompe à chaleur */}
              {subsidyType.includes('Chaleur') && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Spécifications de la pompe à chaleur
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Type de pompe à chaleur</InputLabel>
                      <Select
                        name="heatPumpType"
                        value={technicalDetails.heatPumpType || ''}
                        label="Type de pompe à chaleur"
                        onChange={handleTechnicalSelectChange}
                      >
                        <MenuItem value="air-air">Air-Air</MenuItem>
                        <MenuItem value="air-eau">Air-Eau</MenuItem>
                        <MenuItem value="sol-eau">Sol-Eau (géothermie)</MenuItem>
                        <MenuItem value="eau-eau">Eau-Eau</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Coefficient de performance saisonnier (SCOP)"
                      name="scopValue"
                      value={technicalDetails.scopValue || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'decimal' }}
                      helperText="Minimum 3.5 requis pour être éligible"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Puissance thermique (kW)"
                      name="thermalPower"
                      value={technicalDetails.thermalPower || ''}
                      onChange={handleTechnicalChange}
                      inputProps={{ inputMode: 'decimal' }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Usage principal</InputLabel>
                      <Select
                        name="mainUsage"
                        value={technicalDetails.mainUsage || ''}
                        label="Usage principal"
                        onChange={handleTechnicalSelectChange}
                      >
                        <MenuItem value="heating">Chauffage uniquement</MenuItem>
                        <MenuItem value="cooling">Climatisation uniquement</MenuItem>
                        <MenuItem value="both">Chauffage et climatisation</MenuItem>
                        <MenuItem value="water">Eau chaude sanitaire</MenuItem>
                        <MenuItem value="complete">Solution complète (chauffage, climatisation et eau chaude)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </>
              )}

              {/* Champs communs pour tous les types */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Certification de l'installateur"
                  name="installerCertification"
                  value={technicalDetails.installerCertification || ''}
                  onChange={handleTechnicalChange}
                  helperText="Certifications spécifiques de l'installateur (ex: RESCert, QualiPV, etc.)"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Informations techniques supplémentaires"
                  name="additionalTechnicalInfo"
                  value={technicalDetails.additionalTechnicalInfo || ''}
                  onChange={handleTechnicalChange}
                  multiline
                  rows={3}
                  helperText="Autres informations techniques pertinentes pour votre demande"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
};

export default ProjectInfoForm;

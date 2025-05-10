import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  AlertTitle,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow
} from '@mui/material';
import { 
  PersonOutline, 
  HomeOutlined, 
  BuildOutlined, 
  AccountBalanceOutlined,
  InsertDriveFile,
  ExpandMore,
  CheckCircle,
  ErrorOutline
} from '@mui/icons-material';
import { SubsidyType } from '../SubsidyCard';
import { FormData } from '../SubsidyApplicationForm';

interface DocumentType {
  id: string;
  name: string;
  description: string;
  required: boolean;
  type: string;
}

interface ReviewSubmitFormProps {
  formData: FormData;
  subsidy: SubsidyType;
  requiredDocuments: DocumentType[];
}

const ReviewSubmitForm: React.FC<ReviewSubmitFormProps> = ({ 
  formData, 
  subsidy, 
  requiredDocuments 
}) => {
  // Vérifier si les documents requis sont téléchargés
  const missingDocuments = requiredDocuments
    .filter(doc => doc.required && !formData.documents[doc.id]?.uploaded);

  // Vérifier si toutes les étapes sont complètes
  const isApplicantInfoComplete = formData.applicant.name && formData.applicant.email && formData.applicant.phone;
  const isPropertyInfoComplete = formData.property.address && formData.property.type;
  const isProjectInfoComplete = formData.project.description && formData.project.estimatedCost && formData.project.estimatedCompletionDate;
  const isAllComplete = isApplicantInfoComplete && isPropertyInfoComplete && isProjectInfoComplete && missingDocuments.length === 0;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Révision et soumission
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Veuillez vérifier toutes les informations avant de soumettre votre demande de subvention.
      </Typography>

      {!isAllComplete && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <AlertTitle>Information incomplète</AlertTitle>
          Certaines informations sont manquantes ou incomplètes. Veuillez revenir aux étapes précédentes pour compléter votre demande.
        </Alert>
      )}

      <Box mb={3}>
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Détails de la subvention
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, mb: 3, backgroundColor: '#f9f9f9' }}>
          <Typography variant="h6" color="primary" gutterBottom>
            {subsidy.name}
          </Typography>
          <Typography variant="body2" paragraph>
            {subsidy.description}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">
                Fournisseur:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {subsidy.provider}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">
                Régions applicables:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {subsidy.regions.join(', ')}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              {subsidy.maxAmount && (
                <>
                  <Typography variant="subtitle2">
                    Montant maximum:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {subsidy.maxAmount.toLocaleString()}€
                  </Typography>
                </>
              )}
            </Grid>
            <Grid item xs={12} sm={6}>
              {subsidy.percentage && (
                <>
                  <Typography variant="subtitle2">
                    Pourcentage des coûts éligibles:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {subsidy.percentage}%
                  </Typography>
                </>
              )}
            </Grid>
          </Grid>
        </Paper>

        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            aria-controls="panel1a-content"
            id="panel1a-header"
          >
            <Box display="flex" alignItems="center">
              <PersonOutline sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Informations du demandeur</Typography>
              {isApplicantInfoComplete ? (
                <Chip 
                  icon={<CheckCircle fontSize="small" />} 
                  label="Complet" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 2 }}
                />
              ) : (
                <Chip 
                  icon={<ErrorOutline fontSize="small" />} 
                  label="Incomplet" 
                  size="small" 
                  color="warning" 
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell component="th" scope="row" width="30%">
                      Nom complet
                    </TableCell>
                    <TableCell>{formData.applicant.name || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Email
                    </TableCell>
                    <TableCell>{formData.applicant.email || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Téléphone
                    </TableCell>
                    <TableCell>{formData.applicant.phone || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Adresse
                    </TableCell>
                    <TableCell>{formData.applicant.address || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Type de demandeur
                    </TableCell>
                    <TableCell>
                      {formData.applicant.userType === 'individual' ? 'Particulier' : 
                       formData.applicant.userType === 'self_employed' ? 'Indépendant' :
                       formData.applicant.userType === 'small_business' ? 'Petite entreprise' :
                       formData.applicant.userType === 'medium_business' ? 'Moyenne entreprise' :
                       formData.applicant.userType === 'large_business' ? 'Grande entreprise' :
                       formData.applicant.userType || <Typography color="error">Non renseigné</Typography>}
                    </TableCell>
                  </TableRow>
                  {formData.applicant.companyName && (
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Nom de l'entreprise
                      </TableCell>
                      <TableCell>{formData.applicant.companyName}</TableCell>
                    </TableRow>
                  )}
                  {formData.applicant.companyNumber && (
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Numéro d'entreprise (BCE)
                      </TableCell>
                      <TableCell>{formData.applicant.companyNumber}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>

        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            aria-controls="panel2a-content"
            id="panel2a-header"
          >
            <Box display="flex" alignItems="center">
              <HomeOutlined sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Informations sur le bien</Typography>
              {isPropertyInfoComplete ? (
                <Chip 
                  icon={<CheckCircle fontSize="small" />} 
                  label="Complet" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 2 }}
                />
              ) : (
                <Chip 
                  icon={<ErrorOutline fontSize="small" />} 
                  label="Incomplet" 
                  size="small" 
                  color="warning" 
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell component="th" scope="row" width="30%">
                      Adresse du bien
                    </TableCell>
                    <TableCell>{formData.property.address || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Type de bien
                    </TableCell>
                    <TableCell>
                      {formData.property.type === 'house' ? 'Maison unifamiliale' : 
                       formData.property.type === 'apartment' ? 'Appartement' :
                       formData.property.type === 'duplex' ? 'Duplex/Triplex' :
                       formData.property.type === 'commercial' ? 'Local commercial' :
                       formData.property.type === 'office' ? 'Bureau' :
                       formData.property.type === 'industrial' ? 'Bâtiment industriel' :
                       formData.property.type || <Typography color="error">Non renseigné</Typography>}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Année de construction
                    </TableCell>
                    <TableCell>{formData.property.yearBuilt || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  {formData.property.surfaceArea && (
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Surface habitable
                      </TableCell>
                      <TableCell>{formData.property.surfaceArea} m²</TableCell>
                    </TableRow>
                  )}
                  {formData.property.energyClass && (
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Classe énergétique
                      </TableCell>
                      <TableCell>{formData.property.energyClass}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>

        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            aria-controls="panel3a-content"
            id="panel3a-header"
          >
            <Box display="flex" alignItems="center">
              <BuildOutlined sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Informations sur le projet</Typography>
              {isProjectInfoComplete ? (
                <Chip 
                  icon={<CheckCircle fontSize="small" />} 
                  label="Complet" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 2 }}
                />
              ) : (
                <Chip 
                  icon={<ErrorOutline fontSize="small" />} 
                  label="Incomplet" 
                  size="small" 
                  color="warning" 
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell component="th" scope="row" width="30%">
                      Description du projet
                    </TableCell>
                    <TableCell>{formData.project.description || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Coût estimé
                    </TableCell>
                    <TableCell>
                      {formData.project.estimatedCost 
                        ? `${Number(formData.project.estimatedCost).toLocaleString()}€` 
                        : <Typography color="error">Non renseigné</Typography>}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Date d'achèvement prévue
                    </TableCell>
                    <TableCell>{formData.project.estimatedCompletionDate || <Typography color="error">Non renseigné</Typography>}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Travaux déjà commencés
                    </TableCell>
                    <TableCell>
                      {formData.project.workStarted === 'no' ? 'Non, pas encore' : 
                       formData.project.workStarted === 'yes' ? 'Oui, en cours' :
                       formData.project.workStarted === 'completed' ? 'Oui, terminés' :
                       <Typography color="error">Non renseigné</Typography>}
                    </TableCell>
                  </TableRow>
                  {formData.project.workStartDate && (
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Date de début des travaux
                      </TableCell>
                      <TableCell>{formData.project.workStartDate}</TableCell>
                    </TableRow>
                  )}
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Entrepreneur sélectionné
                    </TableCell>
                    <TableCell>
                      {formData.project.contractorSelected === 'yes' ? 'Oui' : 
                       formData.project.contractorSelected === 'no' ? 'Non, pas encore' :
                       <Typography color="error">Non renseigné</Typography>}
                    </TableCell>
                  </TableRow>
                  {formData.project.contractorName && (
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Nom de l'entrepreneur
                      </TableCell>
                      <TableCell>{formData.project.contractorName}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {formData.technicalDetails && (
              <Box mt={3}>
                <Typography variant="subtitle2" gutterBottom>
                  Détails techniques
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {Object.entries(formData.technicalDetails).map(([key, value]) => (
                        value && (
                          <TableRow key={key}>
                            <TableCell component="th" scope="row" width="30%">
                              {key === 'insulationMaterial' ? 'Matériau isolant' :
                               key === 'surfaceArea' ? 'Surface à isoler' :
                               key === 'rValue' ? 'Valeur R (m²K/W)' :
                               key === 'thickness' ? 'Épaisseur (mm)' :
                               key === 'peakPower' ? 'Puissance crête (kWc)' :
                               key === 'panelCount' ? 'Nombre de panneaux' :
                               key === 'efficiency' ? 'Rendement (%)' :
                               key === 'orientation' ? 'Orientation' :
                               key === 'heatPumpType' ? 'Type de pompe à chaleur' :
                               key === 'scopValue' ? 'SCOP' :
                               key === 'thermalPower' ? 'Puissance thermique (kW)' :
                               key === 'mainUsage' ? 'Usage principal' :
                               key === 'installerCertification' ? 'Certification installateur' :
                               key === 'additionalTechnicalInfo' ? 'Infos techniques supplémentaires' :
                               key}
                            </TableCell>
                            <TableCell>{value}</TableCell>
                          </TableRow>
                        )
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            aria-controls="panel4a-content"
            id="panel4a-header"
          >
            <Box display="flex" alignItems="center">
              <InsertDriveFile sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Documents</Typography>
              {missingDocuments.length === 0 ? (
                <Chip 
                  icon={<CheckCircle fontSize="small" />} 
                  label="Complet" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 2 }}
                />
              ) : (
                <Chip 
                  icon={<ErrorOutline fontSize="small" />} 
                  label={`${missingDocuments.length} document(s) manquant(s)`} 
                  size="small" 
                  color="warning" 
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {missingDocuments.length > 0 ? (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <AlertTitle>Documents manquants</AlertTitle>
                Les documents suivants sont obligatoires et doivent être téléchargés:
                <List dense>
                  {missingDocuments.map(doc => (
                    <ListItem key={doc.id}>
                      <ListItemText primary={doc.name} secondary={doc.description} />
                    </ListItem>
                  ))}
                </List>
              </Alert>
            ) : (
              <Alert severity="success" sx={{ mb: 2 }}>
                Tous les documents requis ont été téléchargés.
              </Alert>
            )}

            <List>
              {requiredDocuments.map(doc => (
                <ListItem key={doc.id}>
                  <ListItemIcon>
                    {formData.documents[doc.id]?.uploaded ? (
                      <CheckCircle color="success" />
                    ) : (
                      <ErrorOutline color="warning" />
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
                    secondary={formData.documents[doc.id]?.file?.name || "Aucun fichier téléchargé"}
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            aria-controls="panel5a-content"
            id="panel5a-header"
          >
            <Box display="flex" alignItems="center">
              <AccountBalanceOutlined sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Coordonnées bancaires</Typography>
              {formData.bankDetails?.iban ? (
                <Chip 
                  icon={<CheckCircle fontSize="small" />} 
                  label="Renseigné" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 2 }}
                />
              ) : (
                <Chip 
                  icon={<ErrorOutline fontSize="small" />} 
                  label="Non renseigné" 
                  size="small" 
                  color="default" 
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell component="th" scope="row" width="30%">
                      Titulaire du compte
                    </TableCell>
                    <TableCell>{formData.bankDetails?.accountHolder || "Non renseigné"}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      IBAN
                    </TableCell>
                    <TableCell>{formData.bankDetails?.iban || "Non renseigné"}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box>
        <Alert severity="info">
          <AlertTitle>Déclaration sur l'honneur</AlertTitle>
          En soumettant cette demande, je certifie que toutes les informations fournies sont exactes et complètes. 
          Je comprends que toute fausse déclaration peut entraîner le rejet de ma demande ou le remboursement 
          des subventions déjà perçues.
        </Alert>
      </Box>
    </Box>
  );
};

export default ReviewSubmitForm;

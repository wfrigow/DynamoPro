import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Stepper, 
  Step, 
  StepLabel, 
  Paper, 
  Divider, 
  CircularProgress,
  Alert,
  AlertTitle
} from '@mui/material';
import { SubsidyType } from './SubsidyCard';
import { SubsidyDetail } from '../../services/SubsidyService';
import ApplicantInfoForm from './forms/ApplicantInfoForm';
import PropertyInfoForm from './forms/PropertyInfoForm';
import ProjectInfoForm from './forms/ProjectInfoForm';
import DocumentsUploadForm from './forms/DocumentsUploadForm';
import ReviewSubmitForm from './forms/ReviewSubmitForm';

export interface FormData {
  applicant: {
    name: string;
    email: string;
    phone: string;
    address: string;
    userType: string;
    [key: string]: any;
  };
  property: {
    address: string;
    type: string;
    yearBuilt: string;
    [key: string]: any;
  };
  project: {
    description: string;
    estimatedCost: number | string;
    estimatedCompletionDate: string;
    [key: string]: any;
  };
  bankDetails: {
    accountHolder: string;
    iban: string;
    [key: string]: any;
  };
  documents: {
    [key: string]: {
      file: File | null;
      uploaded: boolean;
      validated: boolean;
      name: string;
    };
  };
  technicalDetails?: {
    [key: string]: any;
  };
}

interface DocumentType {
  id: string;
  name: string;
  description: string;
  required: boolean;
  type: string;
}

interface SubsidyApplicationFormProps {
  subsidyId: string;
  recommendationId?: string;
  initialData?: Partial<FormData>;
  subsidyDetails?: SubsidyDetail | null;
  onSubmit: (data: FormData) => Promise<void>;
  onSaveDraft: (data: FormData) => Promise<void>;
}

const SubsidyApplicationForm: React.FC<SubsidyApplicationFormProps> = ({
  subsidyId,
  recommendationId,
  initialData,
  subsidyDetails,
  onSubmit,
  onSaveDraft
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [subsidy, setSubsidy] = useState<SubsidyType | null>(null);
  const [requiredDocuments, setRequiredDocuments] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({
    applicant: {
      name: '',
      email: '',
      phone: '',
      address: '',
      userType: 'individual'
    },
    property: {
      address: '',
      type: 'house',
      yearBuilt: ''
    },
    project: {
      description: '',
      estimatedCost: '',
      estimatedCompletionDate: ''
    },
    bankDetails: {
      accountHolder: '',
      iban: ''
    },
    documents: {}
  });
  const [submitting, setSubmitting] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [draftSaved, setDraftSaved] = useState(false);

  const steps = [
    'Informations personnelles',
    'Informations sur le bien',
    'Informations sur le projet',
    'Documents requis',
    'Révision et soumission'
  ];

  // Charger les données de la subvention si elles ne sont pas déjà fournies
  useEffect(() => {
    const fetchSubsidyDetails = async () => {
      // Si les détails de la subvention sont déjà fournis, les utiliser directement
      if (subsidyDetails) {
        // Convertir SubsidyDetail en SubsidyType
        const convertedSubsidy: SubsidyType = {
          id: subsidyDetails.id,
          name: subsidyDetails.name,
          description: subsidyDetails.description,
          provider: subsidyDetails.provider,
          regions: subsidyDetails.regions,
          maxAmount: subsidyDetails.max_amount,
          percentage: subsidyDetails.percentage,
          keywords: subsidyDetails.keywords,
          eligibility: subsidyDetails.eligibility || []
        };
        
        setSubsidy(convertedSubsidy);
        
        // Configurer les documents requis basés sur les détails de la subvention
        if (subsidyDetails.required_documents) {
          setRequiredDocuments(subsidyDetails.required_documents);
        } else {
          // Documents par défaut si aucun n'est spécifié
          setRequiredDocuments([
            {
              id: 'identity',
              name: 'Pièce d\'identité',
              description: 'Copie de votre carte d\'identité ou passeport',
              required: true,
              type: 'identity'
            },
            {
              id: 'proof_address',
              name: 'Preuve de domicile',
              description: 'Facture récente (moins de 3 mois)',
              required: true,
              type: 'proof'
            }
          ]);
        }
        
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        
        // Simuler un appel API si les détails ne sont pas fournis
        // Dans une implémentation réelle, vous appelleriez votre API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Exemple de données (à remplacer par une vraie API)
        const mockSubsidy: SubsidyType = {
          id: subsidyId,
          name: "Prime Énergie - Isolation Toiture",
          description: "Prime pour l'isolation thermique du toit ou des combles dans une habitation existante.",
          provider: "Service Public de Wallonie - Énergie",
          regions: ["wallonie"],
          maxAmount: 2000,
          percentage: 35,
          keywords: ["Isolation", "Rénovation", "Économie d'énergie"],
          eligibility: [
            "Habitation située en Wallonie",
            "Coefficient de résistance thermique R ≥ 4,5 m²K/W",
            "Travaux réalisés par un entrepreneur enregistré"
          ],
          documentationUrl: "https://energie.wallonie.be/fr/prime-isolation-du-toit.html"
        };
        
        const mockDocuments: DocumentType[] = [
          {
            id: "doc1",
            name: "Carte d'identité",
            description: "Copie de la carte d'identité du demandeur",
            required: true,
            type: "identity"
          },
          {
            id: "doc2",
            name: "Preuve de propriété",
            description: "Acte de propriété ou bail de location",
            required: true,
            type: "ownership"
          },
          {
            id: "doc3",
            name: "Devis détaillé",
            description: "Devis détaillé de l'entrepreneur",
            required: true,
            type: "quote"
          },
          {
            id: "doc4",
            name: "Fiche technique",
            description: "Fiche technique du matériau isolant utilisé",
            required: true,
            type: "technicalSpec"
          }
        ];
        
        // Initialiser l'état des documents
        const docState: {[key: string]: any} = {};
        mockDocuments.forEach(doc => {
          docState[doc.id] = {
            file: null,
            uploaded: false,
            validated: false,
            name: doc.name
          };
        });
        
        // Mettre à jour l'état
        setSubsidy(mockSubsidy);
        setRequiredDocuments(mockDocuments);
        setFormData(prev => ({
          ...prev,
          documents: docState,
          // Si le type de subvention nécessite des détails techniques spécifiques
          technicalDetails: mockSubsidy.keywords.includes("Isolation") ? {
            insulationMaterial: '',
            surfaceArea: '',
            rValue: '',
            installerCertification: ''
          } : undefined
        }));
        
        // Fusionner avec les données initiales si fournies
        if (initialData) {
          setFormData(prev => ({ ...prev, ...initialData }));
        }
        
        setLoading(false);
      } catch (err) {
        setError("Erreur lors du chargement des détails de la subvention");
        setLoading(false);
        console.error(err);
      }
    };
    
    fetchSubsidyDetails();
  }, [subsidyId, recommendationId, initialData, subsidyDetails]);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    // Sauvegarder automatiquement un brouillon lors de la progression
    if (activeStep < steps.length - 1) {
      handleSaveDraft();
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleFormChange = (step: number, data: any) => {
    setFormData(prev => {
      const newData = { ...prev };
      
      switch(step) {
        case 0:
          newData.applicant = { ...newData.applicant, ...data };
          break;
        case 1:
          newData.property = { ...newData.property, ...data };
          break;
        case 2:
          newData.project = { ...newData.project, ...data };
          break;
        case 3:
          newData.documents = { ...newData.documents, ...data };
          break;
        default:
          break;
      }
      
      return newData;
    });
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      await onSubmit(formData);
      setSubmitSuccess(true);
      setSubmitting(false);
    } catch (err) {
      setError(typeof err === 'string' ? err : (err instanceof Error ? err.message : "Erreur lors de la soumission du formulaire"));
      setSubmitting(false);
      console.error(err);
    }
  };

  const handleSaveDraft = async () => {
    try {
      setSavingDraft(true);
      await onSaveDraft(formData);
      setDraftSaved(true);
      setTimeout(() => setDraftSaved(false), 3000); // Message de confirmation pendant 3 secondes
      setSavingDraft(false);
    } catch (err) {
      setError("Erreur lors de la sauvegarde du brouillon");
      setSavingDraft(false);
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 3 }}>
        <AlertTitle>Erreur</AlertTitle>
        {error}
      </Alert>
    );
  }

  if (submitSuccess) {
    return (
      <Alert severity="success" sx={{ my: 3 }}>
        <AlertTitle>Demande soumise avec succès</AlertTitle>
        Votre demande de subvention a été soumise avec succès. Vous recevrez un email de confirmation et vous pourrez suivre l'état de votre demande dans la section "Mes demandes" de votre profil.
      </Alert>
    );
  }

  if (!subsidy) {
    return (
      <Alert severity="warning" sx={{ my: 3 }}>
        <AlertTitle>Subvention non trouvée</AlertTitle>
        Impossible de trouver les détails de la subvention demandée.
      </Alert>
    );
  }

  return (
    <Box mb={4}>
      <Typography variant="h5" gutterBottom color="primary" fontWeight={600}>
        Demande de {subsidy.name}
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        {subsidy.description}
      </Typography>
      
      <Divider sx={{ my: 3 }} />
      
      {draftSaved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Brouillon sauvegardé avec succès
        </Alert>
      )}
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        {activeStep === 0 && (
          <ApplicantInfoForm 
            data={formData.applicant} 
            onChange={(data) => handleFormChange(0, data)}
          />
        )}
        
        {activeStep === 1 && (
          <PropertyInfoForm 
            data={formData.property} 
            onChange={(data) => handleFormChange(1, data)}
          />
        )}
        
        {activeStep === 2 && (
          <ProjectInfoForm 
            data={formData.project}
            subsidyType={subsidy.keywords}
            technicalDetails={formData.technicalDetails}
            onChange={(data) => handleFormChange(2, data)}
          />
        )}
        
        {activeStep === 3 && (
          <DocumentsUploadForm 
            documents={formData.documents}
            requiredDocuments={requiredDocuments}
            onChange={(data) => handleFormChange(3, data)}
          />
        )}
        
        {activeStep === 4 && (
          <ReviewSubmitForm 
            formData={formData} 
            subsidy={subsidy}
            requiredDocuments={requiredDocuments}
          />
        )}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            variant="outlined"
            color="primary"
            disabled={activeStep === 0 || submitting}
            onClick={handleBack}
          >
            Précédent
          </Button>
          
          <Box>
            <Button
              variant="outlined"
              color="primary"
              onClick={handleSaveDraft}
              disabled={savingDraft || submitting}
              sx={{ mr: 1 }}
            >
              {savingDraft ? 'Sauvegarde...' : 'Sauvegarder le brouillon'}
            </Button>
            
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={submitting}
              >
                {submitting ? 'Soumission...' : 'Soumettre la demande'}
              </Button>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
              >
                Suivant
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default SubsidyApplicationForm;

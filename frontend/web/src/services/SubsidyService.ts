import apiService from './api';
import { API_CONFIG } from '../config';

// Configuration de l'URL de base de l'API
const API_BASE_URL = API_CONFIG.SUBSIDIES_URL;

// Types pour les subventions
export interface Document {
  id: string;
  name: string;
  description: string;
  type: string;
  required: boolean;
  format: string[];
}

export interface Subsidy {
  id: string;
  name: string;
  provider: string;
  description: string;
  regions: string[];
  domains: string[];
  max_amount: number | null;
  percentage: number | null;
  keywords: string[];
  status: string;
}

export interface SubsidyDetail extends Subsidy {
  conditions: string | null;
  eligibility: string[];
  user_types: string[];
  required_documents: Document[];
  application_process: string | null;
  documentation_url: string | null;
  min_year_built: number | null;
  max_year_built: number | null;
  additional_info: string | null;
}

export interface SubsidySearchParams {
  query?: string;
  regions?: string[];
  domains?: string[];
  user_types?: string[];
  min_amount?: number;
  max_amount?: number;
  year_built?: number;
  language?: string;
}

export interface SubsidySearchResponse {
  count: number;
  results: Subsidy[];
}

// Types pour les intégrations avec les recommandations
export interface SubsidyRecommendation {
  subsidy_id: string;
  name: string;
  provider: string;
  description: string;
  max_amount: number | null;
  percentage: number | null;
  relevance_score: number;
  recommendation_id: string;
  recommendation_title: string;
  match_reason: string;
}

export interface RecommendationSubsidies {
  recommendation_id: string;
  subsidies: SubsidyRecommendation[];
}

export interface RecommendationSetSubsidies {
  recommendation_set_id: string;
  recommendations: RecommendationSubsidies[];
}

// Types pour les intégrations avec l'optimisation
export interface SubsidyOptimizationRecommendation {
  subsidy_id: string;
  name: string;
  provider: string;
  description: string;
  max_amount: number | null;
  percentage: number | null;
  relevance_score: number;
  project_id: string;
  project_name: string;
  measure_id?: string;
  measure_name?: string;
  match_reason: string;
  potential_savings?: number;
}

export interface OptimizationMeasureSubsidies {
  measure_id: string;
  subsidies: SubsidyOptimizationRecommendation[];
}

export interface OptimizationProjectSubsidies {
  project_id: string;
  measures: OptimizationMeasureSubsidies[];
}

// Types pour les intégrations avec le passeport vert
export interface SubsidyPropertyRecommendation {
  subsidy_id: string;
  name: string;
  provider: string;
  description: string;
  max_amount: number | null;
  percentage: number | null;
  relevance_score: number;
  property_id: string;
  property_address: string;
  match_reason: string;
}

export interface PropertySubsidies {
  property_id: string;
  property_address: string;
  subsidies: SubsidyPropertyRecommendation[];
}

// Service pour interagir avec l'API de subventions
class SubsidyService {
  // Méthodes pour les subventions
  async searchSubsidies(params: SubsidySearchParams): Promise<SubsidySearchResponse> {
    try {
      return await apiService.get(`${API_BASE_URL}`, params);
    } catch (error) {
      console.error('Error searching subsidies:', error);
      throw error;
    }
  }

  async getSubsidyById(id: string, language: string = 'fr'): Promise<SubsidyDetail> {
    try {
      return await apiService.get(`${API_BASE_URL}/${id}`, { language });
    } catch (error) {
      console.error(`Error getting subsidy with ID ${id}:`, error);
      throw error;
    }
  }

  async getSubsidiesByRegion(region: string, language: string = 'fr'): Promise<SubsidySearchResponse> {
    try {
      return await apiService.get(`${API_BASE_URL}/regions/${region}`, { language });
    } catch (error) {
      console.error(`Error getting subsidies for region ${region}:`, error);
      throw error;
    }
  }

  async getSubsidiesByDomain(domain: string, language: string = 'fr'): Promise<SubsidySearchResponse> {
    try {
      return await apiService.get(`${API_BASE_URL}/domains/${domain}`, { language });
    } catch (error) {
      console.error(`Error getting subsidies for domain ${domain}:`, error);
      throw error;
    }
  }

  async getSubsidiesByUserType(userType: string, language: string = 'fr'): Promise<SubsidySearchResponse> {
    try {
      return await apiService.get(`${API_BASE_URL}/user-types/${userType}`, { language });
    } catch (error) {
      console.error(`Error getting subsidies for user type ${userType}:`, error);
      throw error;
    }
  }

  async getSubsidiesByKeyword(keyword: string, language: string = 'fr'): Promise<SubsidySearchResponse> {
    try {
      return await apiService.get(`${API_BASE_URL}/keywords/${keyword}`, { language });
    } catch (error) {
      console.error(`Error getting subsidies for keyword ${keyword}:`, error);
      throw error;
    }
  }

  // Méthodes pour l'intégration avec les recommandations
  async getSubsidiesForRecommendation(recommendationId: string, language: string = 'fr'): Promise<SubsidyRecommendation[]> {
    try {
      return await apiService.get(`${API_BASE_URL}-integration/recommendations/${recommendationId}/subsidies`, { language });
    } catch (error) {
      console.error(`Error getting subsidies for recommendation ${recommendationId}:`, error);
      throw error;
    }
  }

  async getBestSubsidiesForRecommendation(
    recommendationId: string, 
    limit: number = 3, 
    minScore: number = 0.5, 
    language: string = 'fr'
  ): Promise<SubsidyRecommendation[]> {
    try {
      return await apiService.get(`${API_BASE_URL}-integration/recommendations/${recommendationId}/best-subsidies`, 
        { limit, min_score: minScore, language }
      );
    } catch (error) {
      console.error(`Error getting best subsidies for recommendation ${recommendationId}:`, error);
      throw error;
    }
  }

  async getSubsidiesForRecommendationSet(recommendationSetId: string, language: string = 'fr'): Promise<RecommendationSetSubsidies> {
    try {
      return await apiService.get(`${API_BASE_URL}-integration/recommendation-sets/${recommendationSetId}/subsidies`, 
        { language }
      );
    } catch (error) {
      console.error(`Error getting subsidies for recommendation set ${recommendationSetId}:`, error);
      throw error;
    }
  }

  // Méthodes pour l'intégration avec l'optimisation
  async getSubsidiesForOptimizationMeasure(measureId: string, language: string = 'fr'): Promise<SubsidyOptimizationRecommendation[]> {
    try {
      return await apiService.get(`${API_BASE_URL}-integration/optimization/measures/${measureId}/subsidies`, 
        { language }
      );
    } catch (error) {
      console.error(`Error getting subsidies for optimization measure ${measureId}:`, error);
      throw error;
    }
  }

  async getBestSubsidiesForOptimizationMeasure(
    measureId: string, 
    limit: number = 3, 
    minScore: number = 0.5, 
    language: string = 'fr'
  ): Promise<SubsidyOptimizationRecommendation[]> {
    try {
      return await apiService.get(`${API_BASE_URL}-integration/optimization/measures/${measureId}/best-subsidies`, 
        { limit, min_score: minScore, language }
      );
    } catch (error) {
      console.error(`Error getting best subsidies for optimization measure ${measureId}:`, error);
      throw error;
    }
  }

  async getSubsidiesForOptimizationProject(projectId: string, language: string = 'fr'): Promise<OptimizationProjectSubsidies> {
    try {
      return await apiService.get(`${API_BASE_URL}-integration/optimization/projects/${projectId}/subsidies`, 
        { language }
      );
    } catch (error) {
      console.error(`Error getting subsidies for optimization project ${projectId}:`, error);
      throw error;
    }
  }

  // Méthodes pour l'intégration avec le passeport vert
  async getSubsidiesForProperty(propertyId: string, userId?: string, language: string = 'fr'): Promise<PropertySubsidies> {
    try {
      return await apiService.get(`${API_BASE_URL}-green-passport/properties/${propertyId}/subsidies`, 
        { user_id: userId, language }
      );
    } catch (error) {
      console.error(`Error getting subsidies for property ${propertyId}:`, error);
      throw error;
    }
  }

  async getBestSubsidiesForProperty(
    propertyId: string, 
    userId?: string, 
    limit: number = 5, 
    minScore: number = 0.4, 
    language: string = 'fr'
  ): Promise<SubsidyPropertyRecommendation[]> {
    try {
      return await apiService.get(`${API_BASE_URL}-green-passport/properties/${propertyId}/best-subsidies`, 
        { user_id: userId, limit, min_score: minScore, language }
      );
    } catch (error) {
      console.error(`Error getting best subsidies for property ${propertyId}:`, error);
      throw error;
    }
  }

  // Méthodes liées aux applications de subventions
  
  /**
   * Soumet une demande de subvention
   * @param subsidyId ID de la subvention
   * @param applicationData Données de la demande
   * @returns Informations sur la demande soumise
   */
  async submitApplication(subsidyId: string, applicationData: any): Promise<any> {
    try {
      // Dans une implémentation réelle, nous utiliserions l'API
      // Pour l'instant, nous simulons l'appel API, mais la structure est prête pour une vraie API
      // return await apiService.post(`${API_BASE_URL}/${subsidyId}/applications`, applicationData);
      
      // Simulation pour la démonstration
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Générer un ID d'application fictif pour la démonstration
      const applicationId = 'APP-' + Math.random().toString(36).substring(2, 10).toUpperCase();
      
      return {
        id: applicationId,
        subsidyId,
        status: 'submitted',
        submissionDate: new Date().toISOString(),
        referenceNumber: `PRE-${new Date().getFullYear()}-${Math.floor(10000 + Math.random() * 90000)}`
      };
    } catch (error) {
      console.error('Erreur lors de la soumission de la demande:', error);
      throw new Error('Erreur lors de la soumission de la demande. Veuillez réessayer.');
    }
  }
  
  /**
   * Sauvegarde un brouillon de demande de subvention
   * @param subsidyId ID de la subvention
   * @param draftData Données du brouillon
   * @param draftId ID du brouillon existant (optionnel)
   * @returns Informations sur le brouillon sauvegardé
   */
  async saveDraft(subsidyId: string, draftData: any, draftId?: string): Promise<any> {
    try {
      // Dans une implémentation réelle, nous utiliserions l'API
      // Pour l'instant, nous simulons l'appel API, mais la structure est prête pour une vraie API
      // const endpoint = draftId 
      //   ? `${API_BASE_URL}/${subsidyId}/applications/drafts/${draftId}` 
      //   : `${API_BASE_URL}/${subsidyId}/applications/drafts`;
      // return await apiService.post(endpoint, draftData);
      
      // Simulation pour la démonstration
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Utiliser l'ID existant ou en générer un nouveau
      const newDraftId = draftId || 'DRAFT-' + Math.random().toString(36).substring(2, 10).toUpperCase();
      
      return {
        id: newDraftId,
        subsidyId,
        status: 'draft',
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du brouillon:', error);
      throw new Error('Erreur lors de la sauvegarde du brouillon. Veuillez réessayer.');
    }
  }
  
  /**
   * Récupère les détails d'une demande de subvention
   * @param applicationId ID de la demande
   * @returns Détails de la demande
   */
  async getApplicationById(applicationId: string): Promise<any> {
    try {
      // Dans une implémentation réelle, nous utiliserions l'API
      // Pour l'instant, nous simulons l'appel API, mais la structure est prête pour une vraie API
      // return await apiService.get(`${API_BASE_URL}/applications/${applicationId}`);
      
      // Simulation pour la démonstration
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Exemple de données (dans une implémentation réelle, elles viendraient de l'API)
      return {
        id: applicationId,
        subsidyId: "sub1",
        subsidyName: "Prime Énergie - Isolation Toiture",
        status: "processing",
        statusLabel: "En traitement",
        submissionDate: "2025-04-15",
        lastUpdated: "2025-05-01",
        referenceNumber: `PRE-2025-${Math.floor(10000 + Math.random() * 90000)}`,
        applicant: {
          name: "Jean Dupont",
          email: "jean.dupont@example.com",
          phone: "+32 470 12 34 56"
        },
        property: {
          address: "Rue de la Science 123, 1040 Bruxelles",
          type: "Maison unifamiliale"
        },
        project: {
          description: "Isolation de la toiture avec des matériaux écologiques",
          estimatedCost: 5000,
          estimatedCompletionDate: "2025-09-15"
        },
        subsidy: {
          maxAmount: 2000,
          percentage: 35,
          calculatedAmount: 1750
        },
        documents: [
          {
            id: "doc1",
            name: "Carte d'identité",
            status: "validated",
            uploadDate: "2025-04-15",
            validationDate: "2025-04-17"
          },
          {
            id: "doc2",
            name: "Preuve de domicile",
            status: "validated",
            uploadDate: "2025-04-15",
            validationDate: "2025-04-17"
          },
          {
            id: "doc3",
            name: "Devis de l'entrepreneur",
            status: "pending",
            uploadDate: "2025-04-15"
          },
          {
            id: "doc4",
            name: "Photos avant travaux",
            status: "requested",
            comments: "Veuillez fournir des photos de la toiture avant les travaux."
          }
        ],
        notes: [
          {
            id: "note1",
            date: "2025-04-17",
            author: "Service des Primes",
            authorType: "admin",
            content: "Votre demande a été reçue et est en cours de traitement. Nous avons validé votre carte d'identité et votre preuve de domicile."
          },
          {
            id: "note2",
            date: "2025-04-20",
            author: "Service des Primes",
            authorType: "admin",
            content: "Nous avons besoin de photos de votre toiture avant le début des travaux pour compléter votre dossier."
          },
          {
            id: "note3",
            date: "2025-04-21",
            author: "Jean Dupont",
            authorType: "user",
            content: "Je vais vous envoyer les photos demandées d'ici la fin de la semaine."
          }
        ],
        history: [
          {
            id: "hist1",
            date: "2025-04-15",
            status: "submitted",
            description: "Demande soumise"
          },
          {
            id: "hist2",
            date: "2025-04-17",
            status: "processing",
            description: "Demande en cours de traitement"
          },
          {
            id: "hist3",
            date: "2025-04-20",
            status: "additional_info",
            description: "Informations complémentaires demandées"
          }
        ],
        nextSteps: [
          "Fournir les photos avant travaux",
          "Attendre la validation technique du dossier",
          "Notification de la décision finale"
        ]
      };
    } catch (error) {
      console.error('Erreur lors de la récupération des détails de la demande:', error);
      throw new Error('Erreur lors de la récupération des détails de la demande. Veuillez réessayer.');
    }
  }
  
  /**
   * Ajoute une note à une demande de subvention
   * @param applicationId ID de la demande
   * @param noteContent Contenu de la note
   * @returns Informations sur la note ajoutée
   */
  async addApplicationNote(applicationId: string, noteContent: string): Promise<any> {
    try {
      // Dans une implémentation réelle, nous utiliserions l'API
      // Pour l'instant, nous simulons l'appel API, mais la structure est prête pour une vraie API
      // return await apiService.post(`${API_BASE_URL}/applications/${applicationId}/notes`, { content: noteContent });
      
      // Simulation pour la démonstration
      await new Promise(resolve => setTimeout(resolve, 800));
      
      return {
        id: 'note-' + Math.random().toString(36).substring(2, 10),
        date: new Date().toISOString(),
        author: "Jean Dupont", // Dans une implémentation réelle, ce serait l'utilisateur connecté
        authorType: "user",
        content: noteContent
      };
    } catch (error) {
      console.error('Erreur lors de l\'ajout de la note:', error);
      throw new Error('Erreur lors de l\'ajout de la note. Veuillez réessayer.');
    }
  }
  
  /**
   * Télécharge un document pour une demande de subvention
   * @param applicationId ID de la demande
   * @param documentId ID du document
   * @param file Fichier à télécharger
   * @returns Informations sur le document téléchargé
   */
  async uploadApplicationDocument(applicationId: string, documentId: string, file: File): Promise<any> {
    try {
      // Dans une implémentation réelle, nous utiliserions l'API
      // Pour l'instant, nous simulons l'appel API, mais la structure est prête pour une vraie API
      // return await apiService.uploadFile(
      //   `${API_BASE_URL}/applications/${applicationId}/documents/${documentId}`,
      //   file
      // );
      
      // Simulation pour la démonstration
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      return {
        id: documentId,
        name: file.name,
        status: "pending",
        uploadDate: new Date().toISOString(),
        size: file.size
      };
    } catch (error) {
      console.error('Erreur lors du téléchargement du document:', error);
      throw new Error('Erreur lors du téléchargement du document. Veuillez réessayer.');
    }
  }
}

// Exporter une instance singleton du service
export const subsidyService = new SubsidyService();
export default subsidyService;

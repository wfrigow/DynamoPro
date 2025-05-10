import apiService from './api';
import { API_CONFIG } from '../config';
import { 
  ApplicationBase, 
  ApplicationCreate, 
  ApplicationResponse, 
  ApplicationStatus, 
  ApplicationDocument, 
  ApplicationNote, 
  ApplicationHistory,
  DocumentStatus
} from '../types/api';

// Configuration de l'URL de base de l'API
const API_BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.APPLICATIONS_URL}`;

// Utilisation des types définis dans le fichier commun types/api.ts

// Types spécifiques au service d'application qui ne sont pas dans le fichier commun
export interface Applicant {
  name: string;
  email: string;
  phone: string;
  address: string;
  postalCode: string;
  city: string;
  userType: string;
}

export interface Property {
  address: string;
  postalCode: string;
  city: string;
  yearBuilt: number;
  type: string;
  size: number;
}

export interface Project {
  description: string;
  startDate: string;
  endDate: string;
  estimatedCost: number;
  contractor?: string;
}

export interface BankDetails {
  accountHolder: string;
  iban: string;
  bic: string;
}

export interface ApplicationRequest {
  subsidyId: string;
  applicant: Applicant;
  property: Property;
  project: Project;
  bankDetails: BankDetails;
}

export interface ApplicationDraftRequest {
  subsidyId: string;
  applicant?: Partial<Applicant>;
  property?: Partial<Property>;
  project?: Partial<Project>;
  bankDetails?: Partial<BankDetails>;
}

export interface ApplicationDraftResponse {
  id: string;
  subsidyId: string;
  status: string;
  lastUpdated: string;
  applicant: Partial<Applicant>;
  property: Partial<Property>;
  project: Partial<Project>;
  bankDetails: Partial<BankDetails>;
}

// Service pour interagir avec l'API d'applications de subventions
class ApplicationService {
  /**
   * Crée une nouvelle application de subvention
   * @param applicationData Données de l'application
   * @returns Informations sur l'application créée
   */
  async createApplication(applicationData: ApplicationRequest): Promise<ApplicationResponse> {
    try {
      return await apiService.post<ApplicationResponse>(`${API_BASE_URL}`, applicationData);
    } catch (error) {
      console.error('Error creating application:', error);
      throw error;
    }
  }
  
  /**
   * Crée ou met à jour un brouillon d'application
   * @param draftData Données du brouillon
   * @returns Informations sur le brouillon créé ou mis à jour
   */
  async saveDraft(draftData: ApplicationDraftRequest): Promise<ApplicationDraftResponse> {
    try {
      return await apiService.post<ApplicationDraftResponse>(`${API_BASE_URL}/drafts`, draftData);
    } catch (error) {
      console.error('Error saving draft:', error);
      throw error;
    }
  }
  
  /**
   * Met à jour un brouillon existant
   * @param draftId ID du brouillon
   * @param draftData Données du brouillon
   * @returns Informations sur le brouillon mis à jour
   */
  async updateDraft(draftId: string, draftData: ApplicationDraftRequest): Promise<ApplicationDraftResponse> {
    try {
      return await apiService.put<ApplicationDraftResponse>(`${API_BASE_URL}/drafts/${draftId}`, draftData);
    } catch (error) {
      console.error('Error updating draft:', error);
      throw error;
    }
  }
  
  /**
   * Récupère les détails d'une application
   * @param applicationId ID de l'application
   * @returns Détails de l'application
   */
  async getApplication(applicationId: string): Promise<ApplicationResponse> {
    try {
      return await apiService.get<ApplicationResponse>(`${API_BASE_URL}/${applicationId}`);
    } catch (error: any) {
      console.error('Error fetching application:', error);
      if (error.response && error.response.status === 404) {
        throw new Error(`La demande avec l'ID ${applicationId} n'a pas été trouvée.`);
      } else if (error.response && error.response.status === 401) {
        throw new Error('Vous n\'êtes pas autorisé à accéder à cette demande. Veuillez vous connecter.');
      } else if (error.response && error.response.status === 403) {
        throw new Error('Vous n\'avez pas les droits nécessaires pour accéder à cette demande.');
      } else if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors de la récupération de la demande.');
      }
    }
  }
  
  /**
   * Récupère les détails d'un brouillon
   * @param draftId ID du brouillon
   * @returns Détails du brouillon
   */
  async getDraft(draftId: string): Promise<ApplicationDraftResponse> {
    try {
      return await apiService.get<ApplicationDraftResponse>(`${API_BASE_URL}/drafts/${draftId}`);
    } catch (error) {
      console.error('Error fetching draft:', error);
      throw error;
    }
  }
  
  /**
   * Récupère les applications d'un utilisateur
   * @param userId ID de l'utilisateur
   * @param status Filtre par statut (optionnel)
   * @returns Liste des applications de l'utilisateur
   */
  async getUserApplications(userId: string, status?: ApplicationStatus): Promise<ApplicationResponse[]> {
    try {
      const params = status ? { status } : undefined;
      return await apiService.get<ApplicationResponse[]>(`${API_BASE_URL}/user/${userId}`, params);
    } catch (error: any) {
      console.error('Error fetching user applications:', error);
      if (error.response && error.response.status === 401) {
        throw new Error('Vous n\'êtes pas autorisé à accéder à ces demandes. Veuillez vous connecter.');
      } else if (error.response && error.response.status === 403) {
        throw new Error('Vous n\'avez pas les droits nécessaires pour accéder à ces demandes.');
      } else if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors de la récupération des demandes.');
      }
    }
  }
  
  /**
   * Récupère les brouillons d'un utilisateur
   * @param userId ID de l'utilisateur
   * @returns Liste des brouillons de l'utilisateur
   */
  async getUserDrafts(userId: string): Promise<ApplicationDraftResponse[]> {
    try {
      return await apiService.get<ApplicationDraftResponse[]>(`${API_BASE_URL}/user/${userId}/drafts`);
    } catch (error) {
      console.error('Error fetching user drafts:', error);
      throw error;
    }
  }
  
  /**
   * Ajoute une note à une application
   * @param applicationId ID de l'application
   * @param content Contenu de la note
   * @returns Informations sur la note ajoutée
   */
  async addNote(applicationId: string, content: string): Promise<ApplicationNote> {
    try {
      return await apiService.post<ApplicationNote>(`${API_BASE_URL}/${applicationId}/notes`, { content });
    } catch (error: any) {
      console.error('Error adding note:', error);
      if (error.response && error.response.status === 404) {
        throw new Error(`La demande avec l'ID ${applicationId} n'a pas été trouvée.`);
      } else if (error.response && error.response.status === 401) {
        throw new Error('Vous n\'êtes pas autorisé à ajouter une note à cette demande. Veuillez vous connecter.');
      } else if (error.response && error.response.status === 403) {
        throw new Error('Vous n\'avez pas les droits nécessaires pour ajouter une note à cette demande.');
      } else if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors de l\'ajout de la note.');
      }
    }
  }
  
  /**
   * Télécharge un document pour une application
   * @param applicationId ID de l'application
   * @param documentId ID du document
   * @param file Fichier à télécharger
   * @returns Informations sur le document téléchargé
   */
  async uploadDocument(applicationId: string, documentId: string, file: File): Promise<ApplicationDocument> {
    try {
      return await apiService.uploadFile<ApplicationDocument>(
        `${API_BASE_URL}/${applicationId}/documents/${documentId}`,
        file
      );
    } catch (error: any) {
      console.error('Error uploading document:', error);
      if (error.response && error.response.status === 404) {
        throw new Error(`La demande ou le document n'a pas été trouvé.`);
      } else if (error.response && error.response.status === 401) {
        throw new Error('Vous n\'êtes pas autorisé à télécharger un document pour cette demande. Veuillez vous connecter.');
      } else if (error.response && error.response.status === 403) {
        throw new Error('Vous n\'avez pas les droits nécessaires pour télécharger un document pour cette demande.');
      } else if (error.response && error.response.status === 413) {
        throw new Error('Le fichier est trop volumineux. Veuillez télécharger un fichier plus petit.');
      } else if (error.response && error.response.status === 415) {
        throw new Error('Le format du fichier n\'est pas pris en charge. Veuillez télécharger un fichier dans un format valide.');
      } else if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors du téléchargement du document.');
      }
    }
  }
  
  /**
   * Crée une nouvelle application de subvention avec simulation pour le développement
   * Cette méthode est utilisée temporairement pendant le développement
   * @param applicationData Données de l'application
   * @returns Informations sur l'application créée (simulées)
   */
  async createApplicationSimulated(applicationData: ApplicationCreate): Promise<ApplicationResponse> {
    try {
      // Simulation pour le développement
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        id: 'app-' + Math.random().toString(36).substring(2, 10),
        subsidy_id: applicationData.subsidy_id,
        user_id: 'user-123', // Dans une implémentation réelle, ce serait l'utilisateur connecté
        status: ApplicationStatus.SUBMITTED,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        subsidy: {
          id: applicationData.subsidy_id,
          name: 'Prime Rénovation Énergétique',
          provider: 'Service Public de Wallonie',
          max_amount: 5000,
          percentage: 30
        },
        documents: [
          {
            id: 'doc-1',
            document_id: 'doc-type-1',
            name: 'Preuve de propriété',
            status: DocumentStatus.PENDING,
            uploaded_at: null,
            file_url: null
          },
          {
            id: 'doc-2',
            document_id: 'doc-type-2',
            name: 'Devis de l\'entrepreneur',
            status: DocumentStatus.PENDING,
            uploaded_at: null,
            file_url: null
          }
        ],
        notes: [],
        history: [
          {
            id: 'hist-1',
            date: new Date().toISOString(),
            status: ApplicationStatus.SUBMITTED,
            description: 'Demande soumise'
          }
        ],
        nextSteps: [
          'Télécharger les documents requis',
          'Attendre la validation de votre dossier',
          'Vous serez notifié par email des prochaines étapes'
        ]
      };
    } catch (error: any) {
      console.error('Error creating application (simulated):', error);
      throw new Error('Une erreur est survenue lors de la création de la demande.');
    }
  }
}

// Exporter une instance singleton du service
export const applicationService = new ApplicationService();
export default applicationService;

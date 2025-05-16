import axios, { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { store } from '../store';
import { logout } from '../store/slices/authSlice';
import { API_CONFIG } from '../config/api';

// Configuration de base
const API_URL = API_CONFIG.baseUrl;

// Log pour le débogage
console.log(`Service API utilisant l'URL de base: ${API_URL}`);

// Création d'une instance axios avec une configuration de base
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification à chaque requête
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const state = store.getState();
    const token = state.auth.token;
    
    if (token && config.headers) {
      // Ajouter le token d'authentification aux headers
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les réponses et les erreurs
api.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response;
  },
  (error: AxiosError) => {
    // Gérer les erreurs d'authentification (401)
    if (error.response && error.response.status === 401) {
      // Déconnecter l'utilisateur si le token est invalide ou expiré
      store.dispatch(logout());
      // Rediriger vers la page de connexion
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// Fonctions d'API génériques
export const apiService = {
  /**
   * Effectue une requête GET
   * @param url URL de la requête
   * @param params Paramètres de la requête ou options de configuration
   * @returns Promesse avec les données de la réponse
   */
  get: async <T>(url: string, params?: any): Promise<T> => {
    try {
      const config = params && params.headers ? params : { params };
      const response = await api.get<T>(url, config);
      return response.data;
    } catch (error) {
      console.error(`GET request to ${url} failed:`, error);
      throw error;
    }
  },
  
  /**
   * Effectue une requête POST
   * @param url URL de la requête
   * @param data Données à envoyer
   * @param config Options de configuration supplémentaires
   * @returns Promesse avec les données de la réponse
   */
  post: async <T>(url: string, data: any, config?: any): Promise<T> => {
    try {
      const response = await api.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`POST request to ${url} failed:`, error);
      throw error;
    }
  },
  
  /**
   * Effectue une requête PUT
   * @param url URL de la requête
   * @param data Données à envoyer
   * @param config Options de configuration supplémentaires
   * @returns Promesse avec les données de la réponse
   */
  put: async <T>(url: string, data: any, config?: any): Promise<T> => {
    try {
      const response = await api.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`PUT request to ${url} failed:`, error);
      throw error;
    }
  },
  
  /**
   * Effectue une requête DELETE
   * @param url URL de la requête
   * @param config Options de configuration supplémentaires
   * @returns Promesse avec les données de la réponse
   */
  delete: async <T>(url: string, config?: any): Promise<T> => {
    try {
      const response = await api.delete<T>(url, config);
      return response.data;
    } catch (error) {
      console.error(`DELETE request to ${url} failed:`, error);
      throw error;
    }
  },
  
  /**
   * Effectue une requête POST avec upload de fichier
   * @param url URL de la requête
   * @param file Fichier à uploader
   * @param additionalData Données additionnelles à envoyer
   * @returns Promesse avec les données de la réponse
   */
  uploadFile: async <T>(url: string, file: File, additionalData?: any): Promise<T> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Ajouter des données supplémentaires si nécessaire
      if (additionalData) {
        Object.keys(additionalData).forEach(key => {
          formData.append(key, additionalData[key]);
        });
      }
      
      const response = await api.post<T>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error(`File upload to ${url} failed:`, error);
      throw error;
    }
  }
};

export default apiService;

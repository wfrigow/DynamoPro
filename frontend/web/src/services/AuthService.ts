import apiService from './api';
import { API_CONFIG, AUTH_CONFIG } from '../config';
import { LoginRequest, RegisterRequest, TokenResponse, UserResponse } from '../types/api';

// Configuration de l'URL de base de l'API d'authentification
const AUTH_API_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.AUTH_URL}`;

// Service pour interagir avec l'API d'authentification
class AuthService {
  /**
   * Connecte un utilisateur
   * @param credentials Identifiants de l'utilisateur
   * @returns Token d'accès et informations sur l'utilisateur
   */
  async login(credentials: LoginRequest): Promise<{ token: string; user: UserResponse }> {
    try {
      // Convertir les identifiants en format form-urlencoded pour l'API FastAPI
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      // Appel à l'API
      const tokenResponse = await apiService.post<TokenResponse>(
        `${AUTH_API_URL}/token`, 
        formData.toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );
      
      // Stocker le token dans le localStorage
      localStorage.setItem(AUTH_CONFIG.TOKEN_STORAGE_KEY, tokenResponse.access_token);
      
      // Récupérer les informations de l'utilisateur
      const userResponse = await this.getCurrentUser(tokenResponse.access_token);
      
      return {
        token: tokenResponse.access_token,
        user: userResponse
      };
    } catch (error: any) {
      console.error('Error during login:', error);
      if (error.response && error.response.status === 401) {
        throw new Error('Identifiants invalides. Veuillez vérifier votre nom d\'utilisateur et votre mot de passe.');
      } else if (error.response && error.response.status === 403) {
        throw new Error('Votre compte n\'est pas actif. Veuillez contacter l\'administrateur.');
      } else if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors de la connexion. Veuillez réessayer.');
      }
    }
  }
  
  /**
   * Inscrit un nouvel utilisateur
   * @param userData Données de l'utilisateur
   * @returns Informations sur l'utilisateur créé
   */
  async register(userData: RegisterRequest): Promise<UserResponse> {
    try {
      const response = await apiService.post<UserResponse>(`${AUTH_API_URL}/register`, userData);
      return response;
    } catch (error: any) {
      console.error('Error during registration:', error);
      if (error.response && error.response.status === 400) {
        if (error.response.data && error.response.data.detail) {
          throw new Error(error.response.data.detail);
        } else {
          throw new Error('Les données d\'inscription sont invalides. Veuillez vérifier les informations fournies.');
        }
      } else if (error.response && error.response.status === 409) {
        throw new Error('Un utilisateur avec cette adresse e-mail existe déjà.');
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.');
      }
    }
  }
  
  /**
   * Récupère les informations de l'utilisateur actuellement connecté
   * @param token Token d'authentification (optionnel)
   * @returns Informations sur l'utilisateur
   */
  async getCurrentUser(token?: string): Promise<UserResponse> {
    try {
      // Si un token est fourni, l'utiliser pour cette requête uniquement
      const config = token ? {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      } : undefined;
      
      return await apiService.get<UserResponse>(`${AUTH_API_URL}/me`, config);
    } catch (error: any) {
      console.error('Error fetching current user:', error);
      if (error.response && error.response.status === 401) {
        // Supprimer le token du localStorage si la session est expirée
        localStorage.removeItem(AUTH_CONFIG.TOKEN_STORAGE_KEY);
        throw new Error('Votre session a expiré. Veuillez vous reconnecter.');
      } else if (error.response && error.response.status === 404) {
        throw new Error('Utilisateur non trouvé.');
      } else if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Une erreur est survenue lors de la récupération des informations utilisateur.');
      }
    }
  }
  
  /**
   * Déconnecte l'utilisateur en supprimant le token du localStorage
   */
  logout(): void {
    localStorage.removeItem(AUTH_CONFIG.TOKEN_STORAGE_KEY);
  }
  
  /**
   * Vérifie si l'utilisateur est connecté
   * @returns true si l'utilisateur est connecté, false sinon
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem(AUTH_CONFIG.TOKEN_STORAGE_KEY);
  }
  
  /**
   * Récupère le token d'authentification
   * @returns Le token d'authentification ou null si l'utilisateur n'est pas connecté
   */
  getToken(): string | null {
    return localStorage.getItem(AUTH_CONFIG.TOKEN_STORAGE_KEY);
  }
}

// Exporter une instance singleton du service
export const authService = new AuthService();
export default authService;

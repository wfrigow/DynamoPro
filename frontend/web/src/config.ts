/**
 * Configuration globale de l'application
 */

// URLs des APIs
export const API_CONFIG = {
  // URL de base de l'API
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8010/api',
  
  // URLs spécifiques
  AUTH_URL: '/auth',
  SUBSIDIES_URL: '/subsidies',
  APPLICATIONS_URL: '/subsidies/applications',
  RECOMMENDATIONS_URL: '/recommendations',
  OPTIMIZATION_URL: '/optimization',
  GREEN_PASSPORT_URL: '/green-passport'
};

// Configuration de l'authentification
export const AUTH_CONFIG = {
  // Durée de validité du token en minutes
  TOKEN_EXPIRY: 60,
  
  // Clé de stockage du token dans le localStorage
  TOKEN_STORAGE_KEY: 'dynamo_pro_token'
};

// Configuration de l'interface utilisateur
export const UI_CONFIG = {
  // Nombre d'éléments par page pour la pagination
  ITEMS_PER_PAGE: 10,
  
  // Délai d'affichage des notifications en millisecondes
  NOTIFICATION_DURATION: 5000
};

// Configuration des langues
export const LANGUAGE_CONFIG = {
  // Langue par défaut
  DEFAULT_LANGUAGE: 'fr',
  
  // Langues disponibles
  AVAILABLE_LANGUAGES: ['fr', 'nl', 'en']
};

export default {
  API: API_CONFIG,
  AUTH: AUTH_CONFIG,
  UI: UI_CONFIG,
  LANGUAGE: LANGUAGE_CONFIG
};

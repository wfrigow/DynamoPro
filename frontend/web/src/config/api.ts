/**
 * Configuration des URLs d'API selon l'environnement
 */

// Détermine l'URL de base de l'API en fonction de l'environnement
const getApiBaseUrl = (): string => {
  // En production (Netlify), nous utilisons l'URL Heroku
  if (window.location.hostname !== 'localhost') {
    return 'https://nom-de-votre-app-dynamopro.herokuapp.com';
  }
  
  // En développement local, nous utilisons localhost
  return 'http://localhost:8003';
};

// Configuration exportée
export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  endpoints: {
    auth: {
      login: '/api/auth/login',
      register: '/api/auth/register',
      currentUser: '/api/auth/me',
    },
    recommendations: {
      simple: '/api/v1/simple-recommendations',
      detailed: '/api/v1/detailed-recommendations',
    },
    // Autres endpoints...
  }
};

// Pour faciliter le débogage
console.log(`API configurée pour : ${API_CONFIG.baseUrl}`);

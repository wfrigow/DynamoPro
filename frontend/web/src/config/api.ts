/**
 * Configuration des URLs d'API selon l'environnement
 */

// Détermine l'URL de base de l'API en fonction de l'environnement
const getApiBaseUrl = (): string => {
  // En production (Netlify), nous utilisons l'URL Heroku
  if (window.location.hostname !== 'localhost') {
    // Déterminer l'URL backend en fonction du déploiement
    if (window.location.hostname.includes('windsurf.build')) {
      // Pour les déploiements sur windsurf.build, utiliser la même origine
      // Cela évite les problèmes CORS car le backend et le frontend sont hébergés au même endroit
      return window.location.origin;
    }
    // URL du backend Heroku
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
    llm: {
      proxy: '/api/llm', // Endpoint pour le proxy OpenAI
    },
    // Autres endpoints...
  }
};

// Pour faciliter le débogage
console.log(`API configurée pour : ${API_CONFIG.baseUrl}`);

// Exposer l'URL de base de l'API globalement pour faciliter le débogage
// Cette variable est utilisée par le gestionnaire d'erreurs dans index.tsx
if (typeof window !== 'undefined') {
  window.apiBaseUrl = API_CONFIG.baseUrl;
}

// URL complète du proxy LLM (utilisée par direct-openai.ts)
export const getLlmProxyUrl = (): string => {
  return `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.llm.proxy}`;
};

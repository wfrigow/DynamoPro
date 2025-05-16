/**
 * Configuration des URLs d'API selon l'environnement
 */

// Détermine l'URL de base de l'API en fonction de l'environnement
const getApiBaseUrl = (): string => {
  // En production (que ce soit sur Netlify, windsurf.build ou ailleurs), nous utilisons toujours l'URL Heroku
  if (window.location.hostname !== 'localhost') {
    // IMPORTANT : Ne jamais utiliser l'origine actuelle comme URL API pour windsurf.build
    // car le backend est hébergé sur Heroku, pas sur windsurf.build
    console.log('Utilisation de l\'URL Heroku pour les appels API');
    return 'https://nom-de-votre-app-dynamopro-b0d7b735d20c.herokuapp.com';
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

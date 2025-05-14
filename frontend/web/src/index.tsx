import React from 'react';
import ReactDOM from 'react-dom/client';

// Élément DOM racine pour le rendu
const rootElement = document.getElementById('root') as HTMLElement;

// Fonction pour afficher un message d'erreur dans le DOM
const renderErrorMessage = (error: Error) => {
  rootElement.innerHTML = `
    <div style="padding: 20px; font-family: sans-serif;">
      <h2 style="color: #d32f2f;">Une erreur s'est produite lors de l'initialisation</h2>
      <p><strong>Type:</strong> ${error.name}</p>
      <p><strong>Message:</strong> ${error.message}</p>
      <p><strong>Où:</strong> Pendant le chargement de l'application</p>
      <p>Veuillez rafraîchir la page ou contacter l'assistance si le problème persiste.</p>
    </div>
  `;
  console.error('Erreur d\'initialisation :', error);
};

// Fonction pour initialiser l'application par étapes, avec gestion d'erreurs à chaque étape
// Gestionnaire d'erreurs pour les ressources 404
const setupResourceErrorHandler = () => {
  // Écoute les erreurs de chargement de ressources
  window.addEventListener('error', (event) => {
    if (event.target && (event.target as HTMLElement).tagName) {
      const element = event.target as HTMLElement;
      const tagName = element.tagName.toLowerCase();
      
      // Si l'erreur concerne une image, un script, une feuille de style, etc.
      if (['img', 'script', 'link', 'audio', 'video'].includes(tagName)) {
        let url = '';
        
        // Récupérer l'URL de la ressource selon le type d'élément
        if (tagName === 'img' || tagName === 'script' || tagName === 'audio' || tagName === 'video') {
          url = (element as HTMLImageElement | HTMLScriptElement | HTMLAudioElement | HTMLVideoElement).src || '';
        } else if (tagName === 'link') {
          url = (element as HTMLLinkElement).href || '';
        }
        
        console.error(`Erreur de ressource (404): ${url}`);
        
        // Enregistrer les détails pour aider au débogage
        const details = {
          type: tagName,
          url,
          hostname: window.location.hostname,
          apiBaseUrl: window.apiBaseUrl, // Défini par notre code de configuration API
          time: new Date().toISOString(),
          referrer: document.referrer
        };
        
        console.log('Détails de l\'erreur:', details);
      }
    }
  }, true);
};

// Définir variable globale pour la configuration API
declare global {
  interface Window {
    apiBaseUrl?: string;
  }
}

const initializeApp = async () => {
  try {
    // Configurer le gestionnaire d'erreurs de ressources
    setupResourceErrorHandler();
    console.log('1. Démarrage de l\'initialisation');
    
    // Étape 1 : Importer le thème (moins susceptible de causer des erreurs)
    console.log('2. Chargement du thème...');
    const themeModule = await import('./theme');
    const theme = themeModule.default;
    console.log('3. Thème chargé avec succès');
    
    // Étape 2 : Importer le store Redux
    console.log('4. Chargement du store Redux...');
    const storeModule = await import('./store');
    const { store } = storeModule;
    console.log('5. Store Redux chargé avec succès');
    
    // Étape 3 : Importer les composants React
    console.log('6. Chargement des composants React principaux...');
    const { Provider } = await import('react-redux');
    const { BrowserRouter } = await import('react-router-dom');
    const { ThemeProvider } = await import('@mui/material/styles');
    const CssBaseline = (await import('@mui/material/CssBaseline')).default;
    console.log('7. Composants React chargés avec succès');
    
    // Étape 4 : Importer le composant App (le plus susceptible de causer l'erreur)
    console.log('8. Chargement du composant App...');
    const AppModule = await import('./App');
    const App = AppModule.default;
    console.log('9. Composant App chargé avec succès');
    
    // Étape 5 : Créer et rendre l'application
    console.log('10. Création du root React...');
    const root = ReactDOM.createRoot(rootElement);
    
    console.log('11. Rendu de l\'application...');
    root.render(
      <React.StrictMode>
        <Provider store={store}>
          <BrowserRouter>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <App />
            </ThemeProvider>
          </BrowserRouter>
        </Provider>
      </React.StrictMode>
    );
    console.log('12. Application rendue avec succès');
    
  } catch (error) {
    console.error('Erreur lors de l\'initialisation :', error);
    renderErrorMessage(error as Error);
  }
};

// Démarrer l'initialisation
initializeApp();

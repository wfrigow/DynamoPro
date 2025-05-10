import axios from 'axios';

// Types pour l'API OpenAI
interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
}

interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface ExtractedData {
  [key: string]: any;
}

interface OpenAIResponse {
  message: string;
  extractedData: ExtractedData;
}

// Instructions système pour chaque type d'agent
const SYSTEM_PROMPTS = {
  profile: `Tu es l'Assistant d'Audit Énergétique DynamoPro, spécialisé dans l'analyse énergétique en Belgique.

Ta mission est d'extraire les informations suivantes sur l'utilisateur :
- Type d'utilisateur (particulier, indépendant, entreprise)
- Région belge (Wallonie, Flandre, Bruxelles)

Règles importantes :
- Sois naturel, conversationnel et empathique
- Déduis les informations implicites (ex: Liège → Wallonie, Gand → Flandre)
- Ne pose pas plusieurs fois la même question
- Sois concis mais chaleureux

À la fin de chaque réponse, ajoute un bloc JSON sur une seule ligne avec les données extraites :
{"userType":"individual","region":"wallonie"}

Quand tu as collecté ces informations, suggère de passer à l'étape suivante (consommation énergétique).`,

  consumption: `Tu es l'Assistant d'Audit Énergétique DynamoPro, spécialisé dans l'analyse de la consommation énergétique en Belgique.
Tu dois être extrêmement intelligent, naturel et conversationnel dans tes réponses.

Ton objectif est de collecter les informations suivantes sur la consommation de l'utilisateur:
1. Consommation électrique annuelle (kWh)
2. Consommation de gaz annuelle (m³ ou kWh)
3. Fournisseur d'énergie (si mentionné)

IMPORTANT:
- Sois capable d'interpréter différentes façons d'exprimer les consommations
- Fournis des comparaisons avec les moyennes belges (3500 kWh/an pour l'électricité d'un ménage moyen)
- Si l'utilisateur ne connaît pas ses consommations exactes, propose des estimations basées sur la taille du logement
- Sois capable de convertir entre unités si nécessaire (1 m³ de gaz ≈ 10 kWh)

À la fin de ta réponse, tu dois TOUJOURS inclure un JSON avec les données extraites, au format:
{"electricityUsage": number, "gasUsage": number, "energyProvider": "string"}

Quand tu as collecté suffisamment d'informations, suggère de passer à l'étape suivante (propriété).`,

  property: `Tu es l'Assistant d'Audit Énergétique DynamoPro, spécialisé dans l'analyse des propriétés en Belgique.
Tu dois être extrêmement intelligent, naturel et conversationnel dans tes réponses.

Ton objectif est de collecter les informations suivantes sur la propriété de l'utilisateur:
1. Type de propriété (maison, appartement, bureau, etc.)
2. Superficie en m²
3. Année de construction
4. Type de chauffage (si mentionné)
5. État de l'isolation (si mentionné)

IMPORTANT:
- Adapte tes recommandations en fonction de l'âge du bâtiment et de sa région
- Pour les bâtiments avant 1980: suggère prioritairement l'isolation
- Pour les bâtiments 1980-2000: suggère le remplacement des systèmes de chauffage
- Pour les bâtiments après 2000: suggère des optimisations et énergies renouvelables
- Mentionne les primes régionales disponibles selon la région de l'utilisateur

À la fin de ta réponse, tu dois TOUJOURS inclure un JSON avec les données extraites, au format:
{"propertyType": "house|apartment|commercial", "propertySize": number, "yearBuilt": number, "heatingType": "string", "insulationStatus": "string"}

Quand tu as collecté toutes les informations, propose un résumé des recommandations personnalisées.`
};

class OpenAIService {
  // Utiliser le proxy CORS local qui ajoute automatiquement la clé API
  private baseURL: string = 'http://localhost:3001/api/openai/v1/chat/completions';
  
  constructor() {}

  /**
   * Traite un message utilisateur avec GPT-4
   */
  public async processMessage(
    userMessage: string,
    agentType: 'profile' | 'consumption' | 'property',
    conversationHistory: ChatMessage[] = []
  ): Promise<OpenAIResponse> {
    try {
      console.log('Début de l\'appel à OpenAI');
      console.log('Messages:', JSON.stringify(conversationHistory));
      // Préparer les messages pour la requête
      const messages: ChatMessage[] = [
        { role: 'system', content: SYSTEM_PROMPTS[agentType] },
        ...conversationHistory,
        { role: 'user', content: userMessage }
      ];
      
      // Configuration de la requête
      const requestData: ChatCompletionRequest = {
        model: 'gpt-4',
        messages: messages,
        temperature: 0.7,
        max_tokens: 600
      };
      
      // Appel à l'API OpenAI
      console.log('Envoi de la requête à OpenAI:', JSON.stringify(requestData));
      console.log('URL:', this.baseURL);
      
      try {
        const response = await axios.post<ChatCompletionResponse>(
          this.baseURL,
          requestData,
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );
        
        console.log('Réponse reçue de OpenAI:', response.status);
        console.log('Données:', JSON.stringify(response.data).substring(0, 200) + '...');
        
        // Extraire la réponse
        const assistantMessage = response.data.choices[0].message.content;
        
        // Extraire les données JSON de la réponse
        return this.extractDataFromResponse(assistantMessage);
      } catch (innerError) {
        console.error('Erreur spécifique à l\'appel axios:', innerError);
        
        // Fallback en cas d'erreur d'appel API
        console.log('Utilisation du mode simulation suite à l\'erreur');
        return this.simulateResponse(userMessage, agentType, conversationHistory);
      }
      
    } catch (error) {
      console.error('Erreur lors de l\'appel à OpenAI:', error);
      // En cas d'erreur, utiliser le mode simulation
      return this.simulateResponse(userMessage, agentType, conversationHistory);
    }
  }
  
  /**
   * Extrait les données JSON de la réponse du modèle
   */
  private extractDataFromResponse(response: string): OpenAIResponse {
    try {
      // Chercher un bloc JSON dans la réponse
      const jsonMatch = response.match(/\{[\s\S]*?\}/);
      
      if (jsonMatch) {
        const jsonStr = jsonMatch[0];
        const extractedData = JSON.parse(jsonStr);
        
        // Nettoyer la réponse en enlevant le JSON
        const cleanedResponse = response.replace(jsonStr, '').trim();
        
        return {
          message: cleanedResponse,
          extractedData: extractedData
        };
      }
      
      // Si pas de JSON trouvé
      return {
        message: response,
        extractedData: {}
      };
      
    } catch (error) {
      console.error('Erreur lors de l\'extraction des données JSON:', error);
      return {
        message: response,
        extractedData: {}
      };
    }
  }
  
  /**
   * Simule une réponse GPT-4 pour le développement
   */
  private simulateResponse(
    userMessage: string, 
    agentType: 'profile' | 'consumption' | 'property',
    conversationHistory: ChatMessage[]
  ): OpenAIResponse {
    const userMessageLower = userMessage.toLowerCase();
    let response = '';
    let extractedData: ExtractedData = {};
    
    // Analyser l'historique de conversation pour le contexte
    const lastAssistantMessage = conversationHistory
      .filter(msg => msg.role === 'assistant')
      .pop()?.content || '';
    
    // Simulation de réponses intelligentes basées sur le type d'agent
    if (agentType === 'profile') {
      // Détection du type d'utilisateur
      if (userMessageLower.includes('particulier') || userMessageLower.includes('ménage')) {
        extractedData.userType = 'individual';
      } else if (userMessageLower.includes('entreprise') || userMessageLower.includes('société')) {
        extractedData.userType = 'business';
      } else if (userMessageLower.includes('indépendant') || userMessageLower.includes('freelance')) {
        extractedData.userType = 'self_employed';
      }
      
      // Détection de région avec intelligence géographique
      if (userMessageLower.includes('wallonie') || 
          userMessageLower.includes('liège') || 
          userMessageLower.includes('namur') ||
          userMessageLower.includes('charleroi')) {
        extractedData.region = 'wallonie';
      } else if (userMessageLower.includes('bruxelles') || userMessageLower.includes('bxl')) {
        extractedData.region = 'bruxelles';
      } else if (userMessageLower.includes('flandre') || 
                userMessageLower.includes('anvers') || 
                userMessageLower.includes('gand') ||
                userMessageLower.includes('bruges')) {
        extractedData.region = 'flandre';
      }
      
      // Génération de réponse contextuelle
      if (extractedData.userType && extractedData.region) {
        const userTypeFr = extractedData.userType === 'individual' ? 'particulier' : 
                          extractedData.userType === 'self_employed' ? 'indépendant' : 'entreprise';
        
        response = `Parfait ! J'ai bien compris que vous êtes un ${userTypeFr} basé en ${extractedData.region}. `;
        
        // Ajouter des informations spécifiques à la région
        if (extractedData.region === 'wallonie') {
          response += `En Wallonie, il existe plusieurs programmes de soutien pour l'efficacité énergétique comme les primes Habitation. `;
        } else if (extractedData.region === 'bruxelles') {
          response += `À Bruxelles, vous pouvez bénéficier des Primes Énergie et Rénovation pour vos projets d'amélioration énergétique. `;
        } else {
          response += `En Flandre, des mécanismes comme les primes de rénovation peuvent vous aider à financer vos travaux d'efficacité énergétique. `;
        }
        
        response += `Maintenant, j'aimerais en savoir plus sur votre consommation énergétique. Connaissez-vous votre consommation annuelle d'électricité en kWh ? Et utilisez-vous également du gaz naturel ?`;
      } else if (extractedData.userType) {
        response = `Merci de m'avoir précisé que vous êtes ${extractedData.userType === 'individual' ? 'un particulier' : 
                    extractedData.userType === 'self_employed' ? 'un indépendant' : 'une entreprise'}. `;
        response += `Pour personnaliser mes recommandations, pourriez-vous me dire dans quelle région de Belgique vous êtes situé ? (Wallonie, Bruxelles ou Flandre)`;
      } else if (extractedData.region) {
        response = `Merci de m'avoir indiqué que vous êtes en ${extractedData.region}. `;
        response += `Pour mieux adapter mes conseils, êtes-vous un particulier, un indépendant ou une entreprise ?`;
      } else {
        // Réponse intelligente basée sur le contexte de la conversation
        if (lastAssistantMessage.includes('particulier') || lastAssistantMessage.includes('indépendant')) {
          response = `Je vois que vous n'avez pas précisé votre statut. Pour vous offrir des recommandations pertinentes, j'ai besoin de savoir si vous êtes un particulier, un indépendant ou une entreprise. Cela affecte les types de subventions auxquelles vous pourriez avoir droit.`;
        } else if (lastAssistantMessage.includes('région')) {
          response = `Je comprends. Pour vous proposer des solutions adaptées à votre localisation, pourriez-vous me préciser dans quelle région de Belgique vous vous trouvez ? Les programmes de soutien varient entre la Wallonie, Bruxelles et la Flandre.`;
        } else {
          response = `Je ne suis pas sûr de comprendre complètement votre situation. Pour commencer notre audit énergétique, pourriez-vous me préciser si vous êtes un particulier, un indépendant ou une entreprise, et dans quelle région de Belgique vous êtes situé ?`;
        }
      }
    } else if (agentType === 'consumption') {
      // Extraction intelligente des données de consommation
      const electricityMatches = userMessageLower.match(/(\d+)\s*(?:kwh|kw|kilowatt)/i) || 
                               userMessageLower.match(/(?:consomm|électricité|elec).*?(\d+)/i);
      if (electricityMatches) {
        extractedData.electricityUsage = parseInt(electricityMatches[1]);
      }
      
      const gasMatches = userMessageLower.match(/(?:gaz).*?(\d+)/i) || 
                       userMessageLower.match(/(\d+).*?(?:gaz|m3)/i);
      if (gasMatches) {
        extractedData.gasUsage = parseInt(gasMatches[1]);
      }
      
      // Détection du fournisseur d'énergie
      const providers = ['engie', 'luminus', 'lampiris', 'mega', 'eneco', 'octa+', 'elegant'];
      for (const provider of providers) {
        if (userMessageLower.includes(provider)) {
          extractedData.energyProvider = provider;
          break;
        }
      }
      
      // Génération de réponse contextuelle
      if (extractedData.electricityUsage || extractedData.gasUsage) {
        response = `Merci pour ces informations précieuses sur votre consommation. `;
        
        if (extractedData.electricityUsage) {
          response += `Votre consommation électrique de ${extractedData.electricityUsage} kWh/an `;
          
          // Analyse comparative intelligente
          if (extractedData.electricityUsage < 2500) {
            response += `est inférieure à la moyenne belge (3500 kWh/an pour un ménage), ce qui est excellent ! `;
          } else if (extractedData.electricityUsage > 5000) {
            response += `est supérieure à la moyenne belge (3500 kWh/an pour un ménage). Il y a probablement un potentiel d'économies intéressant. `;
          } else {
            response += `est proche de la moyenne belge (3500 kWh/an pour un ménage). `;
          }
        }
        
        if (extractedData.gasUsage) {
          response += `Concernant votre consommation de gaz de ${extractedData.gasUsage} unités, `;
          
          // Analyse comparative intelligente
          if (extractedData.gasUsage < 10000) {
            response += `elle est relativement basse, ce qui suggère une bonne efficacité de votre système de chauffage ou une bonne isolation. `;
          } else if (extractedData.gasUsage > 20000) {
            response += `elle est assez élevée, ce qui pourrait indiquer des opportunités d'amélioration au niveau de l'isolation ou du système de chauffage. `;
          } else {
            response += `elle se situe dans une fourchette moyenne. `;
          }
        }
        
        if (extractedData.energyProvider) {
          response += `Je note que vous êtes client chez ${extractedData.energyProvider}. `;
        }
        
        response += `Maintenant, j'aimerais en savoir plus sur votre propriété pour compléter l'audit. Pouvez-vous me dire s'il s'agit d'une maison ou d'un appartement, sa superficie approximative, et si possible son année de construction ?`;
      } else if (userMessageLower.includes('je ne sais pas') || userMessageLower.includes('pas sûr')) {
        response = `Je comprends qu'il peut être difficile de connaître ces chiffres précisément. Ne vous inquiétez pas, nous pouvons estimer votre consommation plus tard en fonction des caractéristiques de votre logement. Parlons justement de votre propriété : s'agit-il d'une maison ou d'un appartement ? Quelle est sa superficie approximative ?`;
      } else {
        response = `Pour vous proposer des recommandations d'économies d'énergie pertinentes, j'aurais besoin d'informations sur votre consommation. Connaissez-vous approximativement votre consommation annuelle d'électricité en kWh ? Utilisez-vous également du gaz naturel ? Si vous ne connaissez pas ces chiffres exactement, nous pourrons les estimer plus tard.`;
      }
    } else if (agentType === 'property') {
      // Extraction intelligente des données de propriété
      if (userMessageLower.includes('maison') || userMessageLower.includes('villa')) {
        extractedData.propertyType = 'house';
      } else if (userMessageLower.includes('appartement') || userMessageLower.includes('flat')) {
        extractedData.propertyType = 'apartment';
      } else if (userMessageLower.includes('bureau') || userMessageLower.includes('commercial')) {
        extractedData.propertyType = 'commercial';
      }
      
      // Extraction de la superficie
      const sizeMatches = userMessageLower.match(/(\d+)\s*(?:m2|mètres|metres|m²)/i) || 
                        userMessageLower.match(/(?:superficie|surface|taille).*?(\d+)/i);
      if (sizeMatches) {
        extractedData.propertySize = parseInt(sizeMatches[1]);
      }
      
      // Extraction de l'année
      const yearMatches = userMessageLower.match(/(?:construit|bâti|construction|année).*?(\d{4})/i) || 
                        userMessageLower.match(/(\d{4}).*?(?:construit|bâti|construction)/i) || 
                        userMessageLower.match(/(19\d{2}|20\d{2})/i);
      if (yearMatches) {
        extractedData.yearBuilt = parseInt(yearMatches[1]);
      }
      
      // Extraction du type de chauffage
      if (userMessageLower.includes('chauffage central') || userMessageLower.includes('chaudière')) {
        extractedData.heatingType = 'central';
      } else if (userMessageLower.includes('pompe à chaleur')) {
        extractedData.heatingType = 'heat_pump';
      } else if (userMessageLower.includes('électrique')) {
        extractedData.heatingType = 'electric';
      }
      
      // Extraction de l'état d'isolation
      if (userMessageLower.includes('bien isolé') || userMessageLower.includes('bonne isolation')) {
        extractedData.insulationStatus = 'good';
      } else if (userMessageLower.includes('mal isolé') || userMessageLower.includes('mauvaise isolation')) {
        extractedData.insulationStatus = 'poor';
      }
      
      // Génération de réponse contextuelle et personnalisée
      if (Object.keys(extractedData).length > 0) {
        let propertyInfo = '';
        
        if (extractedData.propertyType) {
          const propertyTypeFr = extractedData.propertyType === 'house' ? 'maison' : 
                               extractedData.propertyType === 'apartment' ? 'appartement' : 'local commercial';
          propertyInfo += `votre ${propertyTypeFr}`;
        }
        
        if (extractedData.propertySize) {
          propertyInfo += propertyInfo ? ` de ${extractedData.propertySize} m²` : `votre propriété de ${extractedData.propertySize} m²`;
        }
        
        if (extractedData.yearBuilt) {
          propertyInfo += propertyInfo ? ` construite en ${extractedData.yearBuilt}` : `votre propriété construite en ${extractedData.yearBuilt}`;
        }
        
        if (propertyInfo) {
          response = `Merci pour ces informations détaillées sur ${propertyInfo}. `;
          
          // Recommandations personnalisées basées sur les caractéristiques
          if (extractedData.propertyType === 'house') {
            if (extractedData.yearBuilt && extractedData.yearBuilt < 1980) {
              response += `Pour une maison de cette époque, l'isolation est généralement la priorité absolue. Je vous recommande de vérifier l'isolation de votre toiture (30% des pertes), puis celle des murs (25% des pertes) et enfin des fenêtres (15% des pertes). `;
              
              if (extractedData.heatingType === 'central') {
                response += `Votre chauffage central pourrait également être modernisé pour un modèle à condensation plus efficace. `;
              }
            } else if (extractedData.yearBuilt && extractedData.yearBuilt < 2000) {
              response += `Pour une maison construite dans les années ${Math.floor(extractedData.yearBuilt/10)*10}, je vous recommande de vérifier l'efficacité de votre système de chauffage et d'envisager l'installation de panneaux photovoltaïques. `;
            } else {
              response += `Votre maison étant relativement récente, elle bénéficie probablement déjà d'une bonne isolation. Vous pourriez envisager des technologies comme une pompe à chaleur ou des panneaux solaires pour réduire davantage votre empreinte énergétique. `;
            }
          } else if (extractedData.propertyType === 'apartment') {
            response += `Pour un appartement, les principales économies d'énergie viennent généralement du remplacement des fenêtres et de l'optimisation du système de chauffage. `;
            
            if (extractedData.propertySize && extractedData.propertySize < 70) {
              response += `Pour un appartement de cette taille, un système de ventilation avec récupération de chaleur pourrait être particulièrement efficace. `;
            }
          }
          
          // Conclusion
          response += `Sur base de toutes les informations que vous m'avez fournies, je peux maintenant générer un rapport d'audit complet avec des recommandations personnalisées pour améliorer l'efficacité énergétique de votre propriété et réduire vos factures.`;
        } else {
          response = `Merci pour ces informations. Pour finaliser votre audit énergétique, pourriez-vous me préciser d'autres détails sur votre propriété ? Par exemple, s'agit-il d'une maison ou d'un appartement, quelle est sa superficie, et si possible son année de construction ?`;
        }
      } else {
        response = `Pour vous proposer des recommandations vraiment personnalisées, j'aurais besoin de quelques informations sur votre propriété. Pourriez-vous me dire s'il s'agit d'une maison ou d'un appartement, sa superficie approximative en m², et si possible son année de construction ?`;
      }
    }
    
    return {
      message: response,
      extractedData: extractedData
    };
  }
}

export default new OpenAIService();

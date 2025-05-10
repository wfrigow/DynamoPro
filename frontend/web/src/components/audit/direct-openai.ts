// Fonction utilitaire pour appeler l'API OpenAI via le proxy Express sécurisé
export async function callOpenAI(inputText: string, conversationHistory: any[]) {
  // URL du proxy Express sécurisé - utilise une variable d'environnement ou une URL par défaut
  const proxyUrl = process.env.REACT_APP_LLM_API_URL || '/api/llm';
  
  // Prompt système universel
  const systemPrompt = `Tu es l'Assistant d'Audit Énergétique DynamoPro. 
Ta mission : discuter naturellement avec l'utilisateur et extraire les données suivantes : 
- Type d'utilisateur (particulier, indépendant, entreprise, etc.)
- Région (Wallonie, Bruxelles, Flandre)
- Consommation électrique annuelle (kWh)
- Utilisation de gaz naturel (oui/non)
- Consommation de gaz annuelle (kWh ou m³)
- Type de propriété (maison, appartement, bâtiment commercial)
- Superficie (m²)
- Année de construction
- État de l'isolation

Réponds de manière conversationnelle, sans listes ni puces. Sois poli, concis et naturel.

Très important : à la fin de ta réponse, inclus un objet JSON avec les données extraites. Format :

{"userType": "particulier", "region": "wallonie", "electricityUsage": 3500, "gasUsage": true, "gasConsumption": 15000, "propertyType": "maison", "area": 120, "constructionYear": 1985, "insulationStatus": "moyen"}

Laisse les champs vides si l'information n'est pas fournie. Le JSON doit être valide.`;

  try {
    console.log('Appel à OpenAI API via le proxy Netlify');
    
    // Ajouter un timeout pour éviter les requêtes qui restent bloquées
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 secondes timeout
    
    let response;
    try {
      // Préparer les headers avec le Content-Type
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Ajouter l'API key depuis le localStorage si disponible
      const apiKey = localStorage.getItem('OPENAI_API_KEY');
      if (apiKey) {
        headers['Authorization'] = `Bearer ${apiKey}`;
      }
      
      response = await fetch(proxyUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [
            { role: 'system', content: systemPrompt },
            ...conversationHistory,
            { role: 'user', content: inputText }
          ],
          temperature: 0.7,
          max_tokens: 500
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Erreur de réponse OpenAI:', errorText);
        throw new Error(`Erreur OpenAI: ${response.status} - ${errorText}`);
      }
    } catch (fetchError: unknown) {
      clearTimeout(timeoutId);
      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        throw new Error('La requête a expiré après 30 secondes');
      }
      throw fetchError;
    }

    // Vérifier que la réponse existe avant de la traiter
    if (!response) {
      throw new Error('Aucune réponse reçue du serveur');
    }
    
    const data = await response.json();
    
    // Vérifier que la réponse contient les données attendues
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      console.error('Format de réponse OpenAI inattendu:', data);
      throw new Error('Format de réponse OpenAI inattendu');
    }
    
    const assistantContent = data.choices[0].message.content;
    console.log('Réponse OpenAI:', assistantContent);
    
    // Extraire les données JSON si présentes
    let extractedData = {};
    const jsonMatch = assistantContent.match(/\{[\s\S]*?\}/);
    let cleanedContent = assistantContent;
    
    if (jsonMatch) {
      try {
        const jsonStr = jsonMatch[0];
        extractedData = JSON.parse(jsonStr);
        cleanedContent = assistantContent.replace(jsonStr, '').trim();
      } catch (e) {
        console.error('Erreur lors du parsing JSON:', e);
      }
    }
    console.log('Données extraites:', extractedData);
    
    return {
      message: cleanedContent,
      extractedData: extractedData
    };
  } catch (error) {
    console.error('Erreur lors de l\'appel à OpenAI:', error);
    throw error;
  }
}

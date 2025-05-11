import React, { useState, useEffect, useRef } from 'react';
import { callOpenAI } from './direct-openai';
import { 
  Box, 
  Paper, 
  Typography, 
  IconButton, 
  TextField, 
  List, 
  ListItem, 
  ListItemText, 
  Divider,
  CircularProgress,
  Fab,
  Tooltip,
  Card,
  CardContent,
  Chip,
  Grid
} from '@mui/material';
import { 
  Mic, 
  MicOff, 
  Send, 
  ArrowUpward,
  Home,
  Bolt,
  Opacity,
  Delete,
  Nature,
  Business
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { saveAuditData as saveAuditDataToStorage } from '../../utils/auditStorage';
import { useDispatch } from 'react-redux';
import { setAuditData as setAuditDataAction, UserAuditData as FrontendUserAuditData } from '../../store/slices/profileSlice';

// Service d'intelligence artificielle utilisant l'API OpenAI réelle via le proxy
const OpenAIService = {
  processMessage: async (userMessage: string, conversationHistory: any[] = []) => {
    // Appel à l'API OpenAI via la fonction callOpenAI mise à jour
    return await callOpenAI(userMessage, conversationHistory);
  }
};

// Simple UUID generator function to replace uuid dependency
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Fonction pour générer des données extraites de secours basées sur l'entrée utilisateur
function generateFallbackExtractedData(userInput: string): ExtractedData {
  const input = userInput.toLowerCase();
  const extractedData: ExtractedData = {};
  
  // Essayer de détecter le type d'utilisateur
  if (input.includes('particulier') || input.includes('individu') || input.includes('personnel')) {
    extractedData.userType = 'particulier';
  } else if (input.includes('indépendant') || input.includes('freelance')) {
    extractedData.userType = 'indépendant';
  } else if (input.includes('entreprise') || input.includes('société') || input.includes('business')) {
    extractedData.userType = 'entreprise';
  }
  
  // Essayer de détecter la région
  if (input.includes('wallonie') || input.includes('liège') || input.includes('namur')) {
    extractedData.region = 'wallonie';
  } else if (input.includes('bruxelles') || input.includes('brussel')) {
    extractedData.region = 'bruxelles';
  } else if (input.includes('flandre') || input.includes('anvers') || input.includes('gand')) {
    extractedData.region = 'flandre';
  }
  
  // Essayer de détecter la consommation électrique
  const electricityMatch = input.match(/(\d+)\s*kwh/i);
  if (electricityMatch) {
    extractedData.electricityUsage = parseInt(electricityMatch[1]);
  }
  
  // Essayer de détecter l'utilisation de gaz
  if (input.includes('gaz')) {
    extractedData.gasUsage = true;
    
    // Essayer de détecter la consommation de gaz
    const gasMatch = input.match(/(\d+)\s*m3/i);
    if (gasMatch) {
      extractedData.gasConsumption = parseInt(gasMatch[1]);
    }
  } else if (input.includes('pas de gaz') || input.includes('sans gaz')) {
    extractedData.gasUsage = false;
  }
  
  // Essayer de détecter le type de propriété
  if (input.includes('maison')) {
    extractedData.propertyType = 'maison';
  } else if (input.includes('appartement')) {
    extractedData.propertyType = 'appartement';
  } else if (input.includes('bureau') || input.includes('commercial')) {
    extractedData.propertyType = 'commercial';
  }
  
  // Essayer de détecter la superficie
  const areaMatch = input.match(/(\d+)\s*m2/i);
  if (areaMatch) {
    extractedData.area = parseInt(areaMatch[1]);
  }
  
  // Essayer de détecter l'année de construction
  const yearMatch = input.match(/(19|20)(\d{2})/);
  if (yearMatch) {
    extractedData.constructionYear = parseInt(yearMatch[0]);
  }
  
  // Essayer de détecter l'état de l'isolation
  if (input.includes('bonne isolation') || input.includes('bien isolé')) {
    extractedData.insulationStatus = 'bonne';
  } else if (input.includes('isolation moyenne') || input.includes('moyennement isolé')) {
    extractedData.insulationStatus = 'moyenne';
  } else if (input.includes('mauvaise isolation') || input.includes('mal isolé')) {
    extractedData.insulationStatus = 'mauvaise';
  }
  
  return extractedData;
}

// Types pour les données d'audit unifiées

// Type pour toutes les données d'audit
interface AuditData {
  userType?: string;
  region?: string;
  electricityUsage?: number;
  gasUsage?: boolean;
  gasConsumption?: number;
  propertyType?: string;
  area?: number;
  constructionYear?: number;
  insulationStatus?: string;
}

// Type pour les données extraites (structure simplifiée)
interface ExtractedData {
  userType?: string;
  region?: string;
  electricityUsage?: number;
  gasUsage?: boolean;
  gasConsumption?: number;
  propertyType?: string;
  area?: number;
  constructionYear?: number;
  insulationStatus?: string;
}

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant' | 'system';
  timestamp: Date;
  extractedData?: ExtractedData;
}

interface ConversationHistoryItem {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface OpenAIResponse {
  message: string;
  extractedData: ExtractedData;
}

interface VoiceAuditAssistantProps {
  userId: string;
  onAuditComplete?: (auditData: Record<string, any>) => void;
}

const VoiceAuditAssistant: React.FC<VoiceAuditAssistantProps> = ({ 
  userId, 
  onAuditComplete 
}: VoiceAuditAssistantProps): JSX.Element => {
  // Déclarations d'état
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationHistory, setConversationHistory] = useState<ConversationHistoryItem[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [auditData, setAuditData] = useState<AuditData>({});
  const [currentAgentType, setCurrentAgentType] = useState<string>('profile');
  const initialAgentType = 'profile';
  const [processingMessage, setProcessingMessage] = useState<string>('');
  const [isAuditCompleted, setIsAuditCompleted] = useState<boolean>(false);
  const [isSpeechRecognitionAvailable, setIsSpeechRecognitionAvailable] = useState<boolean>(false);

  // Références
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const speechRecognition = useRef<any>(null); // Using 'any' for SpeechRecognition as type might not be globally available
  const conversationHistoryRef = useRef(conversationHistory);
  const auditDataRef = useRef(auditData);
  const isAuditCompletedRef = useRef(isAuditCompleted); 
  const theme = useTheme();
  const dispatch = useDispatch();

  useEffect(() => {
    conversationHistoryRef.current = conversationHistory;
  }, [conversationHistory]);

  useEffect(() => {
    auditDataRef.current = auditData;
  }, [auditData]);

  useEffect(() => {
    isAuditCompletedRef.current = isAuditCompleted; 
  }, [isAuditCompleted]);

  // Initialiser directement avec le message de bienvenue pour éviter les doublons
  const welcomeMessage: Message = {
    id: generateUUID(),
    content: "Bonjour ! Je suis votre assistant d'audit énergétique DynamoPro. Je vais vous aider à réaliser un bilan complet pour vous proposer des recommandations personnalisées. Dites-moi tout sur votre profil (particulier, entreprise), votre région, votre consommation d'énergie et votre propriété.",
    sender: 'assistant',
    timestamp: new Date()
  };

  useEffect(() => {
    // Ajouter le message de bienvenue à l'historique de conversation pour OpenAI
    setConversationHistory([
      { role: 'system', content: `Type d'agent actuel: ${initialAgentType}` },
      { role: 'assistant', content: welcomeMessage.content }
    ]);
  }, []); // Dépendances vides = exécution unique au montage
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Initialize speech recognition
  useEffect(() => {
    // Check if browser supports SpeechRecognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSpeechRecognitionAvailable(true);
      speechRecognition.current = new SpeechRecognition();
      speechRecognition.current.continuous = true;
      speechRecognition.current.interimResults = true;
      speechRecognition.current.lang = 'fr-FR'; // Set to French
      
      speechRecognition.current.onresult = (event: any) => {
        // Use type assertions to help TypeScript understand the structure
        const results = event.results as any[];
        const transcript = Array.from(results)
          .map((result: any) => result[0])
          .map((result: any) => result.transcript as string)
          .join('');
        
        setInputText(transcript);
      };
      
      speechRecognition.current.onerror = (event: Event) => {
        console.error('Speech recognition error');
        setIsRecording(false);
      };
    }
    
    return () => {
      if (speechRecognition.current) {
        speechRecognition.current.stop();
      }
    };
  }, []);
  
  const toggleRecording = () => {
    if (isRecording) {
      speechRecognition.current?.stop();
    } else {
      speechRecognition.current?.start();
    }
    setIsRecording(!isRecording);
  };

  const addMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);

    if (message.sender === 'user' || message.sender === 'assistant') {
      setConversationHistory((prev) => [
        ...prev,
        {
          role: message.sender as 'user' | 'assistant' | 'system',
          content: message.content
        }
      ]);
    }
  };

  // Fonction pour traiter le message utilisateur avec l'IA
  const processUserMessage = async (
    userInput: string, 
    currentAgentTypeArg: string, 
    currentConversationHistory: ConversationHistoryItem[]
  ): Promise<OpenAIResponse | null> => { // Explicit return type
    setIsProcessing(true);
    setProcessingMessage(`Traitement de votre demande avec l'agent ${currentAgentTypeArg}...`);

    // Construire l'historique de conversation pour l'API OpenAI
    const apiConversationHistory = [
      { role: 'system', content: `Vous êtes un assistant spécialisé dans la collecte d'informations pour un audit énergétique. Agent actuel: ${currentAgentTypeArg}. Objectif: collecter des informations spécifiques à cet agent. Posez des questions claires et concises.` },
      ...currentConversationHistory,
      { role: 'user', content: userInput }
    ];

    try {
      // Appel corrigé: OpenAIService.processMessage attend 2 arguments
      const response = await OpenAIService.processMessage(userInput, apiConversationHistory.slice(0, -1)); 
      // Pass all history except the last user message which is the new prompt itself

      let aiResponseText = "Je n'ai pas compris, pouvez-vous reformuler ?";
      let extractedDataFromAI: ExtractedData = {};

      if (typeof response === 'string') {
        aiResponseText = response; // Simple string response
      } else if (response && response.message) {
        aiResponseText = response.message;
        if (response.extractedData) {
          extractedDataFromAI = response.extractedData;
        }
      }

      if (Object.keys(extractedDataFromAI).length === 0) {
        console.log("AI did not return structured data, attempting fallback extraction.");
        extractedDataFromAI = generateFallbackExtractedData(userInput + " " + aiResponseText);
      }

      addMessage({
        id: generateUUID(),
        content: aiResponseText,
        sender: 'assistant',
        timestamp: new Date(),
        extractedData: extractedDataFromAI
      });

      if (Object.keys(extractedDataFromAI).length > 0) {
        updateAuditData(extractedDataFromAI);
      }

      return { message: aiResponseText, extractedData: extractedDataFromAI }; // Return the response and data

    } catch (error) {
      console.error('Erreur lors de la communication avec l\'API:', error);
      const errorMessage: Message = {
        id: generateUUID(),
        content: "Désolé, j'ai rencontré une erreur technique. Vos informations ont été sauvegardées localement. Vous pouvez continuer ou rafraîchir la page si le problème persiste.",
        sender: 'system',
        timestamp: new Date()
      };

      addMessage(errorMessage);

      try {
        const currentAuditData = {
          timestamp: new Date().toISOString(),
          data: auditData
        };
        localStorage.setItem('dynamopro_current_audit', JSON.stringify(currentAuditData));
        console.log('Données d\'audit sauvegardées en mode secours');
      } catch (storageError) {
        console.error('Erreur lors de la sauvegarde de secours:', storageError);
      }
      return null; // Return null in case of error
    } finally {
      setIsProcessing(false);
      setProcessingMessage("");
    }
  };

  const updateAuditData = (extractedData: ExtractedData) => {
    if (!extractedData || Object.keys(extractedData).length === 0) return;

    setAuditData((prevData) => {
      const newData = { ...prevData, ...extractedData };
      auditDataRef.current = newData; // Update ref immediately
      checkIfAuditIsComplete(newData); // Pass the fresh newData
      return newData;
    });
  };

  // Vérifier si toutes les données nécessaires pour l'audit sont collectées
  const checkIfAuditIsComplete = (data: AuditData): boolean => {
    // Logique de complétion basée sur la structure AuditData aplatie
    const profileFieldsComplete = data.userType && data.region;
    const consumptionFieldsComplete = 
      data.electricityUsage !== undefined && 
      data.gasUsage !== undefined; // gasConsumption est optionnel
    const propertyFieldsComplete = 
      data.propertyType && 
      data.area !== undefined; // constructionYear et insulationStatus sont optionnels

    const isComplete = 
      !!profileFieldsComplete && 
      !!consumptionFieldsComplete && 
      !!propertyFieldsComplete;

    if (isComplete && !isAuditCompletedRef.current) { 
      console.log("Audit is complete according to checkIfAuditIsComplete. Finalizing...", data);
      finalizeAudit(); 
    }
    return isComplete;
  };

  // Finaliser l'audit, obtenir un résumé JSON et sauvegarder
  const finalizeAudit = async () => {
    if (isAuditCompletedRef.current) { 
      console.log("FinalizeAudit called but audit is already completed.");
      return;
    }
    console.log("Finalizing audit...");
    setIsProcessing(true);
    setProcessingMessage("Finalisation de l'audit et génération du résumé...");

    // Utiliser l'historique complet pour le résumé
    const finalPrompt = "Nous avons terminé la collecte d'informations pour l'audit énergétique. Peux-tu fournir un résumé complet et structuré de toutes les données collectées au format JSON ? Assure-toi d'inclure toutes les informations pertinentes que j'ai fournies.";
    
    // Construire un historique de conversation spécifique pour la finalisation si nécessaire
    // ou simplement utiliser conversationHistoryRef.current qui est le plus à jour.
    const historyForSummary = [...conversationHistoryRef.current, {role: 'user', content: finalPrompt}];

    try {
      // Appeler l'API OpenAI pour obtenir le résumé JSON
      const response = await OpenAIService.processMessage(finalPrompt, historyForSummary);
      
      let summaryData: ExtractedData = {};
      if (typeof response === 'string') {
        // Si la réponse est une chaîne, essayer de la parser comme JSON
        // Cela peut arriver si l'API ne renvoie pas la structure attendue
        try {
          const parsedResponse = JSON.parse(response);
          if (parsedResponse.extractedData) {
            summaryData = parsedResponse.extractedData;
          } else if (typeof parsedResponse === 'object') {
            // Si la réponse parsée est un objet mais sans extractedData, l'utiliser directement
            summaryData = parsedResponse;
          } else {
            // Si la réponse n'est pas un JSON valide ou n'a pas la structure attendue
            // On se rabat sur les données collectées dans auditData
            addMessage({
              id: generateUUID(),
              content: `Je n'ai pas pu obtenir un résumé structuré de l'IA. J'utiliserai les données collectées: ${response}`,
              sender: 'system',
              timestamp: new Date(),
            });
            summaryData = { ...auditDataRef.current }; // Utiliser la réf pour auditData
          }
        } catch (e) {
          console.error("Failed to parse summary response from AI as JSON:", e);
          addMessage({
            id: generateUUID(),
            content: `Erreur lors du traitement du résumé de l'IA. J'utiliserai les données collectées. Réponse IA: ${response}`,
            sender: 'system',
            timestamp: new Date(),
          });
          summaryData = { ...auditDataRef.current }; // Utiliser la réf pour auditData
        }
      } else if (response && response.extractedData) {
        summaryData = response.extractedData;
      } else {
        // Si la réponse n'est pas une chaîne et n'a pas extractedData, utiliser auditData
        console.warn("AI response for summary was not in expected format, falling back to collected auditData.");
        summaryData = { ...auditDataRef.current }; // Utiliser la réf pour auditData
      }

      // S'assurer que summaryData contient bien toutes les informations de auditData
      // car l'IA peut omettre des champs ou mal interpréter.
      const comprehensiveSummary = { ...auditDataRef.current, ...summaryData };
      setAuditData(comprehensiveSummary); // Mettre à jour l'état final avec le résumé le plus complet.

      addMessage({
        id: generateUUID(),
        content: "Audit finalisé. Voici le résumé des informations collectées :\n" + JSON.stringify(comprehensiveSummary, null, 2),
        sender: 'assistant',
        timestamp: new Date(),
        extractedData: comprehensiveSummary
      });

      // Sauvegarder les données d'audit finales et complètes
      await saveAuditData(comprehensiveSummary);
      setIsAuditCompleted(true); // Marquer l'audit comme terminé
      if(onAuditComplete) {
        onAuditComplete(comprehensiveSummary as Record<string, any>);
      }
      setProcessingMessage("Audit terminé. Vous pouvez maintenant voir vos recommandations.");

    } catch (error) {
      console.error("Error finalizing audit:", error);
      addMessage({
        id: generateUUID(),
        content: "Une erreur est survenue lors de la finalisation de l'audit. Les données actuelles ont été sauvegardées.",
        sender: 'system',
        timestamp: new Date(),
      });
      // Sauvegarder quand même les données actuelles en cas d'erreur de finalisation AI
      await saveAuditData(auditDataRef.current); // Utiliser la réf pour auditData
    } finally {
      setIsProcessing(false);
      setProcessingMessage("");
    }
  };

  const checkAndSwitchAgentIfNeeded = () => {
    if (currentAgentType === 'profile' && auditData.userType && auditData.region) {
      console.log("Passage à l'agent de consommation");
      setCurrentAgentType('consumption');

      const transitionMessage: Message = {
        id: generateUUID(),
        content: "Maintenant, parlons de votre consommation énergétique. Utilisez-vous principalement de l'électricité, du gaz, ou les deux ? Connaissez-vous votre consommation annuelle ?",
        sender: 'assistant',
        timestamp: new Date()
      };

      addMessage(transitionMessage);
      return true;
    }

    if (currentAgentType === 'consumption' && (typeof auditData.electricityUsage === 'number' || auditData.electricityUsage === false) && (typeof auditData.gasUsage === 'boolean')) {
      console.log("Passage à l'agent de propriété");
      setCurrentAgentType('property');

      const transitionMessage: Message = {
        id: generateUUID(),
        content: "Parlons maintenant de votre propriété. S'agit-il d'un appartement, d'une maison ou d'un bâtiment commercial ? Quelle est sa superficie approximative et son année de construction ?",
        sender: 'assistant',
        timestamp: new Date()
      };

      addMessage(transitionMessage);
      return true;
    }

    if (currentAgentType === 'property' && auditData.propertyType && auditData.area && auditData.constructionYear && auditData.insulationStatus) {
      console.log('Finalisation de l\'audit - toutes les données nécessaires sont collectées');

      const transitionMessage: Message = {
        id: generateUUID(),
        content: "Merci pour toutes ces informations. Je vais maintenant finaliser l'audit et préparer vos recommandations personnalisées.",
        sender: 'assistant',
        timestamp: new Date()
      };

      addMessage(transitionMessage);

      setTimeout(() => {
        finalizeAudit();
      }, 1000);
    }

    return false;
  };

  // Gérer l'envoi de message par l'utilisateur
  const handleSendMessage = async () => {
    if (!inputText.trim() || isProcessing) return;

    const userMessage: Message = {
      id: generateUUID(),
      content: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    addMessage(userMessage);
    const currentInputText = inputText; // Capture inputText before clearing
    setInputText('');
    // No need to setIsProcessing(true) here, processUserMessage does it

    // Pass the current conversation history from the ref
    const aiOutcome = await processUserMessage(currentInputText, currentAgentType, conversationHistoryRef.current);

    if (aiOutcome && aiOutcome.message) { // Check if aiOutcome is not null and has a message
      // AI message is already added by processUserMessage
      // Extracted data is already updated by processUserMessage
      // So, no need to call addMessage or updateAuditData here again for the AI response itself.
      
      // Only need to check if agent needs to switch
      checkAndSwitchAgentIfNeeded();
    } else {
      // Error or no response case is handled within processUserMessage by adding a system error message
      console.log("handleSendMessage: processUserMessage returned null or no message, error likely handled within.");
    }
    // setIsProcessing(false) is handled by processUserMessage's finally block
  };

  // Sauvegarder les données d'audit
  const saveAuditData = async (dataToSave: AuditData) => { // dataToSave is the local component's AuditData type
    console.log("Attempting to save audit data:", dataToSave, "for user:", userId);
    if (!userId) {
      console.error("User ID is missing, cannot save audit data.");
      // Peut-être afficher un message à l'utilisateur ou simplement ne pas sauvegarder
      addMessage({
        id: generateUUID(),
        content: "Erreur: Impossible de sauvegarder l'audit car l'identifiant utilisateur est manquant.",
        sender: 'system',
        timestamp: new Date(),
      });
      return; // Ne pas continuer si userId est manquant
    }

    try {
      // 1. Save to localStorage (using specific key as per memory)
      const localDataToStore = {
        timestamp: new Date().toISOString(),
        data: dataToSave,
        userId: userId 
      };
      localStorage.setItem('dynamopro_current_audit', JSON.stringify(localDataToStore));
      console.log('Audit data saved to localStorage under dynamopro_current_audit.');

      // 2. Save to backend API
      const response = await fetch('/api/v1/audits', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({ userId: userId, auditData: dataToSave }), // Utiliser le userId des props
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Failed to save audit data to server: ${response.status} - ${errorText}`);
        // Envoyer un message système à l'utilisateur au lieu de lancer une erreur qui pourrait ne pas être gérée plus haut
        addMessage({
          id: generateUUID(),
          content: `Les données ont été sauvegardées localement, mais une erreur est survenue lors de la sauvegarde sur le serveur: ${response.status}. Veuillez vérifier votre connexion ou contacter le support.`,
          sender: 'system',
          timestamp: new Date(),
        });
        // Ne pas lever d'erreur ici pour permettre à l'audit de se sentir complété côté client si la sauvegarde locale a réussi
      } else {
        const result = await response.json();
        console.log('Audit data saved to server successfully:', result);
        addMessage({
          id: generateUUID(),
          content: "Les données d'audit ont été sauvegardées avec succès sur le serveur et localement.",
          sender: 'system',
          timestamp: new Date(),
        });
        
        // Dispatch to Redux store with the auditData from the server response
        if (result && result.auditData) {
          // Ensure the structure matches FrontendUserAuditData for type safety
          // The backend's AuditData structure is { profile: {}, consumption: {}, property: {} }
          // which matches our FrontendUserAuditData (formerly UserAuditData in profileSlice)
          dispatch(setAuditDataAction(result.auditData as FrontendUserAuditData));
          console.log('Audit data dispatched to Redux store:', result.auditData);
        } else {
          console.warn('Server response did not contain auditData, Redux store not updated from server response.');
        }
      }
      
      // 3. Potentially update Redux store (placeholder for actual Redux integration)
      // if (dispatch && typeof updateUserAuditDataAction === 'function') {
      //   dispatch(updateUserAuditDataAction(dataToSave)); // This was the old placeholder
      //   console.log('Audit data dispatched to Redux store.');
      // }

    } catch (error) {
      console.error('Error during saveAuditData (network error or other):', error);
      addMessage({
        id: generateUUID(),
        content: `Une erreur réseau ou autre est survenue lors de la tentative de sauvegarde des données sur le serveur. Les données sont sauvegardées localement. Erreur: ${error instanceof Error ? error.message : String(error)}`,
        sender: 'system',
        timestamp: new Date(),
      });
      // Ne pas relancer l'erreur pour que l'audit puisse continuer/finaliser côté client basé sur la sauvegarde locale.
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: theme.palette.background.default }}>
      <Paper elevation={0} sx={{ p: 2, bgcolor: theme.palette.primary.main, color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {currentAgentType === 'profile' ? <Home /> : currentAgentType === 'consumption' ? <Bolt /> : <Business />}
          <Typography variant="h6" sx={{ ml: 1 }}>
            {`Assistant d'Audit ${currentAgentType === 'profile' ? 'Profil' : currentAgentType === 'consumption' ? 'Consommation' : 'Propriété'}`}
          </Typography>
        </Box>
        <Tooltip title="Remonter au début de la conversation">
          <IconButton color="inherit" onClick={() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
            <ArrowUpward />
          </IconButton>
        </Tooltip>
      </Paper>

      <List>
        {messages.map((message) => (
          <ListItem key={message.id} sx={{ justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start', mb: 2 }}>
            <Card sx={{ maxWidth: '80%', bgcolor: message.sender === 'user' ? theme.palette.primary.light : theme.palette.background.paper, color: message.sender === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary }}>
              <CardContent>
                <Typography variant="body1">{message.content}</Typography>

                {message.extractedData && Object.keys(message.extractedData).length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Informations collectées:
                    </Typography>
                    <Grid container spacing={1} sx={{ mt: 0.5 }}>
                      {Object.entries(message.extractedData).map(([key, value]) => (
                        <Grid item key={key}>
                          <Chip size="small" label={`${key}: ${value}`} variant="outlined" />
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}

                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              </CardContent>
            </Card>
          </ListItem>
        ))}
        <div ref={messagesEndRef} />
      </List>

      {isProcessing && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <CircularProgress size={24} />
        </Box>
      )}

      <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}`, display: 'flex', alignItems: 'center' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Tapez votre message ici..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          disabled={isProcessing}
          sx={{ mr: 1 }}
          multiline
          maxRows={3}
        />
        <Tooltip title={isRecording ? "Arrêter l'enregistrement" : "Enregistrer un message vocal"}>
          <IconButton 
            color={isRecording ? "secondary" : "primary"} 
            onClick={toggleRecording}
            disabled={isProcessing || !isSpeechRecognitionAvailable}
          >
            {isRecording ? <MicOff /> : <Mic />}
          </IconButton>
        </Tooltip>
        <Tooltip title="Envoyer le message">
          <IconButton 
            color="primary" 
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isProcessing}
          >
            <Send />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default VoiceAuditAssistant;

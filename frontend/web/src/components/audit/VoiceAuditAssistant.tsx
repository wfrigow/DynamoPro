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

// Service d'intelligence artificielle utilisant l'API OpenAI réelle via le proxy
const OpenAIService = {
  processMessage: async (userMessage: string, agentType: string, conversationHistory: any[] = []) => {
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
function generateFallbackExtractedData(userInput: string, agentType: string): ExtractedData {
  const input = userInput.toLowerCase();
  const extractedData: ExtractedData = {};
  
  // Extraire des informations de base selon le type d'agent
  if (agentType === 'profile') {
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
  } else if (agentType === 'consumption') {
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
  } else if (agentType === 'property') {
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
      extractedData.insulationStatus = 'bon';
    } else if (input.includes('isolation moyenne') || input.includes('moyennement isolé')) {
      extractedData.insulationStatus = 'moyen';
    } else if (input.includes('mauvaise isolation') || input.includes('mal isolé')) {
      extractedData.insulationStatus = 'mauvais';
    }
  }
  
  return extractedData;
}

// Types
// Types pour les données d'audit extraites
interface ProfileData {
  userType?: string;
  region?: string;
}

interface ConsumptionData {
  electricityUsage?: number;
  gasUsage?: boolean;
  gasConsumption?: number;
}

interface PropertyData {
  propertyType?: string;
  area?: number;
  constructionYear?: number;
  insulationStatus?: string;
}

// Type union pour toutes les données extraites possibles
type ExtractedData = ProfileData & ConsumptionData & PropertyData;

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

// Type pour les données d'audit complètes
interface AuditData {
  profile: ProfileData;
  consumption: ConsumptionData;
  property: PropertyData;
}

interface VoiceAuditAssistantProps {
  userId: string;
  initialAgentType?: 'profile' | 'consumption' | 'property';
  onAuditComplete?: (auditData: Record<string, any>) => void;
}

const VoiceAuditAssistant: React.FC<VoiceAuditAssistantProps> = ({ 
  userId, 
  initialAgentType = 'profile',
  onAuditComplete 
}) => {
  const theme = useTheme();
  // Initialiser directement avec le message de bienvenue pour éviter les doublons
  const welcomeMessage: Message = {
    id: generateUUID(),
    content: initialAgentType === 'profile' 
      ? "Bonjour ! Je suis votre assistant d'audit DynamoPro. Pour commencer, pourriez-vous me dire si vous êtes un particulier, un indépendant ou une entreprise ?" 
      : initialAgentType === 'consumption'
      ? "Parlons de votre consommation énergétique. Utilisez-vous principalement de l'électricité, du gaz, ou les deux ? Connaissez-vous votre consommation annuelle ?"
      : "Décrivez-moi votre propriété. S'agit-il d'un appartement, d'une maison ou d'un bâtiment commercial ?",
    sender: 'assistant' as 'user' | 'assistant' | 'system',
    timestamp: new Date()
  };
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentAgentType, setCurrentAgentType] = useState<'profile' | 'consumption' | 'property'>(initialAgentType);
  const [auditData, setAuditData] = useState<Record<string, any>>({
    profile: {},
    consumption: {},
    property: {}
  });
  
  // Historique de conversation pour le LLM
  const [conversationHistory, setConversationHistory] = useState<ConversationHistoryItem[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const speechRecognition = useRef<any>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Initialiser l'historique de conversation avec le message de bienvenue
  useEffect(() => {
    // Ajouter le message de bienvenue à l'historique de conversation pour OpenAI
    setConversationHistory([
      { role: 'system', content: `Type d'agent actuel: ${currentAgentType}` },
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
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      speechRecognition.current = new SpeechRecognition();
      speechRecognition.current.continuous = true;
      speechRecognition.current.interimResults = true;
      speechRecognition.current.lang = 'fr-FR'; // Set to French
      
      speechRecognition.current.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0])
          .map((result) => result.transcript)
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
    setMessages(prev => [...prev, message]);
    
    // Si le message est de l'utilisateur ou de l'assistant, l'ajouter à l'historique de conversation
    if (message.sender === 'user' || message.sender === 'assistant') {
      setConversationHistory(prev => [
        ...prev,
        { role: message.sender, content: message.content }
      ]);
    }
  };
  
  // Analyser la conversation pour éviter les questions répétitives
  const analyzeConversationContext = () => {
    // Récupérer les derniers messages pour l'analyse contextuelle
    const lastMessages = messages.slice(-5);
    const lastUserMessages = lastMessages.filter(m => m.sender === 'user').map(m => m.content.toLowerCase());
    const lastAssistantMessages = lastMessages.filter(m => m.sender === 'assistant').map(m => m.content.toLowerCase());
    
    // Détecter si l'assistant pose des questions répétitives
    const repetitiveQuestions = {
      userType: lastAssistantMessages.filter(m => 
        m.includes('particulier') && m.includes('indépendant') && m.includes('entreprise')
      ).length > 1,
      region: lastAssistantMessages.filter(m => 
        m.includes('région') && m.includes('wallonie') && m.includes('bruxelles')
      ).length > 1,
      consumption: lastAssistantMessages.filter(m => 
        m.includes('consommation') && m.includes('électricité') && m.includes('kwh')
      ).length > 1,
      property: lastAssistantMessages.filter(m => 
        m.includes('propriété') && m.includes('maison') && m.includes('appartement')
      ).length > 1
    };
    
    // Détecter si l'utilisateur a déjà fourni certaines informations
    const userProvidedInfo = {
      userType: lastUserMessages.some(m => 
        m.includes('particulier') || m.includes('indépendant') || m.includes('entreprise') ||
        m.includes('individu') || m.includes('société') || m.includes('freelance')
      ),
      region: lastUserMessages.some(m => 
        m.includes('wallonie') || m.includes('bruxelles') || m.includes('flandre') ||
        m.includes('liège') || m.includes('namur') || m.includes('anvers')
      ),
      consumption: lastUserMessages.some(m => 
        m.includes('kwh') || m.includes('électricité') || m.includes('gaz') ||
        m.includes('consommation') || /\d+/.test(m)
      ),
      property: lastUserMessages.some(m => 
        m.includes('maison') || m.includes('appartement') || m.includes('m2') ||
        m.includes('construction') || m.includes('bâtiment')
      )
    };
    
    return { repetitiveQuestions, userProvidedInfo };
  };
  
  // Fonction pour mettre à jour les données d'audit avec les informations extraites
  const updateAuditData = (extractedData: ExtractedData) => {
    if (!extractedData || Object.keys(extractedData).length === 0) return;
    
    console.log('Mise à jour des données d\'audit avec:', extractedData);
    
    setAuditData(prevData => {
      const newData = { ...prevData };
      
      // Mettre à jour toutes les données extraites, quel que soit l'agent actuel
      // Données de profil
      if (extractedData.userType) {
        newData.profile.userType = extractedData.userType;
      }
      if (extractedData.region) {
        newData.profile.region = extractedData.region;
      }
      
      // Données de consommation
      if (extractedData.electricityUsage) {
        newData.consumption.electricityUsage = extractedData.electricityUsage;
      }
      if (extractedData.gasUsage !== undefined) {
        newData.consumption.gasUsage = extractedData.gasUsage;
      }
      if (extractedData.gasConsumption) {
        newData.consumption.gasConsumption = extractedData.gasConsumption;
      }
      
      // Données de propriété
      if (extractedData.propertyType) {
        newData.property.type = extractedData.propertyType;
      }
      if (extractedData.area) {
        newData.property.size = extractedData.area;
      }
      if (extractedData.constructionYear) {
        newData.property.constructionYear = extractedData.constructionYear;
      }
      if (extractedData.insulationStatus) {
        newData.property.insulation = extractedData.insulationStatus;
      }
      
      console.log('Nouvelles données d\'audit:', newData);
      return newData;
    });
  };

  // Fonction pour sauvegarder les données d'audit dans le backend
  const saveAuditData = async (data: AuditData) => {
    try {
      // Récupérer l'ID utilisateur depuis le localStorage ou le contexte d'authentification
      const userId = localStorage.getItem('userId') || '00000000-0000-0000-0000-000000000000';
      
      // Sauvegarder les données localement d'abord (comme sauvegarde)
      const localAuditKey = `audit_${userId}_${new Date().toISOString()}`;
      localStorage.setItem(localAuditKey, JSON.stringify({
        userId,
        auditData: data,
        createdAt: new Date().toISOString()
      }));
      console.log('Données d\'audit sauvegardées localement:', localAuditKey);
      
      try {
        const response = await fetch('/api/v1/audits', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            userId: userId,
            auditData: data
          })
        });
        
        if (!response.ok) {
          throw new Error(`Erreur lors de la sauvegarde des données d'audit: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Données d\'audit sauvegardées avec succès sur le serveur:', result);
        return result;
      } catch (apiError) {
        console.error('Erreur lors de la sauvegarde des données d\'audit sur le serveur:', apiError);
        console.log('Utilisation des données sauvegardées localement');
        
        // Retourner un objet similaire à ce que l'API aurait retourné
        return {
          id: generateUUID(),
          userId,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          auditData: data
        };
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des données d\'audit:', error);
      // Continuer malgré l'erreur pour ne pas bloquer l'utilisateur
      return {
        id: generateUUID(),
        userId: localStorage.getItem('userId') || '00000000-0000-0000-0000-000000000000',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        auditData: data
      };
    }
  };

  // Fonction pour générer des recommandations détaillées basées sur l'IA
  const finalizeAudit = async () => {
    setIsProcessing(true);
    
    try {
      // Importer l'utilitaire de stockage d'audit
      const { saveAuditData } = await import('../../utils/auditStorage');
      
      // Créer un prompt pour demander un résumé structuré des données collectées
      const finalPrompt = "Nous avons terminé l'audit. Peux-tu résumer toutes les informations collectées au format JSON avec la structure suivante : { userType, region, electricityUsage, gasUsage, gasConsumption, propertyType, area, constructionYear, insulationStatus } ? Utilise uniquement les informations fournies pendant notre conversation.";
      
      // Ajouter le message système à l'interface utilisateur
      const systemMessage: Message = {
        id: generateUUID(),
        content: "Finalisation de l'audit et génération du résumé...",
        sender: 'system',
        timestamp: new Date()
      };
      
      setMessages(msgs => [...msgs, systemMessage]);
      
      // Appeler l'API OpenAI pour obtenir le résumé structuré
      const response = await OpenAIService.processMessage(finalPrompt, 'summary', conversationHistory);
      
      console.log('Réponse du résumé structuré:', response);
      
      // Essayer d'extraire le JSON de la réponse
      let jsonData: any = null;
      
      // Rechercher un objet JSON dans la réponse
      const jsonMatch = response.message.match(/\{[\s\S]*?\}/g);
      if (jsonMatch && jsonMatch.length > 0) {
        try {
          jsonData = JSON.parse(jsonMatch[0]);
          console.log('Données JSON extraites:', jsonData);
        } catch (e) {
          console.error('Erreur lors du parsing JSON:', e);
        }
      }
      
      if (!jsonData) {
        // Essayer d'extraire les données via le extractedData fourni par l'API
        jsonData = response.extractedData || {};
      }
      
      if (jsonData) {
        // Formater les données pour l'API de recommandations
        const formattedData = {
          timestamp: new Date().toISOString(),
          data: jsonData
        };
        
        // Utiliser l'utilitaire pour sauvegarder les données d'audit
        const saveResult = saveAuditData(formattedData);
        
        if (!saveResult) {
          console.warn('Problème lors de la sauvegarde des données d\'audit avec l\'utilitaire, utilisation de la méthode de secours');
          // Méthode de secours: sauvegarder directement dans localStorage
          localStorage.setItem('dynamopro_current_audit', JSON.stringify(formattedData));
        }
        
        // Ajouter un message d'assistant montrant le résumé
        const summaryMessage: Message = {
          id: generateUUID(),
          content: `Merci pour toutes ces informations ! J'ai résumé les données de votre audit et les ai sauvegardées dans votre profil. Vous pouvez maintenant accéder à vos recommandations personnalisées ou consulter ces données dans votre profil.`,
          sender: 'assistant',
          timestamp: new Date(),
          extractedData: jsonData
        };
        
        setMessages(msgs => [...msgs, summaryMessage]);
        
        // Appeler le callback onAuditComplete si fourni
        if (onAuditComplete) {
          onAuditComplete(formattedData);
        }
        
        return formattedData;
      } else {
        throw new Error('Impossible d\'extraire les données structurées de la réponse');
      }
    } catch (error) {
      console.error('Erreur lors de la finalisation de l\'audit:', error);
      
      // Ajouter un message d'erreur
      const errorMessage: Message = {
        id: generateUUID(),
        content: "Désolé, j'ai rencontré une erreur lors de la finalisation de l'audit. Veuillez réessayer ou contacter le support.",
        sender: 'system',
        timestamp: new Date()
      };
      
      setMessages(msgs => [...msgs, errorMessage]);
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  // Fonction pour vérifier et éventuellement changer d'agent
  const checkAndSwitchAgentIfNeeded = () => {
    console.log('Vérification du changement d\'agent:', currentAgentType);
    console.log('Données de profil:', auditData.profile);
    console.log('Données de consommation:', auditData.consumption);
    
    // Si nous sommes en train de collecter des informations de profil et que nous avons
    // suffisamment d'informations (userType et region), passer à l'agent de consommation
    if (currentAgentType === 'profile' && 
        auditData.profile.userType && 
        auditData.profile.region) {
          
      console.log('Passage à l\'agent de consommation');
      setCurrentAgentType('consumption');
      
      // Ajouter un message de transition
      const transitionMessage: Message = {
        id: generateUUID(),
        content: "Maintenant, parlons de votre consommation énergétique. Utilisez-vous principalement de l'électricité, du gaz, ou les deux ? Connaissez-vous votre consommation annuelle ?",
        sender: 'assistant',
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, transitionMessage]);
      
      // Mettre à jour l'historique de conversation avec le nouveau contexte
      setConversationHistory(history => [
        ...history,
        {
          role: 'assistant',
          content: transitionMessage.content
        }
      ]);
      
      return;
    }
    
    // Si nous sommes en train de collecter des informations de consommation et que nous avons
    // des données sur l'électricité et le gaz, passer à l'agent de propriété
    if (currentAgentType === 'consumption' && 
        (typeof auditData.consumption.electricityUsage === 'number' || auditData.consumption.electricityUsage === false) && 
        (typeof auditData.consumption.gasUsage === 'boolean')) {
          
      console.log('Passage à l\'agent de propriété');
      setCurrentAgentType('property');
      
      // Ajouter un message de transition
      const transitionMessage: Message = {
        id: generateUUID(),
        content: "Parlons maintenant de votre propriété. S'agit-il d'un appartement, d'une maison ou d'un bâtiment commercial ? Quelle est sa superficie approximative et son année de construction ?",
        sender: 'assistant',
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, transitionMessage]);
      
      // Mettre à jour l'historique de conversation avec le nouveau contexte
      setConversationHistory(history => [
        ...history,
        {
          role: 'assistant',
          content: transitionMessage.content
        }
      ]);
      
      return;
    }
    
    // Si nous avons collecté des informations sur la propriété et qu'elles sont suffisantes, finaliser l'audit
    if (currentAgentType === 'property' && 
        auditData.property.propertyType && 
        auditData.property.area && 
        auditData.property.constructionYear) {
          
      console.log('Finalisation de l\'audit - toutes les données nécessaires sont collectées');
      
      // Ajouter un message de transition avant la finalisation
      const transitionMessage: Message = {
        id: generateUUID(),
        content: "Merci pour toutes ces informations. Je vais maintenant finaliser l'audit et préparer vos recommandations personnalisées.",
        sender: 'assistant',
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, transitionMessage]);
      
      // Mettre à jour l'historique de conversation avec le message de finalisation
      setConversationHistory(history => [
        ...history,
        {
          role: 'assistant',
          content: transitionMessage.content
        }
      ]);
      
      // Lancer la finalisation de l'audit de manière asynchrone
      setTimeout(() => {
        finalizeAudit();
      }, 1000);
      
      return;
    }
  };
  
  const handleSendMessage = async () => {
    if (!inputText.trim() || isProcessing) return;
    
    // Ajouter le message de l'utilisateur à la conversation
    const userMessage: Message = {
      id: generateUUID(),
      content: inputText,
      sender: 'user',
      timestamp: new Date()
    };
    
    addMessage(userMessage);
    setInputText('');
    setIsProcessing(true);
    
    try {
      // Appeler l'API OpenAI pour obtenir une réponse
      let response;
      try {
        response = await OpenAIService.processMessage(inputText, currentAgentType, conversationHistory);
      } catch (apiError) {
        console.error('Erreur lors de l\'appel à l\'API OpenAI:', apiError);
        
        // Utiliser une réponse de secours si l'API est indisponible
        response = {
          message: "Je comprends votre demande. Malheureusement, je rencontre des difficultés de connexion avec mon service de traitement. Je vais tout de même enregistrer vos informations et continuer notre conversation.",
          extractedData: generateFallbackExtractedData(inputText, currentAgentType)
        };
      }
      
      // Extraire les données de la réponse
      const extractedData = response.extractedData || {};
      
      // Mettre à jour les données d'audit avec les informations extraites
      if (Object.keys(extractedData).length > 0) {
        updateAuditData(extractedData);
      }
      
      // Ajouter la réponse de l'assistant à la conversation
      const assistantMessage: Message = {
        id: generateUUID(),
        content: response.message,
        sender: 'assistant',
        timestamp: new Date(),
        extractedData: extractedData
      };
      
      addMessage(assistantMessage);
      
      // Vérifier si nous devons changer d'agent
      checkAndSwitchAgentIfNeeded();
      
    } catch (error) {
      console.error('Erreur lors de la communication avec l\'API:', error);
      
      // Ajouter un message d'erreur
      const errorMessage: Message = {
        id: generateUUID(),
        content: "Désolé, j'ai rencontré une erreur technique. Vos informations ont été sauvegardées localement. Vous pouvez continuer ou rafraîchir la page si le problème persiste.",
        sender: 'system',
        timestamp: new Date()
      };
      
      addMessage(errorMessage);
      
      // Sauvegarder les données actuelles dans localStorage pour ne pas perdre la progression
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
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const getAgentIcon = () => {
    switch (currentAgentType) {
      case 'profile':
        return <Home />;
      case 'consumption':
        return <Bolt />;
      case 'property':
        return <Business />;
      default:
        return <Home />;
    }
  };
  
  return (
    <Paper 
      elevation={3} 
      sx={{ 
        height: '70vh', 
        display: 'flex', 
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        bgcolor: theme.palette.primary.main, 
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {getAgentIcon()}
          <Typography variant="h6" sx={{ ml: 1 }}>
            Assistant d'Audit DynamoPro - {
              currentAgentType === 'profile' ? 'Profil' : 
              currentAgentType === 'consumption' ? 'Consommation' : 'Propriété'
            }
          </Typography>
        </Box>
        <Box>
          <Chip 
            label={isRecording ? 'Enregistrement...' : 'Prêt'} 
            color={isRecording ? 'error' : 'success'} 
            size="small" 
          />
        </Box>
      </Box>
      
      {/* Messages Area */}
      <Box sx={{ 
        flexGrow: 1, 
        overflow: 'auto', 
        p: 2,
        bgcolor: theme.palette.background.default
      }}>
        <List>
          {messages.map((message) => (
            <ListItem 
              key={message.id} 
              sx={{ 
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Card 
                sx={{ 
                  maxWidth: '80%',
                  bgcolor: message.sender === 'user' 
                    ? theme.palette.primary.light 
                    : theme.palette.background.paper,
                  color: message.sender === 'user' 
                    ? theme.palette.primary.contrastText 
                    : theme.palette.text.primary
                }}
              >
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
                            <Chip 
                              size="small" 
                              label={`${key}: ${value}`} 
                              variant="outlined" 
                            />
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
      </Box>
      
      {/* Input Area */}
      <Box sx={{ 
        p: 2, 
        bgcolor: theme.palette.background.paper,
        borderTop: `1px solid ${theme.palette.divider}`
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Tapez votre message ou parlez..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            size="small"
            disabled={isProcessing}
            sx={{ mr: 1 }}
            inputRef={inputRef}
          />
          <Tooltip title={isRecording ? "Arrêter l'enregistrement" : "Commencer à parler"}>
            <IconButton 
              color={isRecording ? "error" : "primary"} 
              onClick={toggleRecording}
              disabled={isProcessing}
            >
              {isRecording ? <MicOff /> : <Mic />}
            </IconButton>
          </Tooltip>
          <IconButton 
            color="primary" 
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isProcessing}
          >
            <Send />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default VoiceAuditAssistant;

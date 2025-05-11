import React, { useState, useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { v4 as uuidv4 } from 'uuid';
import { updateProfile } from '../../store/slices/profileSlice';
import { Box, TextField, IconButton, Typography, Paper, Avatar, useTheme, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import SendIcon from '@mui/icons-material/Send';

interface UnifiedVoiceAssistantProps {
  userId: string;
  onAuditComplete?: (auditData: AuditData) => void;
}

interface AuditData {
  auditId: string;
  userId: string;
  timestamp: number;
  region?: string;
  situationPersonnelle?: string;
  habitation?: {
    type?: string;
    superficie?: number;
    anneeConstruction?: number;
    niveauEnergetique?: string;
  };
  energie?: {
    chauffage?: string;
    electricite?: {
      consommation?: number;
      fournisseur?: string;
    };
    gaz?: {
      consommation?: number;
      fournisseur?: string;
    };
  };
}

interface Message {
  role: 'system' | 'assistant' | 'user';
  content: string;
}

interface ChatMessage extends Message {
  id: string;
  timestamp: Date;
}

interface ConversationCheck {
  complete: boolean;
  data?: Record<string, any>;
}

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

const SYSTEM_PROMPT = `Tu es un assistant vocal dédié aux audits énergétiques pour DynamoPro. Tu dois collecter des informations essentielles pour effectuer un audit énergétique complet. Recueille les informations sur le profil de l'utilisateur, sa consommation d'énergie et son logement en une seule conversation fluide. Voici les informations que tu dois collecter (pas nécessairement dans cet ordre) : 1. Région en Belgique 2. Situation personnelle (propriétaire/locataire, taille du ménage) 3. Type d'habitation (appartement, maison, etc.) 4. Superficie approximative en m² 5. Année de construction 6. Niveau énergétique actuel (si connu) 7. Type de chauffage 8. Consommation d'électricité annuelle 9. Fournisseur d'électricité 10. Consommation de gaz annuelle (si applicable) 11. Fournisseur de gaz (si applicable) Adapte tes questions en fonction des réponses déjà fournies. Évite de poser des questions sur des informations déjà communiquées. Important: Après avoir collecté les informations essentielles, indique que l'audit est complet. Résume les informations collectées sous forme de JSON structuré à la fin de ta réponse finale, entre accolades {}.`;

const WELCOME_MESSAGE = `Bonjour! Je suis votre assistant pour réaliser un audit énergétique personnalisé. Pour vous proposer les meilleures recommandations, j'aurai besoin de quelques informations sur votre situation et votre logement. Pourriez-vous me parler de votre logement, de sa localisation en Belgique et de votre situation énergétique actuelle? Par exemple, vous pouvez me dire si vous êtes propriétaire ou locataire, dans quelle région vous habitez, quel type de logement vous avez, et comment vous vous chauffez. N'hésitez pas à me donner toutes les informations que vous jugez pertinentes. Je vous guiderai pour compléter l'audit.`;

const saveAuditDataToStorage = (auditData: AuditData): void => {
  try {
    localStorage.setItem('dynamopro_current_audit', JSON.stringify(auditData));
  } catch (error) {
    console.error("Erreur lors de la sauvegarde de l'audit:", error);
  }
};

const formatMessagesForAPI = (chatMessages: ChatMessage[]): Message[] =>
  chatMessages.map(({ role, content }) => ({ role, content }));

const callOpenAI = async (messages: Message[]): Promise<string> => {
  try {
    const response = await fetch('/api/proxy/openai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages,
        temperature: 0.7,
      }),
    });
    if (!response.ok) throw new Error(`Erreur API: ${response.status}`);
    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Erreur OpenAI:', error);
    return 'Désolé, je rencontre des difficultés techniques. Veuillez réessayer.';
  }
};

/**
 * Vérifie si la conversation contient suffisamment d'informations pour finaliser l'audit
 */
const checkIfAuditIsComplete = (chatMessages: ChatMessage[]): ConversationCheck => {
  for (let i = chatMessages.length - 1; i >= 0; i--) {
    const message = chatMessages[i];
    if (message.role === 'assistant') {
      const jsonMatch = message.content.match(/{[\s\S]*}/);
      if (jsonMatch) {
        try {
          const extractedData = JSON.parse(jsonMatch[0]);
          const hasMinimalInfo = extractedData.region && (extractedData.habitation?.type || extractedData.situationPersonnelle);
          if (hasMinimalInfo) {
            return { complete: true, data: extractedData };
          }
        } catch (e) {
          console.error("Erreur lors de l'analyse du JSON:", e);
        }
      }
    }
  }
  return { complete: false };
};

const UnifiedVoiceAssistant: React.FC<UnifiedVoiceAssistantProps> = ({ userId, onAuditComplete }) => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: uuidv4(),
    role: 'system',
    content: SYSTEM_PROMPT,
    timestamp: new Date()
  }, {
    id: uuidv4(),
    role: 'assistant',
    content: WELCOME_MESSAGE,
    timestamp: new Date()
  }]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [auditCompleted, setAuditCompleted] = useState(false);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  const [isSpeechRecognitionAvailable, setIsSpeechRecognitionAvailable] = useState(false);

  useEffect(() => {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      setIsSpeechRecognitionAvailable(true);
    }
    return () => {
      if (recognition) {
        recognition.onresult = null;
        recognition.onerror = null;
        recognition.stop();
      }
    };
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const initializeRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    const recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = false;
    recognitionInstance.lang = 'fr-FR';
    recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
      setTimeout(() => handleSendMessage(transcript), 500);
    };
    recognitionInstance.onerror = () => setIsRecording(false);
    return recognitionInstance;
  };

  const toggleRecording = () => {
    if (isRecording) {
      recognition?.stop();
      setIsRecording(false);
    } else {
      const recognitionInstance = recognition || initializeRecognition();
      if (recognitionInstance) {
        setRecognition(recognitionInstance);
        recognitionInstance.start();
        setIsRecording(true);
      }
    }
  };

  const handleSendMessage = async (text = inputText) => {
    if (!text.trim() || isProcessing || auditCompleted) return;
    setIsProcessing(true);
    setInputText('');
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    try {
      const formattedMessages = formatMessagesForAPI(updatedMessages);
      const response = await callOpenAI(formattedMessages);
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };
      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);
      const { complete, data } = checkIfAuditIsComplete(finalMessages);
      if (complete && data) {
        const finalAuditData: AuditData = {
          auditId: uuidv4(),
          userId,
          timestamp: Date.now(),
          ...data
        };
        saveAuditDataToStorage(finalAuditData);
        dispatch(updateProfile({ auditData: finalAuditData }));
        setAuditCompleted(true);
        if (onAuditComplete) onAuditComplete(finalAuditData);
        setMessages(prev => [...prev, {
          id: uuidv4(),
          role: 'assistant',
          content: "Merci ! J'ai terminé de collecter les informations pour votre audit énergétique. Je vais maintenant générer des recommandations personnalisées.",
          timestamp: new Date(),
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: uuidv4(),
        role: 'assistant',
        content: "Désolé, une erreur est survenue. Veuillez réessayer.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', my: 2 }}>
      <Paper elevation={3} sx={{ p: 2, minHeight: 400, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ flex: 1, overflowY: 'auto', mb: 2 }}>
          {messages.map(msg => (
            <Box key={msg.id} display="flex" justifyContent={msg.role === 'user' ? 'flex-end' : 'flex-start'} mb={1}>
              {msg.role !== 'user' && <Avatar sx={{ mr: 1, bgcolor: theme.palette.primary.main }}>🤖</Avatar>}
              <Box sx={{ bgcolor: msg.role === 'user' ? theme.palette.grey[200] : theme.palette.primary.light, color: msg.role === 'user' ? 'black' : 'white', borderRadius: 2, p: 1.5, maxWidth: 400 }}>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>{msg.content}</Typography>
              </Box>
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <TextField
            fullWidth
            disabled={isProcessing || auditCompleted}
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') handleSendMessage();
            }}
            placeholder={auditCompleted ? 'Audit terminé.' : 'Votre réponse...'}
          />
          {isSpeechRecognitionAvailable && (
            <IconButton color={isRecording ? 'secondary' : 'primary'} onClick={toggleRecording} disabled={isProcessing || auditCompleted}>
              <MicIcon />
            </IconButton>
          )}
          <IconButton color="primary" onClick={() => handleSendMessage()} disabled={isProcessing || !inputText.trim() || auditCompleted}>
            {isProcessing ? <CircularProgress size={24} /> : <SendIcon />}
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};

export default UnifiedVoiceAssistant;

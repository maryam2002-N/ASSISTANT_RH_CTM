import { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/apiService';
import { useChatHistory } from '../hooks/useChatHistory';

const ChatContext = createContext({
  messages: [],
  chatHistory: [],
  currentChatId: null,
  isTyping: false,
  loading: false,
  error: null,
  stats: null,
  sendMessage: () => {},
  startNewChat: () => {},
  loadChat: () => {},
  fetchChatHistory: () => {},
  updateChatTitle: () => {},
  deleteChat: () => {},
});

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat doit être utilisé dans un ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  // Utiliser le hook d'historique persistant
  const {
    sessions: chatHistory,
    loading,
    error,
    stats,
    loadSessions,
    loadSessionMessages,
    deleteSession,
    updateSessionTitle,
    refreshAfterNewMessage,
    clearError
  } = useChatHistory();

  const sendMessage = async (content) => {
    const userMessage = {
      id: Date.now(),
      content,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    clearError();

    try {
      // Appel à l'API Python backend
      const response = await apiService.sendMessage(content, currentChatId);
      
      const aiMessage = {
        id: Date.now() + 1,
        content: response.response,
        sender: 'ai',
        timestamp: response.timestamp,
      };
      
      setMessages(prev => [...prev, aiMessage]);

      // Gérer la session
      const sessionId = response.chat_id;
      
      if (!currentChatId) {
        // Nouvelle conversation
        setCurrentChatId(sessionId);
      }

      // Mettre à jour l'historique local avec les nouvelles données
      refreshAfterNewMessage(sessionId, content, response.response);

    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      
      // Message d'erreur à afficher à l'utilisateur
      const errorMessage = {
        id: Date.now() + 1,
        content: `Désolé, une erreur s'est produite: ${error.message}. 

**Vérifications à effectuer :**
1. Le serveur backend Python est-il démarré ? (python api_server.py)
2. L'API est-elle accessible sur http://localhost:8000 ?
3. Votre agent Python fonctionne-t-il correctement ?

Vous pouvez tester l'API en visitant http://localhost:8000/docs`,
        sender: 'ai',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setCurrentChatId(null);
  };

  const loadChat = async (chatId) => {
    try {
      console.log('Chargement du chat:', chatId);
      setCurrentChatId(chatId);
      
      // Charger les messages depuis l'historique persistant
      const messages = await loadSessionMessages(chatId);
      setMessages(messages);
      
    } catch (error) {
      console.error('Erreur lors du chargement du chat:', error);
      // En cas d'erreur, afficher un message d'erreur
      const errorMessage = {
        id: Date.now(),
        content: 'Impossible de charger cette conversation. Elle a peut-être été supprimée.',
        sender: 'ai',
        timestamp: new Date().toISOString(),
      };
      setMessages([errorMessage]);
    }
  };

  const fetchChatHistory = async () => {
    try {
      await loadSessions();
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
    }
  };

  const updateChatTitle = async (chatId, newTitle) => {
    const success = await updateSessionTitle(chatId, newTitle);
    return success;
  };

  const deleteChat = async (chatId) => {
    const success = await deleteSession(chatId);
    if (success && currentChatId === chatId) {
      startNewChat();
    }
    return success;
  };

  // Recharger l'historique quand l'utilisateur se connecte
  useEffect(() => {
    if (apiService.isAuthenticated()) {
      fetchChatHistory();
    }
  }, []);

  return (
    <ChatContext.Provider value={{
      messages,
      chatHistory,
      currentChatId,
      isTyping,
      loading,
      error,
      stats,
      sendMessage,
      startNewChat,
      loadChat,
      fetchChatHistory,
      updateChatTitle,
      deleteChat,
    }}>
      {children}
    </ChatContext.Provider>
  );
};

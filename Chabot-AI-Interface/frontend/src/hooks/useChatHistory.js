import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/apiService';

/**
 * Hook personnalisé pour gérer l'historique persistant des conversations
 */
export const useChatHistory = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  // Charger l'historique des sessions
  const loadSessions = useCallback(async (limit = 50) => {
    if (!apiService.isAuthenticated()) {
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getChatHistory(limit);
      
      // Transformer les données pour correspondre au format attendu par le sidebar
      const transformedSessions = response.sessions.map(session => ({
        id: session.session_id,
        title: session.title,
        createdAt: session.created_at,
        lastMessage: {
          content: session.last_message || '',
          timestamp: session.updated_at || session.created_at
        },
        messageCount: session.message_count,
        // Données supplémentaires pour la gestion
        session_id: session.session_id,
        user_id: session.user_id,
        updated_at: session.updated_at
      }));

      setSessions(transformedSessions);
    } catch (err) {
      console.error('Erreur lors du chargement de l\'historique:', err);
      setError('Impossible de charger l\'historique des conversations');
    } finally {
      setLoading(false);
    }
  }, []);

  // Charger les messages d'une session
  const loadSessionMessages = useCallback(async (sessionId) => {
    try {
      const response = await apiService.getSessionMessages(sessionId);
      
      // Transformer les messages pour correspondre au format attendu
      const transformedMessages = response.messages
        .filter(msg => msg.role !== 'system') // Exclure les messages système
        .map((msg, index) => ({
          id: Date.now() + index,
          content: msg.content,
          sender: msg.role === 'user' ? 'user' : 'ai',
          timestamp: msg.timestamp,
        }));

      return transformedMessages;
    } catch (err) {
      console.error('Erreur lors du chargement des messages:', err);
      throw new Error('Impossible de charger les messages de la conversation');
    }
  }, []);

  // Supprimer une session
  const deleteSession = useCallback(async (sessionId) => {
    try {
      await apiService.deleteSession(sessionId);
      setSessions(prev => prev.filter(session => session.id !== sessionId));
      return true;
    } catch (err) {
      console.error('Erreur lors de la suppression:', err);
      setError('Impossible de supprimer la conversation');
      return false;
    }
  }, []);

  // Mettre à jour le titre d'une session
  const updateSessionTitle = useCallback(async (sessionId, newTitle) => {
    try {
      await apiService.updateSessionTitle(sessionId, newTitle);
      setSessions(prev => 
        prev.map(session => 
          session.id === sessionId 
            ? { ...session, title: newTitle }
            : session
        )
      );
      return true;
    } catch (err) {
      console.error('Erreur lors de la mise à jour du titre:', err);
      setError('Impossible de mettre à jour le titre');
      return false;
    }
  }, []);

  // Charger les statistiques
  const loadStats = useCallback(async () => {
    try {
      const response = await apiService.getChatStats();
      setStats(response.stats);
    } catch (err) {
      console.error('Erreur lors du chargement des statistiques:', err);
    }
  }, []);

  // Actualiser l'historique après un nouveau message
  const refreshAfterNewMessage = useCallback((chatId, userMessage, aiResponse) => {
    setSessions(prev => {
      const existingSession = prev.find(session => session.id === chatId);
      
      if (existingSession) {
        // Mettre à jour la session existante
        return prev.map(session => 
          session.id === chatId 
            ? {
                ...session,
                lastMessage: {
                  content: aiResponse,
                  timestamp: new Date().toISOString()
                },
                messageCount: session.messageCount + 2 // +1 pour user, +1 pour AI
              }
            : session
        );
      } else {
        // Ajouter une nouvelle session
        const newSession = {
          id: chatId,
          title: userMessage.length > 50 ? userMessage.substring(0, 50) + '...' : userMessage,
          createdAt: new Date().toISOString(),
          lastMessage: {
            content: aiResponse,
            timestamp: new Date().toISOString()
          },
          messageCount: 2,
          session_id: chatId,
          user_id: null,
          updated_at: new Date().toISOString()
        };
        
        return [newSession, ...prev];
      }
    });
  }, []);

  // Charger l'historique au montage du composant
  useEffect(() => {
    if (apiService.isAuthenticated()) {
      loadSessions();
      loadStats();
    }
  }, [loadSessions, loadStats]);

  return {
    sessions,
    loading,
    error,
    stats,
    loadSessions,
    loadSessionMessages,
    deleteSession,
    updateSessionTitle,
    loadStats,
    refreshAfterNewMessage,
    clearError: () => setError(null)
  };
};

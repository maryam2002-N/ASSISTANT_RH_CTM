// ChatHistoryExample.tsx
// Exemple complet d'intégration de l'historique des conversations
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Types TypeScript
interface ChatSession {
  session_id: string;
  user_id: string | null;
  title: string;
  created_at: string;
  updated_at: string | null;
  message_count: number;
  last_message: string | null;
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

interface ChatHistoryProps {
  token: string; // Token d'authentification
  onSessionSelect: (sessionId: string | null) => void;
}

// Configuration API
const API_BASE_URL = 'http://localhost:8000';

// Service API
class ChatHistoryService {
  private token: string;
  
  constructor(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async getSessions(limit = 50): Promise<ChatSession[]> {
    const response = await axios.get(`${API_BASE_URL}/api/chat/history?limit=${limit}`, {
      headers: this.getHeaders()
    });
    return response.data.sessions;
  }

  async getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
    const response = await axios.get(`${API_BASE_URL}/api/chat/session/${sessionId}/messages`, {
      headers: this.getHeaders()
    });
    return response.data.messages;
  }

  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      await axios.delete(`${API_BASE_URL}/api/chat/session/${sessionId}`, {
        headers: this.getHeaders()
      });
      return true;
    } catch (error) {
      console.error('Error deleting session:', error);
      return false;
    }
  }

  async updateSessionTitle(sessionId: string, title: string): Promise<boolean> {
    try {
      await axios.put(`${API_BASE_URL}/api/chat/session/${sessionId}/title`, 
        { title }, 
        { headers: this.getHeaders() }
      );
      return true;
    } catch (error) {
      console.error('Error updating session title:', error);
      return false;
    }
  }

  async getStats() {
    const response = await axios.get(`${API_BASE_URL}/api/chat/stats`, {
      headers: this.getHeaders()
    });
    return response.data.stats;
  }
}

// Hook personnalisé pour l'historique
const useChatHistory = (token: string) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [service] = useState(new ChatHistoryService(token));

  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const sessions = await service.getSessions();
      setSessions(sessions);
    } catch (err) {
      setError('Erreur lors du chargement de l\'historique');
      console.error('Error loading sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionId: string) => {
    const success = await service.deleteSession(sessionId);
    if (success) {
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
    }
    return success;
  };

  const updateSessionTitle = async (sessionId: string, title: string) => {
    const success = await service.updateSessionTitle(sessionId, title);
    if (success) {
      setSessions(prev => 
        prev.map(s => s.session_id === sessionId ? { ...s, title } : s)
      );
    }
    return success;
  };

  useEffect(() => {
    loadSessions();
  }, []);

  return {
    sessions,
    loading,
    error,
    loadSessions,
    deleteSession,
    updateSessionTitle,
    getSessionMessages: service.getSessionMessages.bind(service),
    getStats: service.getStats.bind(service)
  };
};

// Composant d'élément de session
const SessionItem: React.FC<{
  session: ChatSession;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
  onTitleUpdate: (title: string) => void;
}> = ({ session, isActive, onClick, onDelete, onTitleUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(session.title);

  const handleSaveTitle = () => {
    if (editTitle.trim() && editTitle !== session.title) {
      onTitleUpdate(editTitle.trim());
    }
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Aujourd\'hui';
    if (diffDays === 2) return 'Hier';
    if (diffDays <= 7) return `Il y a ${diffDays} jours`;
    return date.toLocaleDateString('fr-FR');
  };

  return (
    <div className={`session-item ${isActive ? 'active' : ''}`}>
      <div className="session-content" onClick={onClick}>
        {isEditing ? (
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={handleSaveTitle}
            onKeyPress={(e) => e.key === 'Enter' && handleSaveTitle()}
            className="session-title-input"
            autoFocus
          />
        ) : (
          <>
            <div className="session-title">{session.title}</div>
            <div className="session-meta">
              <span className="message-count">{session.message_count} messages</span>
              <span className="session-date">{formatDate(session.created_at)}</span>
            </div>
            {session.last_message && (
              <div className="session-preview">
                {session.last_message.substring(0, 60)}...
              </div>
            )}
          </>
        )}
      </div>
      
      <div className="session-actions">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsEditing(true);
          }}
          className="edit-btn"
          title="Renommer"
        >
          ✏️
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (window.confirm('Supprimer cette conversation ?')) {
              onDelete();
            }
          }}
          className="delete-btn"
          title="Supprimer"
        >
          🗑️
        </button>
      </div>
    </div>
  );
};

// Composant principal de l'historique
const ChatHistorySidebar: React.FC<ChatHistoryProps> = ({ token, onSessionSelect }) => {
  const {
    sessions,
    loading,
    error,
    loadSessions,
    deleteSession,
    updateSessionTitle,
    getStats
  } = useChatHistory(token);

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    // Charger les statistiques
    getStats().then(setStats).catch(console.error);
  }, []);

  const handleSessionSelect = (sessionId: string) => {
    setActiveSessionId(sessionId);
    onSessionSelect(sessionId);
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    onSessionSelect(null);
  };

  if (loading) {
    return (
      <div className="chat-history-sidebar loading">
        <div className="loading-spinner">Chargement de l'historique...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chat-history-sidebar error">
        <div className="error-message">{error}</div>
        <button onClick={loadSessions} className="retry-btn">
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div className="chat-history-sidebar">
      {/* En-tête */}
      <div className="sidebar-header">
        <h3>Historique des conversations</h3>
        <button onClick={handleNewChat} className="new-chat-btn">
          ➕ Nouvelle conversation
        </button>
      </div>

      {/* Statistiques */}
      {stats && (
        <div className="sidebar-stats">
          <div className="stat">
            <span className="stat-value">{stats.total_sessions}</span>
            <span className="stat-label">Conversations</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.recent_sessions}</span>
            <span className="stat-label">Récentes</span>
          </div>
        </div>
      )}

      {/* Liste des sessions */}
      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div className="no-sessions">
            <p>Aucune conversation trouvée.</p>
            <button onClick={handleNewChat} className="start-chat-btn">
              Commencer une conversation
            </button>
          </div>
        ) : (
          sessions.map((session) => (
            <SessionItem
              key={session.session_id}
              session={session}
              isActive={activeSessionId === session.session_id}
              onClick={() => handleSessionSelect(session.session_id)}
              onDelete={() => deleteSession(session.session_id)}
              onTitleUpdate={(title) => updateSessionTitle(session.session_id, title)}
            />
          ))
        )}
      </div>

      {/* Bouton actualiser */}
      <div className="sidebar-footer">
        <button onClick={loadSessions} className="refresh-btn">
          🔄 Actualiser
        </button>
      </div>
    </div>
  );
};

// CSS intégré (dans un vrai projet, utilisez des fichiers CSS séparés)
const styles = `
.chat-history-sidebar {
  width: 320px;
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.sidebar-header h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #495057;
}

.new-chat-btn {
  width: 100%;
  padding: 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.new-chat-btn:hover {
  background: #0056b3;
}

.sidebar-stats {
  display: flex;
  padding: 1rem;
  gap: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.stat {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #007bff;
}

.stat-label {
  font-size: 0.8rem;
  color: #6c757d;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.session-item {
  display: flex;
  margin-bottom: 0.5rem;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.session-item:hover {
  border-color: #007bff;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.session-item.active {
  background: #e3f2fd;
  border-color: #007bff;
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-title-input {
  width: 100%;
  border: 1px solid #007bff;
  border-radius: 0.25rem;
  padding: 0.25rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.session-preview {
  font-size: 0.85rem;
  color: #6c757d;
  line-height: 1.3;
}

.session-actions {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.edit-btn, .delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

.edit-btn:hover, .delete-btn:hover {
  background: rgba(0,0,0,0.1);
}

.no-sessions {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.start-chat-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  margin-top: 1rem;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
}

.refresh-btn {
  width: 100%;
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
}

.loading-spinner {
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  text-align: center;
  margin-bottom: 1rem;
}

.retry-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
}
`;

// Exemple d'utilisation
const ChatApp: React.FC = () => {
  const [token, setToken] = useState<string>('your-auth-token-here');
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <style>{styles}</style>
      
      <ChatHistorySidebar 
        token={token}
        onSessionSelect={setSelectedSessionId}
      />
      
      <div style={{ flex: 1, padding: '2rem' }}>
        <h2>Interface de Chat</h2>
        {selectedSessionId ? (
          <p>Session sélectionnée: {selectedSessionId}</p>
        ) : (
          <p>Nouvelle conversation</p>
        )}
        {/* Ici viendrait votre composant de chat principal */}
      </div>
    </div>
  );
};

export default ChatApp;

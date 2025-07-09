import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from './ui/dialog';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { History, MessageSquare, Trash2, Eye, Calendar, User } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

const ChatHistory = ({ onLoadConversation }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionMessages, setSessionMessages] = useState([]);
  const [viewingSession, setViewingSession] = useState(false);

  const fetchChatHistory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/chat/history', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      } else {
        console.error('Erreur lors de la récupération de l\'historique');
      }
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionMessages = async (sessionId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/chat/session/${sessionId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSessionMessages(data.messages || []);
        setViewingSession(true);
      } else {
        console.error('Erreur lors de la récupération des messages');
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/chat/session/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setSessions(sessions.filter(s => s.session_id !== sessionId));
        if (selectedSession?.session_id === sessionId) {
          setSelectedSession(null);
          setViewingSession(false);
        }
      } else {
        console.error('Erreur lors de la suppression de la session');
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const loadConversation = (session) => {
    if (onLoadConversation) {
      onLoadConversation(session.session_id);
    }
    setIsOpen(false);
  };

  useEffect(() => {
    if (isOpen) {
      fetchChatHistory();
    }
  }, [isOpen]);

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true, locale: fr });
    } catch {
      return 'Date inconnue';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center gap-2">
          <History className="h-4 w-4" />
          Historique
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Historique des conversations
          </DialogTitle>
        </DialogHeader>

        {!viewingSession ? (
          <div className="flex-1 overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Aucune conversation trouvée</p>
                <p className="text-sm">Commencez une nouvelle conversation pour voir l'historique</p>
              </div>
            ) : (
              <ScrollArea className="h-full">
                <div className="space-y-3 p-1">
                  {sessions.map((session) => (
                    <div
                      key={session.session_id}
                      className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-medium text-sm line-clamp-2 flex-1">
                          {session.title}
                        </h3>
                        <div className="flex items-center gap-1 ml-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedSession(session);
                              fetchSessionMessages(session.session_id);
                            }}
                            className="h-8 w-8 p-0"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteSession(session.session_id)}
                            className="h-8 w-8 p-0 text-red-500 hover:text-red-600"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(session.created_at)}
                        </span>
                        <span className="flex items-center gap-1">
                          <MessageSquare className="h-3 w-3" />
                          {session.message_count} messages
                        </span>
                      </div>

                      {session.last_message && (
                        <p className="text-xs text-gray-600 line-clamp-2 mb-3">
                          {session.last_message}
                        </p>
                      )}

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => loadConversation(session)}
                        className="w-full"
                      >
                        Reprendre la conversation
                      </Button>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-medium">{selectedSession?.title}</h3>
                <p className="text-sm text-gray-500">
                  {selectedSession?.message_count} messages • {formatDate(selectedSession?.created_at)}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setViewingSession(false)}
              >
                Retour
              </Button>
            </div>

            <ScrollArea className="flex-1 border rounded-lg p-4">
              <div className="space-y-4">
                {sessionMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p className="text-xs mt-1 opacity-70">
                        {formatDate(message.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            <div className="mt-4 flex gap-2">
              <Button
                variant="outline"
                onClick={() => loadConversation(selectedSession)}
                className="flex-1"
              >
                Reprendre cette conversation
              </Button>
              <Button
                variant="outline"
                onClick={() => deleteSession(selectedSession.session_id)}
                className="text-red-500 hover:text-red-600"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ChatHistory;

import React, { useState, useEffect } from 'react';
import ChatHistory from './ChatHistory';
import WelcomePage from './WelcomePage';
import { useChatHistory } from '../hooks/useChatHistory';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Send, History, Plus, User, LogOut } from 'lucide-react';

const ChatInterface = ({ user, onLogout, initialChatSession }) => {
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { sessions, loadSessions, loadSessionMessages } = useChatHistory();

  // Initialiser avec la session de bienvenue si elle existe
  useEffect(() => {
    if (initialChatSession) {
      setCurrentSessionId(initialChatSession.chat_id);
      setMessages([{
        role: 'assistant',
        content: initialChatSession.welcome_message,
        timestamp: initialChatSession.timestamp
      }]);
      
      // Nettoyer le localStorage après utilisation
      localStorage.removeItem('current_chat_id');
      localStorage.removeItem('welcome_message');
    }
    
    loadSessions();
  }, [initialChatSession]);

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    setIsLoading(true);
    const userMessage = { role: 'user', content: message, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/chat/message', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message,
          chat_id: currentSessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, assistantMessage]);
        
        // Mettre à jour l'ID de session si c'est une nouvelle conversation
        if (!currentSessionId) {
          setCurrentSessionId(data.chat_id);
        }
        
        // Recharger les sessions pour mettre à jour l'historique
        loadSessions();
      }
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadConversation = async (sessionId) => {
    try {
      const sessionMessages = await loadSessionMessages(sessionId);
      setMessages(sessionMessages);
      setCurrentSessionId(sessionId);
    } catch (error) {
      console.error('Erreur lors du chargement de la conversation:', error);
    }
  };

  const startNewConversation = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/chat/new-session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSessionId(data.chat_id);
        setMessages([{
          role: 'assistant',
          content: data.welcome_message,
          timestamp: data.timestamp
        }]);
        
        // Recharger les sessions pour inclure la nouvelle
        loadSessions();
      }
    } catch (error) {
      console.error('Erreur lors de la création d\'une nouvelle conversation:', error);
      // Fallback: créer une conversation locale
      setCurrentSessionId(null);
      setMessages([]);
    }
  };

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar avec historique */}
      <div className="w-80 border-r bg-white flex flex-col">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Agent RH CTM</h1>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex gap-2">
            <Button 
              onClick={startNewConversation}
              className="flex-1"
              variant="outline"
            >
              <Plus className="h-4 w-4 mr-2" />
              Nouvelle conversation
            </Button>
            <ChatHistory onLoadConversation={loadConversation} />
          </div>
        </div>

        {/* Liste des sessions récentes */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-2">
            {sessions.slice(0, 10).map((session) => (
              <div
                key={session.session_id}
                onClick={() => loadConversation(session.session_id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSessionId === session.session_id
                    ? 'bg-blue-50 border-blue-200 border'
                    : 'hover:bg-gray-50'
                }`}
              >
                <h3 className="font-medium text-sm line-clamp-1">{session.title}</h3>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(session.created_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Zone de chat principale */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">
                  <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <h2 className="text-xl font-semibold mb-2">Bienvenue sur l'Agent RH CTM</h2>
                  <p>Commencez une nouvelle conversation ou reprenez une conversation existante.</p>
                </div>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white shadow-sm border'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs mt-2 opacity-70">
                      {new Date(message.timestamp).toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Zone de saisie */}
        <div className="border-t bg-white p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Tapez votre message..."
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage(inputMessage)}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={() => sendMessage(inputMessage)}
                disabled={isLoading || !inputMessage.trim()}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { 
  Menu,
  Bot,
  Sparkles,
  Zap
} from 'lucide-react';
import { useChat } from '../contexts/ChatContext';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../components/ToastProvider';
import ChatSidebar from '../components/ChatSidebar';
import ChatMessage from '../components/ChatMessage';
import MessageInput from '../components/MessageInput';

const Chat = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);
  
  const { 
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
    deleteChat  
  } = useChat();
  const { user } = useAuth();
  const { theme } = useTheme();
  const { toast } = useToast();

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    fetchChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    const handleResize = () => {
      setSidebarOpen(window.innerWidth >= 768);
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Memoized handlers for better performance
  const handleSendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || isTyping) return;
    await sendMessage(messageText);
  }, [sendMessage, isTyping]);

  const handleNewChat = useCallback(() => {
    startNewChat();
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  }, [startNewChat]);

  const handleLoadChat = useCallback((chatId) => {
    loadChat(chatId);
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  }, [loadChat]);

  const handleMessageCopy = useCallback((messageId) => {
    toast.success('Message copied to clipboard!');
  }, [toast]);

  const handleMessageFeedback = useCallback((messageId, feedbackType) => {
    const feedbackMessages = {
      like: 'Thanks for your feedback! 👍',
      dislike: 'Thanks for your feedback. We\'ll work to improve! 👎'
    };
    
    toast.info(feedbackMessages[feedbackType] || 'Feedback received');
  }, [toast]);
  // Memoized suggested prompts
  const suggestedPrompts = useMemo(() => [
    {
      icon: <Sparkles className="w-4 h-4" />,
      text: "Comment pouvez-vous m'aider aujourd'hui ?",
      description: "Découvrez les capacités de l'IA"
    },
    {
      icon: <Bot className="w-4 h-4" />,
      text: "Expliquez-moi les politiques RH",
      description: "Obtenez des explications détaillées"
    },
    {
      icon: <Zap className="w-4 h-4" />,
      text: "Aidez-moi à planifier un projet",
      description: "Assistance pour la planification"
    },
    {
      icon: <Sparkles className="w-4 h-4" />,
      text: "Rédigez un email professionnel",
      description: "Aide à la création de contenu"
    }
  ], []);

  const handlePromptClick = useCallback((promptText) => {
    handleSendMessage(promptText);
  }, [handleSendMessage]);

  return (
    <div className="main-layout">
      {/* Sidebar */}
      <ChatSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chatHistory={chatHistory}
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onLoadChat={handleLoadChat}
        onEditChat={updateChatTitle}
        onDeleteChat={deleteChat}
        loading={loading}
        error={error}
        stats={stats}
        onRefresh={fetchChatHistory}
      />

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed"
          style={{
            position: 'fixed',
            top: '0',
            right: '0',
            bottom: '0',
            left: '0',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: '30',
            display: window.innerWidth < 768 ? 'block' : 'none'
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div 
        className="flex-1 flex flex-col"
        style={{ 
          marginLeft: sidebarOpen && window.innerWidth >= 768 ? '280px' : '0',
          transition: 'margin-left 0.3s ease'
        }}
      >
        {/* Chat Header */}
        <div className="chat-header">
          <div className="chat-header-content">
            <button
              onClick={() => setSidebarOpen(true)}
              className="chat-header-menu-button"
              style={{
                display: window.innerWidth < 768 ? 'block' : 'none'
              }}
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            
            <div className="flex items-center gap-3">
              <div className="chat-header-avatar">
                <Bot className="w-4 h-4 text-white" />
              </div>
              
              <div className="chat-header-info">
                <h1 className="chat-header-title">AI Assistant</h1>
                <p className="chat-header-subtitle">Powered by advanced AI</p>
              </div>
            </div>
            
            <div className="chat-header-status">
              <div className="chat-status-dot"></div>
              <span className="chat-status-text">Online</span>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="chat-messages scrollbar-thin">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-content">
                <div className="welcome-icon">
                  <Bot className="w-10 h-10 text-white" />
                </div>
                  <h3 className="welcome-title">Bienvenue dans l'Assistant IA RH</h3>
                <p className="welcome-description">
                  Commencez une conversation avec notre assistant IA. Posez des questions, obtenez de l'aide ou explorez de nouvelles idées !
                </p>
                
                <div className="suggested-prompts">
                  {suggestedPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handlePromptClick(prompt.text)}
                      className="prompt-button"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="prompt-icon">
                        {prompt.icon}
                      </div>
                      <div>
                        <p className="prompt-text">{prompt.text}</p>
                        <p className="prompt-description">{prompt.description}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4">
              {messages.map((msg, index) => (
                <div
                  key={msg.id}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <ChatMessage
                    message={msg}
                    onCopy={handleMessageCopy}
                    onFeedback={handleMessageFeedback}
                  />
                </div>
              ))}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div className="typing-indicator">
                  <div className="message-avatar message-avatar-ai">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="typing-bubble">
                    <div className="typing-dots">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Input */}
        <MessageInput
          onSend={handleSendMessage}
          isTyping={isTyping}
          disabled={false}
          placeholder="Type your message..."
          showAttachments={true}
          showVoice={true}
          showEmoji={true}
          maxLength={4000}
        />
      </div>
    </div>
  );
};

export default Chat;
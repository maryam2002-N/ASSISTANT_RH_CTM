import { useState, memo, useCallback } from 'react';
import { Bot, User as UserIcon, Copy, Check, ThumbsUp, ThumbsDown } from 'lucide-react';
import MessageFormatter from './MessageFormatter';

const ChatMessage = memo(({ message, onCopy, onFeedback }) => {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null);
  
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onCopy?.(message.id);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  }, [message.content, message.id, onCopy]);

  const handleFeedback = useCallback((type) => {
    setFeedback(type);
    onFeedback?.(message.id, type);
  }, [message.id, onFeedback]);
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`message-container ${message.sender === 'user' ? 'message-container-user' : ''}`}>
      {message.sender === 'ai' && (
        <div className="message-avatar message-avatar-ai">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className="message-content">
        <div className={`message-bubble ${message.sender === 'user' ? 'message-bubble-user' : 'message-bubble-ai'}`}>
          {message.sender === 'ai' ? (
            <MessageFormatter content={message.content} />
          ) : (
            <p className="message-text">{message.content}</p>
          )}
          
          {/* Message Actions for AI messages */}
          {message.sender === 'ai' && (
            <div className="message-actions">              <button
                onClick={handleCopy}
                className="message-action-button"
                title="Copier le message"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-green-600" />
                ) : (
                  <Copy className="w-3.5 h-3.5 text-gray-500" />
                )}
              </button>
                <button
                onClick={() => handleFeedback('like')}
                className={`message-action-button ${feedback === 'like' ? 'message-action-button-active' : ''}`}
                title="Bonne réponse"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              
              <button
                onClick={() => handleFeedback('dislike')}
                className={`message-action-button ${feedback === 'dislike' ? 'message-action-button-active-dislike' : ''}`}
                title="Mauvaise réponse"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
        
        <div className={`message-timestamp ${message.sender === 'user' ? 'message-timestamp-user' : ''}`}>          {formatTime(message.timestamp)}
          {copied && message.sender === 'ai' && (
            <span className="message-copy-feedback">Copié !</span>
          )}
        </div>
      </div>

      {message.sender === 'user' && (
        <div className="message-avatar message-avatar-user">
          <UserIcon className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
});

ChatMessage.displayName = 'ChatMessage';

export default ChatMessage;

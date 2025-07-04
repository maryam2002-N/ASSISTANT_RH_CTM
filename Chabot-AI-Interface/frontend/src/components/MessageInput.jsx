import { useState, useRef, useCallback, useEffect } from 'react';
import { Send, Paperclip, Mic, Smile } from 'lucide-react';

const MessageInput = ({
  onSend,
  isTyping = false,
  disabled = false,
  placeholder = "Tapez votre message...",
  showAttachments = false,
  showVoice = false,
  showEmoji = false,
  maxLength = 4000
}) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 128) + 'px';
    }
  }, []);

  useEffect(() => {
    adjustTextareaHeight();
  }, [message, adjustTextareaHeight]);

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (message.trim() && !isTyping && !disabled) {
      onSend(message.trim());
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  }, [message, isTyping, disabled, onSend]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleAttachment = useCallback(() => {
    // Placeholder for attachment functionality
    console.log('Attachment clicked');
  }, []);

  const handleVoice = useCallback(() => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      console.log('Voice recording stopped');
    } else {
      // Start recording
      setIsRecording(true);
      console.log('Voice recording started');
    }
  }, [isRecording]);

  const handleEmoji = useCallback(() => {
    // Placeholder for emoji picker
    console.log('Emoji picker clicked');
  }, []);

  const canSend = message.trim().length > 0 && !isTyping && !disabled;

  return (
    <div className="message-input-container">
      <div className="message-input-wrapper">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isTyping}
            maxLength={maxLength}
            className="message-input-field"
            rows={1}
          />
          
          <div className="message-input-actions">

              <button
              type="submit"
              disabled={!canSend}
              className={`message-input-button message-send-button ${!canSend ? 'opacity-50 cursor-not-allowed' : ''}`}
              title="Envoyer le message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
        
        {/* Character counter */}
        {message.length > maxLength * 0.8 && (
          <div className="absolute -top-6 right-0 text-xs text-gray-500">
            {message.length}/{maxLength}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageInput;

// Custom hook for input management with advanced features
import { useState, useCallback, useRef, useEffect } from 'react';

export const useMessageInput = ({ 
  onSend, 
  maxLength = 4000, 
  debounceDelay = 300,
  multiline = true 
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef(null);
  const debounceRef = useRef(null);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = Math.min(textarea.scrollHeight, 120); // Max height: 120px
      textarea.style.height = `${scrollHeight}px`;
    }
  }, []);

  // Handle message change with debouncing for auto-save
  const handleMessageChange = useCallback((value) => {
    setMessage(value);
    adjustTextareaHeight();

    // Clear previous debounce
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new debounce for auto-save or typing indicators
    debounceRef.current = setTimeout(() => {
      // Here you could add auto-save functionality or typing indicators
      console.log('Debounced input:', value);
    }, debounceDelay);
  }, [adjustTextareaHeight, debounceDelay]);

  // Handle key events
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      if (multiline && e.shiftKey) {
        // Allow new line with Shift+Enter
        return;
      }
      
      if (!isComposing && message.trim()) {
        e.preventDefault();
        onSend(message.trim());
        setMessage('');
        adjustTextareaHeight();
      }
    }
    
    if (e.key === 'Escape') {
      textareaRef.current?.blur();
    }
  }, [message, isComposing, onSend, multiline, adjustTextareaHeight]);

  // Handle composition events (for IME input)
  const handleCompositionStart = useCallback(() => {
    setIsComposing(true);
  }, []);

  const handleCompositionEnd = useCallback(() => {
    setIsComposing(false);
  }, []);

  // Handle focus events
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  // Submit message programmatically
  const submitMessage = useCallback(() => {
    if (message.trim()) {
      onSend(message.trim());
      setMessage('');
      adjustTextareaHeight();
    }
  }, [message, onSend, adjustTextareaHeight]);

  // Clear message
  const clearMessage = useCallback(() => {
    setMessage('');
    adjustTextareaHeight();
  }, [adjustTextareaHeight]);

  // Focus input
  const focusInput = useCallback(() => {
    textareaRef.current?.focus();
  }, []);

  // Insert text at cursor position
  const insertText = useCallback((text) => {
    const textarea = textareaRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newMessage = message.substring(0, start) + text + message.substring(end);
      
      if (newMessage.length <= maxLength) {
        setMessage(newMessage);
        
        // Restore cursor position
        setTimeout(() => {
          textarea.selectionStart = textarea.selectionEnd = start + text.length;
          textarea.focus();
        }, 0);
      }
    }
  }, [message, maxLength]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  // Computed values
  const characterCount = message.length;
  const isNearLimit = characterCount > maxLength * 0.8;
  const isOverLimit = characterCount > maxLength;
  const canSend = message.trim().length > 0 && !isOverLimit;

  return {
    // State
    message,
    isComposing,
    isFocused,
    characterCount,
    isNearLimit,
    isOverLimit,
    canSend,
    
    // Refs
    textareaRef,
    
    // Handlers
    handleMessageChange,
    handleKeyDown,
    handleCompositionStart,
    handleCompositionEnd,
    handleFocus,
    handleBlur,
    
    // Actions
    submitMessage,
    clearMessage,
    focusInput,
    insertText,
    
    // Utils
    adjustTextareaHeight
  };
};

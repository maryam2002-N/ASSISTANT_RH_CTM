// Chat state management hook with performance optimizations
import { useReducer, useCallback, useMemo } from 'react';

// Action types
const CHAT_ACTIONS = {
  SET_MESSAGES: 'SET_MESSAGES',
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_TYPING: 'SET_TYPING',
  SET_CURRENT_CHAT: 'SET_CURRENT_CHAT',
  UPDATE_LAST_MESSAGE: 'UPDATE_LAST_MESSAGE',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Initial state
const initialState = {
  messages: [],
  isTyping: false,
  currentChatId: null,
  error: null,
  lastMessageId: null
};

// Reducer function
const chatReducer = (state, action) => {
  switch (action.type) {
    case CHAT_ACTIONS.SET_MESSAGES:
      return {
        ...state,
        messages: action.payload,
        lastMessageId: action.payload[action.payload.length - 1]?.id || null
      };
      
    case CHAT_ACTIONS.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload],
        lastMessageId: action.payload.id
      };
      
    case CHAT_ACTIONS.SET_TYPING:
      return {
        ...state,
        isTyping: action.payload
      };
      
    case CHAT_ACTIONS.SET_CURRENT_CHAT:
      return {
        ...state,
        currentChatId: action.payload
      };
      
    case CHAT_ACTIONS.UPDATE_LAST_MESSAGE:
      return {
        ...state,
        messages: state.messages.map((msg, index) => 
          index === state.messages.length - 1 
            ? { ...msg, ...action.payload }
            : msg
        )
      };
      
    case CHAT_ACTIONS.CLEAR_MESSAGES:
      return {
        ...state,
        messages: [],
        currentChatId: null,
        lastMessageId: null
      };
      
    case CHAT_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isTyping: false
      };
      
    case CHAT_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
      
    default:
      return state;
  }
};

// Custom hook for chat state management
export const useChatState = () => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Memoized actions
  const actions = useMemo(() => ({
    setMessages: (messages) => dispatch({ type: CHAT_ACTIONS.SET_MESSAGES, payload: messages }),
    addMessage: (message) => dispatch({ type: CHAT_ACTIONS.ADD_MESSAGE, payload: message }),
    setTyping: (isTyping) => dispatch({ type: CHAT_ACTIONS.SET_TYPING, payload: isTyping }),
    setCurrentChat: (chatId) => dispatch({ type: CHAT_ACTIONS.SET_CURRENT_CHAT, payload: chatId }),
    updateLastMessage: (updates) => dispatch({ type: CHAT_ACTIONS.UPDATE_LAST_MESSAGE, payload: updates }),
    clearMessages: () => dispatch({ type: CHAT_ACTIONS.CLEAR_MESSAGES }),
    setError: (error) => dispatch({ type: CHAT_ACTIONS.SET_ERROR, payload: error }),
    clearError: () => dispatch({ type: CHAT_ACTIONS.CLEAR_ERROR })
  }), []);

  // Memoized selectors
  const selectors = useMemo(() => ({
    hasMessages: state.messages.length > 0,
    lastMessage: state.messages[state.messages.length - 1] || null,
    messageCount: state.messages.length,
    canSendMessage: !state.isTyping && !state.error
  }), [state.messages, state.isTyping, state.error]);

  return {
    state,
    actions,
    selectors
  };
};

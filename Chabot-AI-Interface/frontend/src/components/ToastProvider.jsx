import { useState, useEffect, createContext, useContext } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

// Toast context
const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

// Toast types
const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Toast component
const Toast = ({ id, type, title, message, duration, onClose }) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onClose(id), duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case TOAST_TYPES.SUCCESS:
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case TOAST_TYPES.ERROR:
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case TOAST_TYPES.WARNING:
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case TOAST_TYPES.INFO:
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case TOAST_TYPES.SUCCESS:
        return 'border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800';
      case TOAST_TYPES.ERROR:
        return 'border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800';
      case TOAST_TYPES.WARNING:
        return 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-800';
      case TOAST_TYPES.INFO:
      default:
        return 'border-blue-200 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800';
    }
  };

  return (
    <div className={`
      flex items-start gap-3 p-4 rounded-lg border shadow-lg backdrop-blur-sm
      transition-all duration-300 ease-in-out transform
      hover:scale-105 hover:shadow-xl
      ${getStyles()}
    `}>
      {getIcon()}
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
            {title}
          </h4>
        )}
        <p className="text-sm text-gray-700 dark:text-gray-300">
          {message}
        </p>
      </div>
      <button
        onClick={() => onClose(id)}
        className="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      >
        <X className="w-4 h-4 text-gray-500" />
      </button>
    </div>
  );
};

// Toast container
const ToastContainer = ({ toasts, onClose }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onClose} />
      ))}
    </div>
  );
};

// Toast provider
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = ({ type = TOAST_TYPES.INFO, title, message, duration = 5000 }) => {
    const id = Date.now() + Math.random();
    const toast = { id, type, title, message, duration };
    
    setToasts(prev => [...prev, toast]);
    
    return id;
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const clearAllToasts = () => {
    setToasts([]);
  };

  // Convenience methods
  const toast = {
    success: (message, title) => addToast({ type: TOAST_TYPES.SUCCESS, title, message }),
    error: (message, title) => addToast({ type: TOAST_TYPES.ERROR, title, message }),
    warning: (message, title) => addToast({ type: TOAST_TYPES.WARNING, title, message }),
    info: (message, title) => addToast({ type: TOAST_TYPES.INFO, title, message }),
    custom: addToast
  };

  return (
    <ToastContext.Provider value={{ toast, removeToast, clearAllToasts }}>
      {children}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </ToastContext.Provider>
  );
};

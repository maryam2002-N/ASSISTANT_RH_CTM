import { useState, memo } from 'react';
import { Plus, MessageSquare, MoreVertical, Edit2, Trash2, X, RefreshCw, BarChart3 } from 'lucide-react';
import { truncateText } from '../utils/textUtils';

const ChatSidebar = memo(({
  isOpen,
  onClose,
  chatHistory = [],
  currentChatId,
  onNewChat,
  onLoadChat,
  onEditChat,
  onDeleteChat,
  loading = false,
  error = null,
  stats = null,
  onRefresh
}) => {
  const [editingChatId, setEditingChatId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleEdit = (chatId, currentTitle) => {
    setEditingChatId(chatId);
    setEditTitle(currentTitle);
  };

  const handleSaveEdit = async () => {
    if (editTitle.trim() && editingChatId) {
      const success = await onEditChat?.(editingChatId, editTitle.trim());
      if (success) {
        setEditingChatId(null);
        setEditTitle('');
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingChatId(null);
    setEditTitle('');
  };

  const handleDelete = async (chatId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette discussion ?')) {
      await onDeleteChat?.(chatId);
    }
  };

  const formatDate = (dateString) => {
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
    <>
      <div className={`sidebar ${isOpen ? '' : 'sidebar-hidden'}`}>
        {/* Sidebar Header */}
        <div className="sidebar-header">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
            <div className="flex items-center gap-2">
              {onRefresh && (
                <button
                  onClick={onRefresh}
                  className="sidebar-action-button"
                  title="Actualiser l'historique"
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              )}
              <button
                onClick={onClose}
                className="sidebar-action-button"
                style={{ display: window.innerWidth < 768 ? 'block' : 'none' }}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Statistiques */}
          {stats && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Statistiques</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="text-center">
                  <div className="font-bold text-blue-600">{stats.total_sessions || 0}</div>
                  <div className="text-blue-700">Total</div>
                </div>
                <div className="text-center">
                  <div className="font-bold text-green-600">{stats.recent_sessions || 0}</div>
                  <div className="text-green-700">Récentes</div>
                </div>
              </div>
            </div>
          )}
          
          <button
            onClick={onNewChat}
            className="sidebar-new-chat"
            disabled={loading}
          >
            <Plus className="w-4 h-4" />
            <span>Nouvelle Discussion</span>
          </button>

          {/* Message d'erreur */}
          {error && (
            <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Sidebar Content */}
        <div className="sidebar-content">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mb-3" />
              <p className="text-sm text-gray-500">Chargement de l'historique...</p>
            </div>
          ) : chatHistory.length > 0 ? (
            <div className="sidebar-section">
              <h3 className="sidebar-section-title">
                Discussions Récentes ({chatHistory.length})
              </h3>
              <div className="space-y-1">
                {chatHistory.map((chat) => (
                  <div
                    key={chat.id}
                    className={`sidebar-chat-item ${currentChatId === chat.id ? 'sidebar-chat-item-active' : ''}`}
                  >
                    <div
                      className="sidebar-chat-content"
                      onClick={() => onLoadChat?.(chat.id)}
                    >
                      <MessageSquare className="sidebar-chat-icon" />
                      <div className="flex-1 min-w-0">
                        {editingChatId === chat.id ? (
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onBlur={handleSaveEdit}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleSaveEdit();
                              if (e.key === 'Escape') handleCancelEdit();
                            }}
                            className="w-full text-sm bg-transparent border-b border-blue-300 outline-none"
                            autoFocus
                            onClick={(e) => e.stopPropagation()}
                          />
                        ) : (
                          <>
                            <div className="sidebar-chat-title" title={chat.title}>
                              {truncateText(chat.title, 35)}
                            </div>
                            <div className="flex justify-between items-center mt-1">
                              <span className="text-xs text-gray-400">
                                {formatDate(chat.createdAt)}
                              </span>
                              {chat.messageCount && (
                                <span className="text-xs text-blue-500 bg-blue-50 px-1 rounded">
                                  {chat.messageCount} msg
                                </span>
                              )}
                            </div>
                            {chat.lastMessage?.content && (
                              <div className="text-xs text-gray-500 mt-1 truncate">
                                {truncateText(chat.lastMessage.content, 40)}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                    
                    {editingChatId !== chat.id && (
                      <div className="sidebar-chat-actions">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(chat.id, chat.title);
                          }}
                          className="sidebar-action-button"
                          title="Modifier la discussion"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(chat.id);
                          }}
                          className="sidebar-action-button"
                          title="Supprimer la discussion"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8">
              <MessageSquare className="w-12 h-12 text-gray-300 mb-3" />
              <p className="text-sm text-gray-500 text-center">
                Aucune discussion pour le moment. Commencez une nouvelle conversation !
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
});

ChatSidebar.displayName = 'ChatSidebar';

export default ChatSidebar;

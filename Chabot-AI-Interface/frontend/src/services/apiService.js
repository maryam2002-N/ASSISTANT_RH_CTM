// Service API pour communiquer avec le backend Python
class ApiService {
  constructor() {
    // Utiliser l'API principale sur le port 8000
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    this.token = localStorage.getItem('auth_token');
  }

  // Headers par défaut avec authentification
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  // Gestion des erreurs API
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Erreur HTTP: ${response.status}`);
    }
    return response.json();
  }

  // Authentification
  async login(email, password) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await this.handleResponse(response);
      
      // Stocker le token
      this.token = data.access_token;
      localStorage.setItem('auth_token', this.token);
      
      return data;
    } catch (error) {
      console.error('Erreur de connexion:', error);
      throw error;
    }
  }

  async logout() {
    try {
      if (this.token) {
        await fetch(`${this.baseURL}/api/auth/logout`, {
          method: 'POST',
          headers: this.getHeaders(),
        });
      }
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
    } finally {
      // Nettoyer le token local
      this.token = null;
      localStorage.removeItem('auth_token');
    }
  }

  async getCurrentUser() {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/me`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      return this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la récupération des infos utilisateur:', error);
      throw error;
    }
  }

  // Chat
  async sendMessage(message, chatId = null) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/message`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          message,
          chat_id: chatId,
        }),
      });

      return this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      throw error;
    }
  }

  // Chat avec streaming (pour les réponses en temps réel)
  async sendMessageStream(message, chatId = null, onChunk = null) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/stream`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          message,
          chat_id: chatId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                throw new Error(data.error);
              }
              
              if (data.done) {
                return fullResponse;
              }
              
              if (data.content) {
                fullResponse += data.content;
                onChunk?.(data.content, fullResponse);
              }
            } catch (parseError) {
              console.warn('Erreur de parsing du chunk:', parseError);
            }
          }
        }
      }

      return fullResponse;
    } catch (error) {
      console.error('Erreur lors du streaming:', error);
      throw error;
    }
  }

  // Vérification de la santé de l'API
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/api/health`);
      return this.handleResponse(response);
    } catch (error) {
      console.error('Erreur de vérification de santé:', error);
      throw error;
    }
  }

  // Vérifier si l'utilisateur est authentifié
  isAuthenticated() {
    return !!this.token;
  }

  // Nettoyer l'authentification
  clearAuth() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Inscription et activation
  async register(name, email) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email }),
      });

      return this.handleResponse(response);
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      throw error;
    }
  }

  async activateAccount(email, activationCode) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          activation_code: activationCode 
        }),
      });

      return this.handleResponse(response);
    } catch (error) {
      console.error('Erreur d\'activation:', error);
      throw error;
    }
  }

  async setPassword(email, password, confirmPassword) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/set-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password, 
          confirm_password: confirmPassword 
        }),
      });

      return this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la définition du mot de passe:', error);
      throw error;
    }
  }

  // =================== HISTORIQUE DES CONVERSATIONS ===================

  // Récupérer l'historique des conversations
  async getChatHistory(limit = 50) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/history?limit=${limit}`, {
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      throw error;
    }
  }

  // Récupérer les messages d'une session spécifique
  async getSessionMessages(sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/session/${sessionId}/messages`, {
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la récupération des messages:', error);
      throw error;
    }
  }

  // Supprimer une session de chat
  async deleteSession(sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/session/${sessionId}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la suppression de la session:', error);
      throw error;
    }
  }

  // Mettre à jour le titre d'une session
  async updateSessionTitle(sessionId, title) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/session/${sessionId}/title`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify({ title }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la mise à jour du titre:', error);
      throw error;
    }
  }

  // Récupérer les statistiques des conversations
  async getChatStats() {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/stats`, {
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques:', error);
      throw error;
    }
  }

  // Créer une nouvelle session de chat
  async createNewChatSession() {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/new-session`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erreur lors de la création d\'une nouvelle session:', error);
      throw error;
    }
  }
}

// Instance singleton
const apiService = new ApiService();

export default apiService;

import { createContext, useContext, useEffect, useState } from 'react';
import apiService from '../services/apiService';

const AuthContext = createContext({
  user: null,
  login: () => {},
  register: () => {},
  activateAccount: () => {},
  setPassword: () => {},
  logout: () => {},
  isLoading: false,
});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const checkAuthStatus = async () => {
      if (apiService.isAuthenticated()) {
        try {
          const userData = await apiService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Erreur lors de la vérification de l\'authentification:', error);
          // Token invalide, nettoyer l'auth
          apiService.clearAuth();
        }
      }
      setIsLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const response = await apiService.login(email, password);
      const userData = {
        id: response.user.email,
        email: response.user.email,
        username: response.user.name,
        name: response.user.name
      };
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true };
    } catch (error) {
      console.error('Erreur de connexion:', error);
      return { 
        success: false, 
        error: error.message || 'Erreur de connexion' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name, email) => {
    setIsLoading(true);
    try {
      const response = await apiService.register(name, email);
      return { 
        success: true, 
        message: response.message || 'Code d\'activation envoyé à votre email'
      };
    } catch (error) {
      console.error('Erreur d\'enregistrement:', error);
      return { 
        success: false, 
        error: error.message || 'Erreur lors de l\'inscription'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const activateAccount = async (email, activationCode) => {
    setIsLoading(true);
    try {
      const response = await apiService.activateAccount(email, activationCode);
      return { 
        success: true, 
        message: response.message || 'Compte activé avec succès'
      };
    } catch (error) {
      console.error('Erreur d\'activation:', error);
      return { 
        success: false, 
        error: error.message || 'Erreur lors de l\'activation'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const setPassword = async (email, password, confirmPassword) => {
    setIsLoading(true);
    try {
      const response = await apiService.setPassword(email, password, confirmPassword);
      return { 
        success: true, 
        message: response.message || 'Mot de passe défini avec succès'
      };
    } catch (error) {
      console.error('Erreur lors de la définition du mot de passe:', error);
      return { 
        success: false, 
        error: error.message || 'Erreur lors de la définition du mot de passe'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('user');
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      register, 
      activateAccount, 
      setPassword, 
      logout, 
      isLoading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

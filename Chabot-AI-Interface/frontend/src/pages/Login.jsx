import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logoCTM from '../assets/logo_ctm.png';

export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.email || !formData.password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      navigate('/chat');
    } else {
      setError(result.error || 'Échec de la connexion');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-wrapper">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo-container">
              <img 
                src={logoCTM} 
                alt="Logo CTM" 
                className="auth-logo"
              />
            </div>
            <h1 className="auth-title">
              Assistant IA RH CTM
            </h1>
            <h2 className="auth-subtitle">
              Bienvenue de Retour
            </h2>
            <p className="auth-description">
              Connectez-vous pour continuer votre conversation
            </p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {error && (
              <div className="error-message">
                <div className="flex">
                  <div>
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Adresse Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="form-input"
                placeholder="Entrez votre email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Mot de Passe
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="form-input"
                placeholder="Entrez votre mot de passe"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="auth-button"
            >
              {isLoading ? (
                <>
                  <div className="auth-loading-spinner"></div>
                  Connexion en cours...
                </>
              ) : (
                'Se Connecter'
              )}
            </button>

            <div className="auth-footer">
              <p className="auth-text">
                Vous n'avez pas de compte ?{' '}
                <Link
                  to="/register"
                  className="auth-link"
                >
                  Créez-en un ici
                </Link>
              </p>
              <Link
                to="/"
                className="auth-navigation"
              >
                ← Retour à l'accueil
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

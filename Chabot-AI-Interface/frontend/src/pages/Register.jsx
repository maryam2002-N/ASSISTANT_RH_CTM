import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logoCTM from '../assets/logo_ctm.png';

export default function Register() {
  const [currentStep, setCurrentStep] = useState('register'); // register, activation, setPassword
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    activationCode: '',
    password: '',
    confirmPassword: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { register, activateAccount, setPassword, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
    setMessage('');
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.name || !formData.email) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    const result = await register(formData.name, formData.email);
    
    if (result.success) {
      setMessage(result.message);
      setCurrentStep('activation');
    } else {
      setError(result.error);
    }
  };

  const handleActivation = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.activationCode) {
      setError('Veuillez saisir le code d\'activation');
      return;
    }

    const result = await activateAccount(formData.email, formData.activationCode);
    
    if (result.success) {
      setMessage(result.message);
      setCurrentStep('setPassword');
    } else {
      setError(result.error);
    }
  };

  const handleSetPassword = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.password || !formData.confirmPassword) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 4) {
      setError('Le mot de passe doit contenir au moins 4 caractères');
      return;
    }

    const result = await setPassword(formData.email, formData.password, formData.confirmPassword);
    
    if (result.success) {
      setMessage(result.message);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError(result.error);
    }
  };

  const renderRegisterStep = () => (
    <form onSubmit={handleRegister} className="auth-form">
      <div className="form-group">
        <label htmlFor="name" className="form-label">Nom complet</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Votre nom complet"
          className="form-input"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="email" className="form-label">Email</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="votre.email@ctm.ma"
          className="form-input"
          required
        />
      </div>

      <button type="submit" className="auth-button" disabled={isLoading}>
        {isLoading ? (
          <>
            <div className="auth-loading-spinner"></div>
            Inscription en cours...
          </>
        ) : (
          'S\'inscrire'
        )}
      </button>

      <div className="auth-footer">
        <p className="auth-text">
          Vous avez déjà un compte ?{' '}
          <Link to="/login" className="auth-link">
            Se connecter
          </Link>
        </p>
      </div>
    </form>
  );

  const renderActivationStep = () => (
    <form onSubmit={handleActivation} className="auth-form">
      <div className="activation-info">
        <p className="info-text">
          Un code d'activation a été envoyé à <strong>{formData.email}</strong>
        </p>
        <p className="info-subtext">
          Vérifiez votre boîte mail et saisissez le code reçu.
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="activationCode" className="form-label">Code d'activation</label>
        <input
          type="text"
          id="activationCode"
          name="activationCode"
          value={formData.activationCode}
          onChange={handleChange}
          placeholder="Saisissez votre code d'activation"
          className="form-input"
          maxLength="6"
          style={{ textTransform: 'uppercase', letterSpacing: '2px' }}
          required
        />
      </div>

      <button type="submit" className="auth-button" disabled={isLoading}>
        {isLoading ? (
          <>
            <div className="auth-loading-spinner"></div>
            Activation en cours...
          </>
        ) : (
          'Activer le compte'
        )}
      </button>

      <button 
        type="button" 
        className="auth-button-secondary" 
        onClick={() => setCurrentStep('register')}
        disabled={isLoading}
      >
        Retour à l'inscription
      </button>
    </form>
  );

  const renderSetPasswordStep = () => (
    <form onSubmit={handleSetPassword} className="auth-form">
      <div className="activation-info">
        <p className="info-text">
          Compte activé ! Définissez maintenant votre mot de passe.
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="password" className="form-label">Mot de passe</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Votre mot de passe"
          className="form-input"
          minLength="4"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword" className="form-label">Confirmer le mot de passe</label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          placeholder="Confirmez votre mot de passe"
          className="form-input"
          minLength="4"
          required
        />
      </div>

      <button type="submit" className="auth-button" disabled={isLoading}>
        {isLoading ? (
          <>
            <div className="auth-loading-spinner"></div>
            Enregistrement en cours...
          </>
        ) : (
          'Enregistrer le mot de passe'
        )}
      </button>
    </form>
  );

  const getStepTitle = () => {
    switch (currentStep) {
      case 'register':
        return 'Inscription';
      case 'activation':
        return 'Activation du compte';
      case 'setPassword':
        return 'Définir le mot de passe';
      default:
        return 'Inscription';
    }
  };

  const getStepDescription = () => {
    switch (currentStep) {
      case 'register':
        return 'Créez votre compte Assistant RH CTM';
      case 'activation':
        return 'Activez votre compte avec le code reçu par email';
      case 'setPassword':
        return 'Choisissez un mot de passe sécurisé';
      default:
        return '';
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
            <h2 className="auth-subtitle">{getStepTitle()}</h2>
            <p className="auth-description">{getStepDescription()}</p>
          </div>

          <div className="auth-body">
            {message && (
              <div className="success-message">
                {message}
              </div>
            )}

            {error && (
              <div className="error-message">
                <div className="flex">
                  <div>
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'register' && renderRegisterStep()}
            {currentStep === 'activation' && renderActivationStep()}
            {currentStep === 'setPassword' && renderSetPasswordStep()}
          </div>

          <div className="auth-footer">
            <div className="step-indicator">
              <div className={`step ${currentStep === 'register' ? 'active' : 'completed'}`}>1</div>
              <div className={`step ${currentStep === 'activation' ? 'active' : currentStep === 'setPassword' ? 'completed' : ''}`}>2</div>
              <div className={`step ${currentStep === 'setPassword' ? 'active' : ''}`}>3</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

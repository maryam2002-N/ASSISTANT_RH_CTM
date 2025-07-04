import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { MessageSquare, Bot, Users, Shield, Zap, Heart } from 'lucide-react';
import logoCTM from '../assets/logo_ctm.png';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="home-container">      
      {/* Hero Section */}
      <div className="hero-section">
        {/* Animated Background Elements */}
        <div className="hero-bg">
          <div className="hero-bg-element hero-bg-element-1"></div>
          <div className="hero-bg-element hero-bg-element-2"></div>
        </div>

        {/* Main Hero Content */}
        <div className="hero-content">
          <div className="hero-text-center">
            {/* Logo CTM */}
            <div className="hero-logo-container">
              <img 
                src={logoCTM} 
                alt="Logo CTM" 
                className="hero-logo"
              />
            </div>

            {/* Main Title with Animation */}
            <div className="hero-title-container">
              <h1 className="hero-title">
                Assistant IA
                <span className="hero-title-accent"> RH CTM</span>
              </h1>
            </div>

            {/* Subtitle with Delay */}
            <div className="hero-subtitle-container">
              <p className="hero-subtitle">
                Votre compagnon RH intelligent spécialement conçu pour CTM.
                Obtenez une assistance instantanée pour vos questions RH, politiques et support 24h/7.
              </p>
            </div>

            {/* Feature Icons with Staggered Animation */}
            <div className="hero-features">
              <div className="hero-feature">
                <Bot className="hero-feature-icon" />
                <span className="hero-feature-text">IA Avancée</span>
              </div>
              <div className="hero-feature">
                <Users className="hero-feature-icon" />
                <span className="hero-feature-text">Support RH</span>
              </div>
              <div className="hero-feature">
                <Zap className="hero-feature-icon" />
                <span className="hero-feature-text">Aide Instantanée</span>
              </div>
              <div className="hero-feature">
                <Shield className="hero-feature-icon" />
                <span className="hero-feature-text">Sécurisé</span>
              </div>
            </div>

            {/* CTA Buttons with Animation */}
            <div className="hero-cta">
              {user ? (
                <Link to="/chat" className="btn btn-primary btn-large">
                  <MessageSquare className="btn-icon" />
                  Commencer à Discuter
                </Link>
              ) : (
                <>
                  <Link to="/login" className="btn btn-primary btn-large">
                    <MessageSquare className="btn-icon" />
                    Commencer
                  </Link>
                  <Link to="/register" className="btn btn-secondary btn-large">
                    Créer un Compte
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>


    </div>
  );
}


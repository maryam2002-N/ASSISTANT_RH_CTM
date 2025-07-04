import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogOut, User, Moon, Sun } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import logoCTM from '../assets/logo_ctm.png';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <img 
            src={logoCTM} 
            alt="Logo CTM" 
            className="navbar-logo-img"
          />
          <span>Assistant IA RH CTM</span>
        </Link>

        {/* User Section */}
        <div className="navbar-user">
          {/* Theme Toggle */}          <button
            onClick={toggleTheme}
            className="navbar-button"
            title={`Basculer vers le mode ${theme === 'dark' ? 'clair' : 'sombre'}`}
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </button>

          {user ? (
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="navbar-button"
              >
                <User className="w-4 h-4" />
                <span className="navbar-user-info">{user.name || user.email}</span>
              </button>              {/* User Dropdown Menu */}
              {isUserMenuOpen && (
                <div className="navbar-dropdown">
                  <div className="navbar-dropdown-header">
                    <div className="navbar-dropdown-name">{user.name || 'Utilisateur'}</div>
                    <div className="navbar-dropdown-email">{user.email}</div>
                  </div>
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsUserMenuOpen(false);
                    }}
                    className="navbar-dropdown-button"
                  >
                    <LogOut className="w-4 h-4" />
                    Se Déconnecter
                  </button>
                </div>
              )}
            </div>
          ) : (            <div className="flex items-center gap-3">
              <Link to="/login" className="navbar-button">
                Se Connecter
              </Link>
              <Link to="/register" className="navbar-button">
                S'Inscrire
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Click outside to close user menu */}
      {isUserMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsUserMenuOpen(false)}
        />
      )}
    </nav>
  );
};

export default Navbar;

import streamlit as st

def apply_styles():
    """Applique des styles CSS personnalisés à l'interface Streamlit"""
    # Styles CSS personnalisés
    st.markdown(
        """
        <style>
        /* Styles pour la bannière de bienvenue */
        .welcome-banner {
            background-color: #0055B9;
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            margin-left: -20px;
            margin-right: -20px;
            margin-top: -20px;
            width: calc(100% + 40px);
        }
        
        /* Style pour l'avatar circulaire */
        .welcome-banner .avatar {
            background-color: rgba(255, 255, 255, 0.25);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            margin-right: 15px;
        }
        
        /* Style pour les conteneurs de texte */
        .welcome-banner .welcome-info {
            display: flex;
            align-items: center;
        }
        
        .welcome-banner .welcome-text {
            display: flex;
            flex-direction: column;
        }
        
        .welcome-banner .greeting {
            font-size: 16px;
            font-weight: normal;
            opacity: 0.9;
            margin-bottom: 2px;
        }
        
        .welcome-banner .username {
            font-size: 24px;
            font-weight: bold;
        }
        
        /* Style pour le bouton de déconnexion */
        .welcome-banner .logout-btn {
            background-color: rgba(255, 255, 255, 0.25);
            border-radius: 50px;
            padding: 8px 20px;
            cursor: pointer;
            transition: background-color 0.2s;
            font-weight: normal;
        }
        
        .welcome-banner .logout-btn:hover {
            background-color: rgba(255, 255, 255, 0.35);
        }
        
        /* Masquer le bouton de déconnexion par défaut de Streamlit */
        button[key="logout_button"] {
            display: none;
        }
        
        /* --- STYLES CHAT --- */
        /* Modifier la position des bulles de chat */
        [data-testid="stChatMessageContainer"] {
            display: flex;
            flex-direction: column;
            width: 100%;
        }
        
        /* Conteneur des messages utilisateur (aligné à droite) */
        [data-testid="stChatMessageContainer"][data-testid*="user"] {
            align-items: flex-end;
            margin-left: 4rem;
        }
        
        /* Conteneur des messages assistant (aligné à gauche) */
        [data-testid="stChatMessageContainer"][data-testid*="assistant"] {
            align-items: flex-start;
            margin-right: 4rem;
        }
        
        /* Contenu des messages utilisateur */
        .user-message {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            background-color: #e2f0ff;
            margin: 0;
            max-width: fit-content;
        }
        
        /* Contenu des messages assistant */
        .assistant-message {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            background-color: #f0f0f0;
            margin: 0;
            max-width: fit-content;
        }
        
        /* Styles pour les icônes */
        .stChatMessageAvatar {
            margin-bottom: 10px;
        }
        
        /* Avatar utilisateur - style spécifique sans fond */
        [data-testid="stChatMessageAvatar-user"] {
            font-size: 24px !important;
            margin-left: 10px;
        }
        
        /* Avatar assistant - style spécifique sans fond */
        [data-testid="stChatMessageAvatar-assistant"] {
            font-size: 24px !important;
            margin-right: 10px;
        }
        
        /* Suppression des fonds pour les avatars */
        .stChatMessageAvatar div {
            background: transparent !important;
            box-shadow: none !important;
        }
        
        /* Animation pour les messages de chat */
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        
        .stChatMessage {
            animation: fadeIn 0.5s;
        }
          /* Amélioration des boutons avec dégradés */
        div.stButton > button:first-child {
            background: linear-gradient(45deg, #1a5bb4, #3a7bd5, #2b68c4);
            background-size: 200% 200%;
            color: white;
            border-radius: 6px;
            border: none;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            box-shadow: 0 4px 15px rgba(26, 91, 180, 0.25);
            transition: all 0.4s ease;
            animation: gradientAnimation 3s ease infinite;
        }
        
        @keyframes gradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        
        div.stButton > button:hover {
            background-size: 150% 150%;
            transform: translateY(-3px);
            box-shadow: 0 7px 15px rgba(26, 91, 180, 0.4);
            color: white;
        }
          /* Style pour les onglets avec dégradé */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: linear-gradient(to right, #f0f2f6, #e8ecf3);
            border-radius: 6px 6px 0px 0px;
            padding: 10px 24px;
            border: 1px solid #e0e0e0;
            border-bottom: none;
            color: #2c3e50 !important;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.03);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(45deg, #1a5bb4, #3a7bd5);
            background-size: 200% 200%;
            color: white !important;
            cursor: pointer;
            border: none;
            box-shadow: 0 -2px 8px rgba(26, 91, 180, 0.2);
            animation: tabGradientAnimation 3s ease infinite;
        }
        
        @keyframes tabGradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        
        /* Style pour le texte dans les onglets */
        .stTabs [data-testid="stMarkdown"] p {
            color: #000000 !important;
        }
        
        /* Modifier la couleur du texte des champs input pour une meilleure lisibilité */
        input[type="text"], input[type="password"], textarea {
            color: #000000 !important;
            caret-color: #000000 !important; /* Couleur du curseur */
        }
        
        /* S'assurer que le texte dans le champ de chat est noir */
        .stChatInputContainer textarea {
            color: #000000 !important;
            caret-color: #000000 !important; /* Couleur du curseur */
        }
        
        /* Style global pour tous les champs de saisie */
        .stTextInput input, .stTextArea textarea {
            color: #000000 !important;
            caret-color: #000000 !important; /* Couleur du curseur */
        }
        
        /* Style pour le curseur dans tous les éléments interactifs */
        button, input, textarea, select, .stTabs, .stSelectbox, .stMultiSelect {
            cursor: pointer;
        }
        
        /* Assurer que le curseur (caret) est noir dans tous les champs de saisie */
        * {
            caret-color: #000000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
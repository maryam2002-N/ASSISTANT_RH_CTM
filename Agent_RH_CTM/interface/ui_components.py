import streamlit as st
from auth.user_auth import handle_login, handle_register, handle_activation, handle_set_password, handle_logout, load_users
from agent import as_stream
import base64
from pathlib import Path
import time
import os
import random
from agno.exceptions import ModelProviderError
import re

# Gestion des erreurs avec circuit breaker
class CircuitBreaker:
    def __init__(self, max_failures=5, reset_timeout=300):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout  # en secondes
        self.failures = 0
        self.open_since = None
        
    def record_failure(self):
        self.failures += 1
        if self.failures >= self.max_failures:
            self.open_since = time.time()
            
    def record_success(self):
        self.failures = 0
        self.open_since = None
        
    def is_open(self):
        if self.open_since is None:
            return False
            
        # Si le circuit est ouvert mais qu'on a dépassé le temps de reset
        if time.time() - self.open_since > self.reset_timeout:
            # On réinitialise pour permettre une nouvelle tentative
            self.failures = 0
            self.open_since = None
            return False
            
        return True
        
    def get_remaining_timeout(self):
        if self.open_since is None:
            return 0
        elapsed = time.time() - self.open_since
        remaining = max(0, self.reset_timeout - elapsed)
        return int(remaining)

# Instanciation du circuit breaker
api_circuit_breaker = CircuitBreaker(max_failures=8, reset_timeout=180)  # 3 minutes

def get_ctm_logo():
    """Charge le logo CTM depuis le dossier assets"""
    logo_path = os.path.join('assets', 'logo_ctm.png')
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    else:
        # Logo CTM de secours en SVG si le fichier n'est pas accessible
        ctm_color = "#0066CC"  # Bleu CTM
        svg_content = f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 30" width="60" height="20">
            <text x="5" y="20" fill="{ctm_color}" font-family="Arial" font-weight="bold" font-size="20">CTM</text>
        </svg>
        '''
        # Convertir en base64
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return b64

def display_auth_ui():
    """Affiche l'interface d'authentification"""
    # Placer le logo ou le titre
    st.title("Assistant CV - CTM")
    
    # Vérifier d'abord si l'utilisateur doit définir un mot de passe
    users = load_users()
    if st.session_state.email:
        user = next((u for u in users if u["email"].lower() == st.session_state.email.lower()), None)
        if user and user.get("activated") and not user.get("password_hash"):
            st.subheader("Première connexion")
            st.info("Créez votre mot de passe.")
            pwd1 = st.text_input("Nouveau mot de passe", type="password", key="first_pwd1")
            pwd2 = st.text_input("Confirmez le mot de passe", type="password", key="first_pwd2")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Définir le mot de passe", use_container_width=True):
                    handle_set_password(pwd1, pwd2)
            return  # Sortir de la fonction pour ne pas afficher les autres éléments
    
    if st.session_state.page == "auth":
        tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
        
        with tab1:
            st.subheader("Connexion")
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_password")
            
            # Utiliser columns pour créer un layout plus agréable
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Se connecter", use_container_width=True):
                    handle_login(email, pwd)
        
        with tab2:
            st.subheader("Inscription")
            name = st.text_input("Nom complet", key="reg_name")
            email = st.text_input("Adresse email", key="reg_email")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("S'inscrire", use_container_width=True):
                    handle_register(name, email)
    
    elif st.session_state.page == "activation":
        st.subheader("Activation du compte")
        st.info(f"Un code d'activation a été envoyé à {st.session_state.email}")
        code_input = st.text_input("Entrez le code d'activation reçu par email")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Activer", use_container_width=True):
                handle_activation(code_input)

def display_skills_ui(skills_dict):
    """Affiche une interface de visualisation des compétences"""
    if not skills_dict:
        return
        
    st.subheader("Compétences clés")
    
    # Identifier les catégories de compétences
    categories = {
        "tech": "Techniques",
        "soft": "Personnelles", 
        "lang": "Langues",
        "other": "Autres"
    }
    
    # Afficher les compétences par catégories
    cols = st.columns(len(categories))
    
    for i, (cat_key, cat_name) in enumerate(categories.items()):
        with cols[i]:
            st.markdown(f"**{cat_name}**")
            if cat_key in skills_dict:
                for skill, level in skills_dict[cat_key].items():
                    # Affiche une barre de progression pour le niveau (0-100)
                    st.markdown(f"{skill}")
                    st.progress(min(level/100, 1.0))

def display_chat_ui(agent):
    """Affiche l'interface de chat après authentification"""
    # En-tête avec bouton de déconnexion bien placé
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Assistant CV - CTM")
    with col2:
        # Bouton de déconnexion en haut à droite
        if st.button("Déconnexion", key="logout_button", use_container_width=True):
            handle_logout()
    
    # Vérifier si le circuit breaker est actif
    if api_circuit_breaker.is_open():
        st.warning(f"⚠️ Service temporairement limité en raison de surcharge. Réessayez dans {api_circuit_breaker.get_remaining_timeout()} secondes.")

    # Affichage du statut avec logo CTM
    ctm_logo = get_ctm_logo()
    logo_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <img src="data:image/png;base64,{ctm_logo}" style="margin-right: 5px; height: 24px;">
        <span style="color: #71AAE2; font-weight: bold;">Assistant RH</span>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

    st.write(
        f"""Bienvenue {st.session_state.name}! Je suis prêt pour vous assister à effectuer
        des recherches des CV depuis la base de connaissances."""
    )

    # Bouton nouveau chat
    if st.button("💬 Nouveau Chat", key="new_chat"):
        st.session_state.messages = []
        st.rerun()

    # Affichage des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrée de chat
    if prompt := st.chat_input("Posez votre question ici...?"):
        # Vérifier si le circuit est ouvert avant d'accepter de nouvelles requêtes
        if api_circuit_breaker.is_open():
            error_message = f"⚠️ Service temporairement limité en raison de surcharge. Réessayez dans {api_circuit_breaker.get_remaining_timeout()} secondes."
            st.error(error_message)
            return
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Gestion des erreurs API avec tentatives de réessai et backoff exponentiel
            max_retries = 4
            base_delay = 1.5  # secondes
            
            for attempt in range(max_retries):
                try:
                    # Jitter pour éviter les requêtes synchronisées lors des réessais
                    jitter = random.uniform(0.8, 1.2) 
                    retry_delay = base_delay * (2 ** attempt) * jitter
                    
                    chunks = agent.run(prompt, stream=True)
                    response = st.write_stream(as_stream(chunks))
                    
                    message_obj = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message_obj)
                    
                    # Enregistrer le succès dans le circuit breaker
                    api_circuit_breaker.record_success()
                    break  # Sortir de la boucle si réussi
                
                except ModelProviderError as e:
                    error_code = None
                    if "429" in str(e):
                        error_code = "429"
                    elif "503" in str(e):
                        error_code = "503" 
                    elif "500" in str(e):
                        error_code = "500"
                        
                    # Enregistrer l'échec dans le circuit breaker
                    api_circuit_breaker.record_failure()
                        
                    if (error_code in ["429", "503", "500"]) and attempt < max_retries - 1:
                        # Si erreur de surcharge et pas la dernière tentative
                        retry_message = f"Limite de requêtes atteinte. Nouvelle tentative dans {retry_delay:.1f} secondes... ({attempt+1}/{max_retries})"
                        st.warning(retry_message)
                        time.sleep(retry_delay)
                    else:
                        # Dernière tentative ou autre erreur
                        error_message = "Désolé, le service est temporairement surchargé. Veuillez réessayer dans quelques minutes."
                        if error_code not in ["429", "503", "500"]:
                            error_message = f"Une erreur s'est produite: {str(e)}"
                        
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
                        break
                
                except Exception as e:
                    # Gestion des autres types d'erreurs
                    error_message = f"Une erreur inattendue s'est produite: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    break

def extract_skills_from_text(text):
    """Extrait les compétences d'un texte CV"""
    skills = {
        "tech": {},  # Compétences techniques
        "soft": {},  # Compétences personnelles
        "lang": {},  # Compétences linguistiques
        "other": {}  # Autres compétences
    }
    
    # Mots-clés pour identifier les sections de compétences
    tech_keywords = ["technique", "programming", "développement", "logiciel", "software", "informatique", "it", "system"]
    soft_keywords = ["soft", "personnel", "communication", "leadership", "équipe", "team"]
    lang_keywords = ["langue", "language", "idioma", "parlé", "écrit", "anglais", "français", "arabe"]
    
    # Recherche de sections de compétences et attribution d'un niveau heuristique
    lines = text.lower().split("\n")
    
    current_section = None
    
    for line in lines:
        # Détecter le type de section
        if any(keyword in line for keyword in tech_keywords):
            current_section = "tech"
        elif any(keyword in line for keyword in soft_keywords):
            current_section = "soft"
        elif any(keyword in line for keyword in lang_keywords):
            current_section = "lang"
            
        # Si on trouve un mot qui ressemble à une compétence (pas trop long, pas un mot commun)
        skill_match = re.search(r'([a-zA-Z\+\#]+(?:\s[a-zA-Z\+\#]+){0,2})[\s\:\-]*(excellent|bon|moyen|débutant|avancé|courant|natif|[0-9]+\s*\%|[0-9]+\s*ans)?', line)
        if skill_match:
            skill_name = skill_match.group(1).strip()
            
            # Filtrer les compétences non pertinentes (trop courtes ou mots communs)
            if len(skill_name) < 3 or skill_name in ["les", "des", "que", "qui", "une", "pour"]:
                continue
                
            # Déterminer le niveau en fonction du texte ou utiliser une valeur par défaut
            level_text = skill_match.group(2).lower() if skill_match.group(2) else ""
            
            # Convertir le texte en valeur numérique
            level = 50  # Niveau par défaut
            
            if "excellent" in level_text or "avancé" in level_text or "expert" in level_text:
                level = 90
            elif "bon" in level_text or "courant" in level_text:
                level = 75
            elif "moyen" in level_text or "intermédiaire" in level_text:
                level = 50
            elif "débutant" in level_text or "notions" in level_text:
                level = 25
            
            # Extraire un pourcentage s'il est mentionné
            percent_match = re.search(r'([0-9]+)\s*\%', level_text)
            if percent_match:
                level = min(100, int(percent_match.group(1)))
                
            # Extraire les années d'expérience
            years_match = re.search(r'([0-9]+)\s*ans', level_text)
            if years_match:
                years = int(years_match.group(1))
                # Convertir les années en niveau (max 10 ans = 100%)
                level = min(100, years * 10)
            
            # Attribuer la compétence à la section appropriée
            if current_section and current_section in skills:
                skills[current_section][skill_name] = level
            else:
                skills["other"][skill_name] = level
    
    return skills
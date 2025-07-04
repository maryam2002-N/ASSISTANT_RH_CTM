import streamlit as st
from agent import agent
from auth.user_auth import check_auth_token
from interface.ui_components import display_auth_ui, display_chat_ui
from utils.styles import apply_styles


st.set_page_config(
    page_title="AI RH",
    page_icon="https://ctmgroupe-my.sharepoint.com/:i:/r/personal/recrutement-ctm_ctm_ma/Documents/Images/businessman_10817334.png?csf=1&web=1&e=o4QcvR",  
)

# Initialisation des états de session
if "page" not in st.session_state:
    st.session_state.page = "auth"
if "email" not in st.session_state:
    st.session_state.email = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "auth_token" not in st.session_state:
    st.session_state.auth_token = ""

# Vérification de l'authentification via token
check_auth_token()

# Appliquer les styles CSS personnalisés
apply_styles()

# Interface principale
if not st.session_state.authenticated:
    # Afficher l'interface d'authentification
    display_auth_ui()
    st.stop()
else:
    # Afficher l'interface de chat
    display_chat_ui(agent)


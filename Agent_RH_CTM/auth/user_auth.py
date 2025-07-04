import json
import random
import string
import hashlib
import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from dotenv import load_dotenv
from utils.env_config import EMAIL_SENDER, EMAIL_PASSWORD

# Charger les variables d'environnement
load_dotenv()

# Fonction pour générer un token d'authentification unique
def generate_auth_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_activation_email(to_email, code):
    """Envoie un email d'activation avec le code fourni"""
    try:
        # Configuration email depuis .env
        sender_email = os.getenv("EMAIL_USER") or EMAIL_SENDER
        sender_password = os.getenv("EMAIL_PASSWORD") or EMAIL_PASSWORD
        smtp_server = os.getenv("SMTP_SERVER", "smtp-mail.outlook.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        
        # Vérification des identifiants
        if not sender_email or not sender_password:
            print("❌ Configuration email manquante. Vérifiez les variables d'environnement.")
            return False
        
        print(f"🔧 Configuration SMTP: {smtp_server}:{smtp_port}")
        print(f"📧 Envoi du code d'activation vers {to_email}...")
            
        subject = "Activation de votre compte - Assistant RH CTM"
        body = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Activation Assistant RH CTM</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f7fa;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                .header::before {{
                    content: '🚀';
                    font-size: 40px;
                    display: block;
                    margin-bottom: 15px;
                }}
                .header h1 {{
                    font-size: 28px;
                    font-weight: 600;
                    margin-bottom: 8px;
                }}
                .header p {{
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                    background-color: #ffffff;
                }}
                .welcome {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .welcome h2 {{
                    color: #1e3a8a;
                    font-size: 24px;
                    margin-bottom: 10px;
                }}
                .message {{
                    color: #374151;
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .code-container {{
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    padding: 30px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code-label {{
                    color: #1e40af;
                    font-size: 16px;
                    margin-bottom: 15px;
                    font-weight: 500;
                }}
                .activation-code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #1e3a8a;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                    background-color: white;
                    padding: 15px 25px;
                    border-radius: 8px;
                    display: inline-block;
                    border: 2px solid #e5e7eb;
                }}
                .instructions {{
                    background-color: #f8fafc;
                    border-left: 4px solid #3b82f6;
                    padding: 25px;
                    margin: 30px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .instructions h3 {{
                    color: #1e3a8a;
                    font-size: 18px;
                    margin-bottom: 15px;
                }}
                .instructions ol {{
                    color: #374151;
                    font-size: 15px;
                    line-height: 1.8;
                    padding-left: 20px;
                }}
                .instructions li {{
                    margin-bottom: 8px;
                }}
                .notice {{
                    background-color: #fef3c7;
                    border: 1px solid #f59e0b;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .notice p {{
                    color: #92400e;
                    font-size: 14px;
                    font-weight: 500;
                    margin: 0;
                }}
                .footer {{
                    background-color: #f8fafc;
                    padding: 25px 30px;
                    text-align: center;
                    border-top: 1px solid #e5e7eb;
                }}
                .footer p {{
                    color: #6b7280;
                    font-size: 13px;
                    line-height: 1.5;
                    margin: 5px 0;
                }}
                .company {{
                    font-weight: 600;
                    color: #1e3a8a;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Assistant RH CTM</h1>
                    <p>Activation de votre compte</p>
                </div>
                
                <div class="content">
                    <div class="welcome">
                        <h2>Bienvenue !</h2>
                    </div>
                    
                    <div class="message">
                        <p>Votre demande d'inscription à l'Assistant RH CTM a été approuvée.</p>
                        <p>Pour activer votre compte, veuillez utiliser le code d'activation suivant :</p>
                    </div>
                    
                    <div class="code-container">
                        <div class="code-label">Votre code d'activation est :</div>
                        <div class="activation-code">{code}</div>
                    </div>
                    
                    <div class="notice">
                        <p>Ce code est valide pour 24 heures. Si vous n'avez pas demandé cette inscription, veuillez ignorer cet email.</p>
                    </div>
                    
                    <div class="instructions">
                        <h3>Étapes suivantes :</h3>
                        <ol>
                            <li>Retournez sur la page d'inscription</li>
                            <li>Saisissez ce code d'activation</li>
                            <li>Définissez votre mot de passe</li>
                            <li>Commencez à utiliser l'Assistant RH</li>
                        </ol>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par le système d'inscription Assistant RH CTM.</p>
                    <p>Si vous n'avez pas demandé ce code, veuillez ignorer ce message.</p>
                    <p class="company">© 2025 Compagnie de Transports au Maroc</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg["From"] = f"Assistant RH CTM <{sender_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Connexion et envoi
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        
        print(f"✅ Code d'activation envoyé avec succès à {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email: {e}")
        return False

# Fonctions pour les callbacks d'authentification
def handle_login(email, password):
    users = load_users()
    user = next((u for u in users if u["email"].lower() == email.lower()), None)
    if user and user.get("activated") and user.get("password_hash") == hash_password(password):
        # Générer un nouveau token d'authentification
        auth_token = generate_auth_token()
        token_expiry = time.time() + (7 * 24 * 60 * 60)  # Expire dans une semaine
        
        # Stocker le token dans l'utilisateur
        user["auth_token"] = auth_token
        user["token_expiry"] = token_expiry
        save_users(users)
        
        # Mettre à jour l'état de la session
        st.session_state.authenticated = True
        st.session_state.email = email
        st.session_state.name = user.get("name", "")
        st.session_state.auth_token = auth_token
        st.session_state.page = "chat"
        
        # Rediriger vers la page principale avec le token en query param
        st.query_params.token = auth_token
        st.rerun()
    else:
        st.error("Email ou mot de passe incorrect.")

def handle_register(name, email):
    users = load_users()
    user = next((u for u in users if u["email"].lower() == email.lower()), None)
    if not user:
        st.error("Adresse email non autorisée. Contactez l'administrateur.")
    else:
        code = generate_code()
        user["activation_code"] = code
        user["name"] = name
        save_users(users)
        st.session_state.page = "activation"
        st.session_state.email = email
        if send_activation_email(email, code):
            st.success(f"Code d'activation envoyé à {email}.")
            st.rerun()
        else:
            st.error("Impossible d'envoyer l'email d'activation.")

def handle_activation(code):
    users = load_users()
    user = next((u for u in users if u["email"].lower() == st.session_state.email.lower()), None)
    if user and user["activation_code"] == code:
        user["activated"] = True
        user["activation_code"] = ""
        save_users(users)
        st.success("Activation réussie. Veuillez créer votre mot de passe.")
        # Ne pas changer la page, rester pour définir le mot de passe
        st.rerun()
    else:
        st.error("Code d'activation incorrect.")

def handle_set_password(pwd1, pwd2):
    if pwd1 != pwd2:
        st.error("Les mots de passe ne correspondent pas.")
    elif len(pwd1) < 4:
        st.error("Mot de passe trop court.")
    else:
        users = load_users()
        user = next((u for u in users if u["email"].lower() == st.session_state.email.lower()), None)
        if user:
            user["password_hash"] = hash_password(pwd1)
            save_users(users)
            st.success("Mot de passe enregistré. Vous pouvez maintenant vous connecter.")
            st.session_state.page = "auth"  # Rediriger vers la page de connexion
            st.rerun()

def handle_logout():
    # Supprimer le token de l'utilisateur
    if st.session_state.auth_token:
        users = load_users()
        user = next((u for u in users if u.get("auth_token") == st.session_state.auth_token), None)
        if user:
            user.pop("auth_token", None)
            user.pop("token_expiry", None)
            save_users(users)
    
    # Réinitialiser l'état de la session
    st.session_state.authenticated = False
    st.session_state.email = ""
    st.session_state.name = ""
    st.session_state.auth_token = ""
    st.session_state.page = "auth"
    
    # Supprimer le token des query params
    if "token" in st.query_params:
        st.query_params.pop("token")
    
    st.rerun()

def check_auth_token():
    """Vérifier si un token d'authentification existe et tenter de s'authentifier avec ce token"""
    try:
        if not st.session_state.authenticated:
            users = load_users()
            
            # On utiliser un query param pour stocker le token
            query_params = st.query_params
            token = query_params.get("token", "")
            
            if token:
                # Chercher l'utilisateur avec ce token
                user = next((u for u in users if u.get("auth_token") == token), None)
                if user:
                    # Vérifier si le token n'est pas expiré
                    token_expiry = user.get("token_expiry", 0)
                    if token_expiry > time.time():
                        st.session_state.authenticated = True
                        st.session_state.email = user["email"]
                        st.session_state.name = user.get("name", "")
                        st.session_state.auth_token = token
                        st.session_state.page = "chat"
                        return True
    except Exception as e:
        st.error(f"Erreur lors de la récupération du token: {e}")
    return False

def verify_user_credentials(email, password):
    """Vérifier les identifiants utilisateur pour l'API"""
    try:
        users = load_users()
        user = next((u for u in users if u["email"].lower() == email.lower()), None)
        
        if user and user.get("activated", False):
            # Vérifier le mot de passe
            password_hash = hash_password(password)
            if user.get("password_hash") == password_hash:
                return True
        return False
    except Exception as e:
        print(f"Erreur lors de la vérification des identifiants: {e}")
        return False

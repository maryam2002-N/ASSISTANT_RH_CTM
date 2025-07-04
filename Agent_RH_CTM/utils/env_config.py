import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration pour l'email
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_USER = os.environ.get("EMAIL_USER", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp-mail.outlook.com")
SMTP_PORT = os.environ.get("SMTP_PORT", "587")

# Vous pouvez ajouter d'autres variables d'environnement ici
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_KEY_01 = os.environ.get("GEMINI_API_KEY_01", "")
GEMINI_API_KEY_02 = os.environ.get("GEMINI_API_KEY_02", "")
GEMINI_API_KEY_03 = os.environ.get("GEMINI_API_KEY_03", "")
GEMINI_API_KEY_04 = os.environ.get("GEMINI_API_KEY_04", "")
GEMINI_API_KEY_05 = os.environ.get("GEMINI_API_KEY_05", "")
GEMINI_API_KEY_06 = os.environ.get("GEMINI_API_KEY_06", "")
GEMINI_API_KEY_07 = os.environ.get("GEMINI_API_KEY_07", "")
GEMINI_API_KEY_08 = os.environ.get("GEMINI_API_KEY_08", "")
GEMINI_API_KEY_09 = os.environ.get("GEMINI_API_KEY_09", "")
GEMINI_API_KEY_10 = os.environ.get("GEMINI_API_KEY_10", "")
GEMINI_API_KEY_11 = os.environ.get("GEMINI_API_KEY_11", "")
GEMINI_API_KEY_12 = os.environ.get("GEMINI_API_KEY_12", "")
GEMINI_API_KEY_13 = os.environ.get("GEMINI_API_KEY_13", "")
GEMINI_API_KEY_14 = os.environ.get("GEMINI_API_KEY_14", "")
GEMINI_API_KEY_15 = os.environ.get("GEMINI_API_KEY_15", "")
GEMINI_API_KEY_16 = os.environ.get("GEMINI_API_KEY_16", "")
GEMINI_API_KEY_17 = os.environ.get("GEMINI_API_KEY_17", "")
GEMINI_API_KEY_18 = os.environ.get("GEMINI_API_KEY_18", "")
GEMINI_API_KEY_19 = os.environ.get("GEMINI_API_KEY_19", "")
def get_config(key, default=None):
    """Récupère une variable d'environnement avec une valeur par défaut"""
    return os.environ.get(key, default)
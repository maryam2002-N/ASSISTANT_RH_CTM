"""
Serveur API simple pour l'inscription sans la base vectorielle
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.append(os.getcwd())

try:
    from auth.user_auth import load_users, save_users, generate_code, send_activation_email, hash_password
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    exit(1)

app = FastAPI(title="CTM Registration API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    email: str
    name: str

class ActivateRequest(BaseModel):
    email: str
    code: str

class SetPasswordRequest(BaseModel):
    email: str
    password: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "registration_api"
    }

@app.post("/api/auth/register")
def register_user(register_data: RegisterRequest):
    """Inscription d'un utilisateur"""
    try:
        print(f"🔐 Inscription demandée: {register_data.email}")
        
        # Charger les utilisateurs
        users = load_users()
        user = next((u for u in users if u["email"].lower() == register_data.email.lower()), None)
        
        if not user:
            print(f"❌ Email non autorisé: {register_data.email}")
            raise HTTPException(status_code=403, detail="Email non autorisé")
        
        if user.get("activated", False):
            print(f"❌ Utilisateur déjà activé: {register_data.email}")
            raise HTTPException(status_code=400, detail="Utilisateur déjà activé")
        
        # Générer code d'activation
        activation_code = generate_code()
        user["activation_code"] = activation_code
        user["name"] = register_data.name
        user["password_hash"] = ""
        
        save_users(users)
        
        # Envoyer l'email
        email_sent = send_activation_email(register_data.email, activation_code)
        
        if email_sent:
            print(f"✅ Email envoyé: {register_data.email}")
            return {"message": f"Code d'activation envoyé à {register_data.email}"}
        else:
            print(f"❌ Échec envoi email: {register_data.email}")
            raise HTTPException(status_code=500, detail="Impossible d'envoyer l'email")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur inscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/activate")
def activate_user(activate_data: ActivateRequest):
    """Activation avec code"""
    try:
        users = load_users()
        user = next((u for u in users if u["email"].lower() == activate_data.email.lower()), None)
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if user.get("activation_code") != activate_data.code:
            raise HTTPException(status_code=400, detail="Code incorrect")
        
        user["activated"] = True
        user["activation_code"] = ""
        save_users(users)
        
        return {"message": "Activation réussie"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/set-password")
def set_password(password_data: SetPasswordRequest):
    """Définir mot de passe"""
    try:
        users = load_users()
        user = next((u for u in users if u["email"].lower() == password_data.email.lower()), None)
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if not user.get("activated", False):
            raise HTTPException(status_code=400, detail="Utilisateur non activé")
        
        user["password_hash"] = hash_password(password_data.password)
        save_users(users)
        
        return {"message": "Mot de passe défini"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage API d'inscription CTM...")
    print("📧 Serveur SMTP: Office 365")
    print("🌐 URL: http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)

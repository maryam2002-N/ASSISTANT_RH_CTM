from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
import uvicorn

# Import de l'agent seulement quand nécessaire
import sys
import os
# Ajouter le répertoire Agent_RH_CTM au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Changer le répertoire de travail vers Agent_RH_CTM
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import des fonctions d'authentification (toujours disponibles)
from auth.user_auth import verify_user_credentials, load_users, save_users, generate_code, send_activation_email, hash_password

# Import des utilitaires d'historique
from chat_history_utils import chat_history_manager, ChatSession, ChatMessage

# Variables globales pour l'agent
agent = None
agent_ready = False

# Configuration de la stratégie des clés API
# True: Utilise une nouvelle clé API pour chaque requête (meilleure distribution)
# False: Utilise un agent persistant par utilisateur (plus efficace pour les conversations longues)
USE_FRESH_API_KEY_PER_REQUEST = True

def initialize_agent():
    """Initialise l'agent seulement quand nécessaire"""
    global agent, agent_ready
    if agent is None:
        try:
            from agent import agent as _agent, as_text, as_stream
            agent = _agent
            agent_ready = True
            print("✅ Agent initialisé avec succès")
            return _agent, as_text, as_stream
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de l'agent: {e}")
            agent_ready = False
            return None, None, None
    else:
        from agent import as_text, as_stream
        return agent, as_text, as_stream

app = FastAPI(title="Agent RH CTM API", version="1.0.0")

# Configuration CORS pour permettre les requêtes depuis React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],  # Ports React courants
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration pour servir les fichiers statiques (CVs)
static_cvs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "cvs")
if os.path.exists(static_cvs_path):
    app.mount("/static/cvs", StaticFiles(directory=static_cvs_path), name="cvs")
    print(f"📁 Fichiers CV disponibles sur: /static/cvs/")
else:
    print(f"⚠️  Répertoire CV non trouvé: {static_cvs_path}")

# Configuration pour servir tous les fichiers statiques
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    print(f"📁 Fichiers statiques disponibles sur: /static/")

# Configuration de la sécurité
security = HTTPBearer()

# Modèles Pydantic pour la validation des données
class LoginRequest(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    message: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    chat_id: str
    timestamp: str

class UserInfo(BaseModel):
    email: str
    name: str
    authenticated: bool

# Nouveaux modèles pour l'inscription et l'activation
class RegisterRequest(BaseModel):
    name: str
    email: str

class ActivationRequest(BaseModel):
    email: str
    activation_code: str

class SetPasswordRequest(BaseModel):
    email: str
    password: str
    confirm_password: str

# Modèles pour l'historique des discussions
class ChatSessionResponse(BaseModel):
    session_id: str
    user_id: Optional[str]
    title: str
    created_at: str
    updated_at: Optional[str]
    message_count: int
    last_message: Optional[str]

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int
    
class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]
    total: int

class UpdateSessionTitleRequest(BaseModel):
    title: str

# Stockage temporaire des sessions (en production, utilisez Redis ou une base de données)
active_sessions = {}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie le token d'authentification"""
    token = credentials.credentials
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return active_sessions[token]

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    """Endpoint d'authentification"""
    try:
        # Vérifier les credentials avec votre système d'auth existant
        if verify_user_credentials(login_data.email, login_data.password):
            # Créer un token simple (en production, utilisez JWT)
            token = f"token_{datetime.now().timestamp()}_{hash(login_data.email)}"
            
            # Stocker la session
            active_sessions[token] = {
                "email": login_data.email,
                "name": login_data.email.split("@")[0],  # Nom basique depuis l'email
                "authenticated": True
            }
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": active_sessions[token]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de connexion: {str(e)}"
        )

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Endpoint de déconnexion"""
    # Supprimer la session
    for token, user_data in list(active_sessions.items()):
        if user_data["email"] == current_user["email"]:
            del active_sessions[token]
            break
    
    return {"message": "Déconnexion réussie"}

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur actuel"""
    return UserInfo(**current_user)

user_agents = {}

def get_agent_for_user(user_id: str):
    """Récupère ou crée un agent pour un utilisateur spécifique"""
    if user_id not in user_agents:
        from agent import create_agent
        # Créer un agent avec rotation automatique des clés API
        user_agents[user_id] = create_agent(user_id=user_id)
        print(f"[API] Nouvel agent créé pour l'utilisateur: {user_id}")
    return user_agents[user_id]

@app.post("/api/chat/message", response_model=ChatResponse)
async def send_message(
    chat_data: ChatMessage, 
    current_user: dict = Depends(get_current_user)
):
    """Endpoint pour envoyer un message à l'agent"""
    try:
        # Utiliser votre agent existant pour traiter le message
        print(f"[API] Traitement du message de {current_user['email']}: {chat_data.message}")
        
        # Créer un ID de chat si non fourni
        chat_id = chat_data.chat_id or f"chat_{current_user['email']}_{int(datetime.now().timestamp())}"
        
        # Obtenir l'agent selon la stratégie configurée
        if USE_FRESH_API_KEY_PER_REQUEST:
            # Stratégie 1: Nouvelle clé API à chaque requête pour meilleure distribution
            from agent import create_agent_with_fresh_key
            user_agent = create_agent_with_fresh_key(current_user['email'])
            print(f"[API] Agent créé avec nouvelle clé API pour: {current_user['email']}")
        else:
            # Stratégie 2: Agent persistant par utilisateur (plus efficace pour les conversations longues)
            user_agent = get_agent_for_user(current_user['email'])
            print(f"[API] Agent persistant utilisé pour: {current_user['email']}")
        
        if not user_agent:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent non disponible"
            )
        
        # Appeler votre agent avec le message
        response_chunks = user_agent.run(
            chat_data.message, 
            stream=False,
            session_id=chat_id
        )
        
        # Convertir la réponse en texte
        from agent import as_text
        response_text = as_text(response_chunks)
        
        # Si pas de réponse, message par défaut
        if not response_text.strip():
            response_text = "Je n'ai pas pu traiter votre demande. Veuillez réessayer."
        
        # Sauvegarder la conversation avec l'user_id
        chat_history_manager.save_conversation(
            user_id=current_user['email'],
            user_message=chat_data.message,
            assistant_response=response_text,
            session_id=chat_id
        )
        
        print(f"[API] Réponse générée: {response_text[:100]}...")
        
        return ChatResponse(
            response=response_text,
            chat_id=chat_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"[API] Erreur lors du traitement du message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )

@app.post("/api/chat/stream")
async def send_message_stream(
    chat_data: ChatMessage, 
    current_user: dict = Depends(get_current_user)
):
    """Endpoint pour envoyer un message à l'agent avec streaming"""
    try:
        from fastapi.responses import StreamingResponse
        
        # Créer un ID de chat si non fourni
        chat_id = chat_data.chat_id or f"chat_{datetime.now().timestamp()}"
        
        def generate_response():
            try:
                # Initialiser l'agent si nécessaire
                current_agent, as_text_func, as_stream_func = initialize_agent()
                if not current_agent:
                    yield f"data: {json.dumps({'error': 'Agent non disponible'})}\n\n"
                    return
                
                # Appeler votre agent avec streaming et l'ID de session
                response_chunks = current_agent.run(
                    chat_data.message, 
                    stream=True,
                    session_id=chat_id
                )
                
                for chunk in as_stream_func(response_chunks):
                    if chunk:
                        yield f"data: {json.dumps({'content': chunk, 'chat_id': chat_id})}\n\n"
                
                # Signal de fin
                yield f"data: {json.dumps({'done': True, 'chat_id': chat_id})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du streaming: {str(e)}"
        )

@app.get("/api/cvs/list")
async def list_cvs(current_user: dict = Depends(get_current_user)):
    """Endpoint pour lister les CVs disponibles"""
    try:
        cvs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "cvs")
        if not os.path.exists(cvs_path):
            return {"cvs": [], "message": "Répertoire CV non trouvé"}
        
        cvs = []
        for filename in os.listdir(cvs_path):
            file_path = os.path.join(cvs_path, filename)
            if os.path.isfile(file_path):
                # Obtenir les informations du fichier
                stat = os.stat(file_path)
                cvs.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "url": f"/static/cvs/{filename}"
                })
        
        # Trier par date de modification (plus récent en premier)
        cvs.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "cvs": cvs,
            "total": len(cvs),
            "message": f"{len(cvs)} CV(s) trouvé(s)"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des CVs: {str(e)}"
        )

@app.get("/api/cvs/{filename}")
async def get_cv_info(filename: str, current_user: dict = Depends(get_current_user)):
    """Endpoint pour obtenir les informations d'un CV spécifique"""
    try:
        cvs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "cvs")
        file_path = os.path.join(cvs_path, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CV '{filename}' non trouvé"
            )
        
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{filename}' n'est pas un fichier"
            )
        
        # Obtenir les informations du fichier
        stat = os.stat(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Déterminer le type de fichier
        file_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain'
        }
        
        return {
            "filename": filename,
            "size": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1024*1024 else f"{stat.st_size / (1024*1024):.1f} MB",
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_ext,
            "mime_type": file_types.get(file_ext, 'application/octet-stream'),
            "url": f"/static/cvs/{filename}",
            "download_url": f"/static/cvs/{filename}?download=1"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du CV: {str(e)}"
        )

@app.post("/api/auth/register")
async def register_user(register_data: RegisterRequest):
    """Endpoint d'inscription - vérifie si l'email est autorisé puis envoie le code d'activation"""
    try:
        users = load_users()
        user = next((u for u in users if u["email"].lower() == register_data.email.lower()), None)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adresse email non autorisée. Contactez l'administrateur."
            )
        
        if user.get("activated", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce compte est déjà activé. Utilisez la page de connexion."
            )
        
        # Générer un code d'activation
        activation_code = generate_code()
        user["activation_code"] = activation_code
        user["name"] = register_data.name
        save_users(users)
        
        # Envoyer l'email d'activation (ou simuler en mode test)
        if TEST_MODE:
            print(f"[TEST MODE] Code d'activation pour {register_data.email}: {activation_code}")
            email_sent = True
        else:
            email_sent = send_activation_email(register_data.email, activation_code)
        
        if email_sent:
            return {
                "success": True,
                "message": f"Code d'activation {'généré' if TEST_MODE else 'envoyé'} pour {register_data.email}."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Impossible d'envoyer l'email d'activation."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'inscription: {str(e)}"
        )

@app.post("/api/auth/activate")
async def activate_user(activation_data: ActivationRequest):
    """Endpoint pour activer un compte utilisateur"""
    try:
        users = load_users()
        user = next((u for u in users if u["email"].lower() == activation_data.email.lower()), None)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        if user.get("activated", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le compte est déjà activé"
            )
        
        if user.get("activation_code") != activation_data.activation_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code d'activation incorrect"
            )
        
        # Activer l'utilisateur
        user["activated"] = True
        user["activation_code"] = ""
        save_users(users)
        
        return {
            "success": True,
            "message": "Activation réussie. Veuillez créer votre mot de passe."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'activation du compte: {str(e)}"
        )

@app.post("/api/auth/set-password")
async def set_password(set_password_data: SetPasswordRequest):
    """Endpoint pour définir un nouveau mot de passe"""
    try:
        if set_password_data.password != set_password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les mots de passe ne correspondent pas"
            )
        
        if len(set_password_data.password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe trop court (minimum 4 caractères)"
            )
        
        users = load_users()
        user = next((u for u in users if u["email"].lower() == set_password_data.email.lower()), None)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        if not user.get("activated", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le compte doit être activé avant de définir le mot de passe"
            )
        
        # Mettre à jour le mot de passe
        user["password_hash"] = hash_password(set_password_data.password)
        save_users(users)
        
        return {
            "success": True,
            "message": "Mot de passe enregistré. Vous pouvez maintenant vous connecter."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du mot de passe: {str(e)}"
        )

@app.get("/api/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Récupère l'historique des conversations de l'utilisateur"""
    try:
        # Récupérer les sessions pour l'utilisateur actuel
        sessions = chat_history_manager.get_user_sessions(
            user_id=current_user.get('email'),
            limit=limit
        )
        
        # Convertir en format de réponse
        session_responses = [
            ChatSessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=session.message_count,
                last_message=session.last_message
            )
            for session in sessions
        ]
        
        return ChatHistoryResponse(
            sessions=session_responses,
            total=len(session_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}"
        )

@app.get("/api/chat/session/{session_id}/messages", response_model=SessionMessagesResponse)
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère les messages d'une session spécifique appartenant à l'utilisateur"""
    try:
        user_id = current_user.get('email')
        
        # Vérifier que la session appartient à l'utilisateur
        session = chat_history_manager.get_session_by_id(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée ou accès non autorisé"
            )
        
        # Récupérer les messages de la session
        messages = chat_history_manager.get_session_messages(session_id)
        
        # Convertir en format de réponse
        message_responses = [
            ChatMessageResponse(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in messages
        ]
        
        return SessionMessagesResponse(
            session_id=session_id,
            messages=message_responses,
            total=len(message_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des messages: {str(e)}"
        )

@app.delete("/api/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Supprime une session de chat appartenant à l'utilisateur"""
    try:
        user_id = current_user.get('email')
        
        # Vérifier que la session appartient à l'utilisateur
        session = chat_history_manager.get_session_by_id(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée ou accès non autorisé"
            )
        
        # Supprimer la session
        success = chat_history_manager.delete_session(session_id)
        
        if success:
            return {
                "success": True,
                "message": f"Session {session_id} supprimée avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de la session: {str(e)}"
        )

@app.put("/api/chat/session/{session_id}/title")
async def update_session_title(
    session_id: str,
    title_data: UpdateSessionTitleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour le titre d'une session"""
    try:
        success = chat_history_manager.update_session_title(session_id, title_data.title)
        
        if success:
            return {
                "success": True,
                "message": f"Titre de la session mis à jour: {title_data.title}"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du titre: {str(e)}"
        )

@app.get("/api/chat/stats")
async def get_chat_stats(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques des conversations"""
    try:
        stats = chat_history_manager.get_session_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@app.get("/api/config/api-keys")
async def get_api_key_config(current_user: dict = Depends(get_current_user)):
    """Obtenir la configuration actuelle des clés API"""
    return {
        "use_fresh_api_key_per_request": USE_FRESH_API_KEY_PER_REQUEST,
        "description": "True = Nouvelle clé API par requête, False = Agent persistant"
    }

@app.post("/api/config/api-keys")
async def set_api_key_config(
    use_fresh_key: bool, 
    current_user: dict = Depends(get_current_user)
):
    """Configurer la stratégie des clés API"""
    global USE_FRESH_API_KEY_PER_REQUEST
    USE_FRESH_API_KEY_PER_REQUEST = use_fresh_key
    
    # Nettoyer les agents existants si on change de stratégie
    global user_agents
    user_agents.clear()
    
    return {
        "message": "Configuration mise à jour",
        "use_fresh_api_key_per_request": USE_FRESH_API_KEY_PER_REQUEST
    }

@app.get("/api/health")
async def health_check():
    """Endpoint de vérification de santé"""
    global agent_ready
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": agent_ready,
        "services": {
            "authentication": True,
            "registration": True,
            "agent_chat": agent_ready
        }
    }

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Agent RH CTM API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Mode test pour les endpoints (désactiver l'envoi d'email en mode développement)
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

if __name__ == "__main__":
    # Configuration pour le développement
    print("🚀 Démarrage de l'API Agent RH CTM...")
    print("📖 Documentation disponible sur: http://localhost:8000/docs")
    print("🔗 Interface React attendue sur: http://localhost:3000")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

@app.post("/api/chat/new-session")
async def create_new_chat_session(current_user: dict = Depends(get_current_user)):
    """Crée une nouvelle session de chat pour l'utilisateur"""
    try:
        user_email = current_user.get('email')
        user_name = current_user.get('name', user_email.split('@')[0])
        
        # Créer un nouvel ID de session
        new_chat_id = f"chat_{user_email}_{int(datetime.now().timestamp())}"
        
        # Message de bienvenue pour la nouvelle session
        welcome_message = f"🆕 Nouvelle conversation démarrée !\n\nBonjour {user_name}, comment puis-je vous aider aujourd'hui ?\n\n💡 Conseils :\n• Posez-moi des questions sur les CV\n• Demandez des analyses de candidats\n• Recherchez des profils spécifiques"
        
        # Sauvegarder le message de bienvenue
        chat_history_manager.save_conversation(
            user_id=user_email,
            user_message="Nouvelle session créée",
            assistant_response=welcome_message,
            session_id=new_chat_id
        )
        
        return {
            "success": True,
            "chat_id": new_chat_id,
            "welcome_message": welcome_message,
            "timestamp": datetime.now().isoformat(),
            "message": "Nouvelle conversation créée avec succès"
        }
        
    except Exception as e:
        print(f"[API] Erreur lors de la création d'une nouvelle session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la nouvelle session: {str(e)}"
        )

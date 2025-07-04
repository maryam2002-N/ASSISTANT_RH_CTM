import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class ChatMessage:
    """Représente un message de chat"""
    role: str  # 'user' ou 'assistant'
    content: str
    timestamp: str

@dataclass
class ChatSession:
    """Représente une session de chat"""
    session_id: str
    user_id: Optional[str]
    title: str
    created_at: str
    updated_at: Optional[str]
    message_count: int
    last_message: Optional[str]

class ChatHistoryManager:
    """Gestionnaire pour l'historique des conversations"""
    
    def __init__(self, db_path: str = "sqlite.db"):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """S'assure que la base de données existe"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Base de données non trouvée: {self.db_path}")
    
    def get_connection(self):
        """Obtient une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def get_user_sessions(self, user_id: Optional[str] = None, limit: int = 50) -> List[ChatSession]:
        """Récupère les sessions de chat d'un utilisateur"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Requête pour récupérer les sessions avec informations de base
                if user_id:
                    query = """
                    SELECT session_id, user_id, memory, created_at, updated_at
                    FROM agent_sessions 
                    WHERE user_id = ? OR user_id IS NULL
                    ORDER BY created_at DESC 
                    LIMIT ?
                    """
                    cursor.execute(query, (user_id, limit))
                else:
                    query = """
                    SELECT session_id, user_id, memory, created_at, updated_at
                    FROM agent_sessions 
                    ORDER BY created_at DESC 
                    LIMIT ?
                    """
                    cursor.execute(query, (limit,))
                
                sessions = []
                for row in cursor.fetchall():
                    session_id, user_id, memory_json, created_at, updated_at = row
                    
                    # Parser le JSON memory pour extraire les messages
                    messages = []
                    title = f"Conversation {session_id[:8]}"
                    last_message = None
                    
                    if memory_json:
                        try:
                            memory_data = json.loads(memory_json)
                            if 'messages' in memory_data and memory_data['messages']:
                                messages = memory_data['messages']
                                # Générer un titre basé sur le premier message de l'utilisateur
                                for msg in messages:
                                    if msg.get('role') == 'user' and msg.get('content'):
                                        content = msg['content']
                                        title = content[:50] + "..." if len(content) > 50 else content
                                        break
                                
                                # Récupérer le dernier message
                                if messages:
                                    last_msg = messages[-1]
                                    last_message = last_msg.get('content', '')[:100]
                        except (json.JSONDecodeError, KeyError):
                            pass
                    
                    # Convertir timestamp
                    created_str = datetime.fromtimestamp(created_at).isoformat() if created_at else datetime.now().isoformat()
                    updated_str = datetime.fromtimestamp(updated_at).isoformat() if updated_at else None
                    
                    sessions.append(ChatSession(
                        session_id=session_id,
                        user_id=user_id,
                        title=title,
                        created_at=created_str,
                        updated_at=updated_str,
                        message_count=len(messages),
                        last_message=last_message
                    ))
                
                return sessions
                
        except Exception as e:
            print(f"Erreur lors de la récupération des sessions: {e}")
            return []
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Récupère les messages d'une session spécifique"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT memory FROM agent_sessions WHERE session_id = ?", (session_id,))
                result = cursor.fetchone()
                
                if not result or not result[0]:
                    return []
                
                memory_data = json.loads(result[0])
                messages = memory_data.get('messages', [])
                
                chat_messages = []
                for msg in messages:
                    # Extraire les informations du message
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    
                    # Gérer différents formats de contenu
                    if isinstance(content, list):
                        # Si le contenu est une liste, joindre les textes
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and part.get('type') == 'text':
                                text_parts.append(part.get('text', ''))
                            elif isinstance(part, str):
                                text_parts.append(part)
                        content = ' '.join(text_parts)
                    
                    # Timestamp - utiliser celui du message s'il existe, sinon timestamp actuel
                    timestamp = msg.get('timestamp', datetime.now().isoformat())
                    if isinstance(timestamp, (int, float)):
                        timestamp = datetime.fromtimestamp(timestamp).isoformat()
                    
                    chat_messages.append(ChatMessage(
                        role=role,
                        content=content,
                        timestamp=timestamp
                    ))
                
                return chat_messages
                
        except Exception as e:
            print(f"Erreur lors de la récupération des messages: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Supprime une session de chat"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM agent_sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la suppression de la session: {e}")
            return False
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """Met à jour le titre d'une session (stocké dans session_data)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Récupérer les données actuelles
                cursor.execute("SELECT session_data FROM agent_sessions WHERE session_id = ?", (session_id,))
                result = cursor.fetchone()
                
                if result:
                    session_data = json.loads(result[0]) if result[0] else {}
                    session_data['custom_title'] = title
                    
                    cursor.execute(
                        "UPDATE agent_sessions SET session_data = ? WHERE session_id = ?",
                        (json.dumps(session_data), session_id)
                    )
                    conn.commit()
                    return True
                return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour du titre: {e}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques des sessions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Nombre total de sessions
                cursor.execute("SELECT COUNT(*) FROM agent_sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Sessions récentes (dernières 24h)
                recent_timestamp = int(datetime.now().timestamp()) - (24 * 3600)
                cursor.execute("SELECT COUNT(*) FROM agent_sessions WHERE created_at > ?", (recent_timestamp,))
                recent_sessions = cursor.fetchone()[0]
                
                return {
                    "total_sessions": total_sessions,
                    "recent_sessions": recent_sessions,
                    "database_path": self.db_path
                }
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {}

# Instance globale du gestionnaire
chat_history_manager = ChatHistoryManager()

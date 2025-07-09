import os
os.environ["AGNO_DEBUG"] = "True"
from agno.agent import Agent , AgentKnowledge
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.models.google import Gemini
from agno.run.response import RunEvent, RunResponse
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb , SearchType
from agno.tools.duckdb import DuckDbTools
from utils.env_config import GEMINI_API_KEY_14, GEMINI_API_KEY_15
from mcp_email_tool import EmailTool
from agno.vectordb.pgvector import PgVector
import random

# Pour utiliser le reranker FlagEmbedding, installer avec:
# pip install -U FlagEmbedding

def as_text(chunks):
    """Convertit les chunks de réponse en texte"""
    import asyncio
    import inspect
    
    text = ""
    
    # Si chunks est un objet unique, le mettre dans une liste
    if not hasattr(chunks, '__iter__') or isinstance(chunks, str):
        chunks = [chunks]
    
    try:
        for chunk in chunks:
            # Vérifier si c'est une coroutine et l'exécuter
            if inspect.iscoroutine(chunk):
                try:
                    print(f"[DEBUG] Détection d'une coroutine: {chunk}")
                    # Essayer d'exécuter la coroutine
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Si un loop est déjà en cours, créer une nouvelle tâche
                        result = asyncio.create_task(chunk)
                        # Attendre que la tâche se termine (non recommandé mais nécessaire ici)
                        import time
                        while not result.done():
                            time.sleep(0.01)
                        chunk = result.result()
                    else:
                        chunk = asyncio.run(chunk)
                    print(f"[DEBUG] Résultat de la coroutine: {chunk}")
                except Exception as e:
                    print(f"[DEBUG] Erreur lors de l'exécution de la coroutine: {e}")
                    chunk = f"❌ Erreur lors du traitement: {str(e)}"
            
            # Traitement des différents types de chunks
            if isinstance(chunk, RunResponse):
                if hasattr(chunk, 'content') and isinstance(chunk.content, str):
                    if chunk.event == RunEvent.run_response:
                        text += chunk.content
                elif hasattr(chunk, '__str__'):
                    text += str(chunk)
            elif isinstance(chunk, str):
                text += chunk
            elif isinstance(chunk, dict):
                # Gérer les dictionnaires (comme les réponses d'email)
                if 'message' in chunk:
                    text += str(chunk['message'])
                else:
                    text += str(chunk)
            elif hasattr(chunk, '__str__'):
                text += str(chunk)
                
    except TypeError as e:
        print(f"[DEBUG] TypeError dans as_text: {e}")
        # Si chunks n'est pas itérable, essayer de l'utiliser directement
        if inspect.iscoroutine(chunks):
            try:
                print(f"[DEBUG] Traitement de la coroutine unique: {chunks}")
                chunks = asyncio.run(chunks)
                print(f"[DEBUG] Résultat de la coroutine unique: {chunks}")
            except Exception as e:
                print(f"[DEBUG] Erreur lors de l'exécution de la coroutine unique: {e}")
                return f"❌ Erreur lors du traitement: {str(e)}"
        
        if isinstance(chunks, RunResponse):
            if hasattr(chunks, 'content') and isinstance(chunks.content, str):
                if chunks.event == RunEvent.run_response:
                    text = chunks.content
            elif hasattr(chunks, '__str__'):
                text = str(chunks)
        elif isinstance(chunks, str):
            text = chunks
        elif isinstance(chunks, dict):
            # Gérer les dictionnaires
            if 'message' in chunks:
                text = str(chunks['message'])
            else:
                text = str(chunks)
        elif hasattr(chunks, '__str__'):
            text = str(chunks)
    
    except Exception as e:
        print(f"[DEBUG] Erreur générale dans as_text: {e}")
        return f"❌ Erreur lors du traitement de la réponse: {str(e)}"
    
    return text


def get_api_key():
    """Retourne alternativement une des deux clés API pour distribuer la charge"""
    # Liste des clés API disponibles
    api_keys = [GEMINI_API_KEY_14, GEMINI_API_KEY_15]
    
    # Filtre les clés vides
    available_keys = [key for key in api_keys if key and key.strip()]
    
    if not available_keys:
        raise ValueError("Aucune clé API Gemini disponible")
    
    # Sélectionne une clé au hasard pour distribuer la charge
    selected_key = random.choice(available_keys)
    print(f"[DEBUG] Sélection de la clé API: {selected_key[:10]}...")
    return selected_key


def get_agent_instructions():
    """Retourne la liste des instructions communes pour l'agent"""
    return [
        "Répondez uniquement en français.",
        "Se contenter uniquement des données de la base de connaissances.",
        "Ne pas effectuer de recherche sur internet.",
        "Afficher le résultat en tableau.",
        "RECHERCHE OBLIGATOIRE: TOUJOURS effectuer des recherches dans la base de connaissances avant de répondre.",
        "IMPORTANT: Utilisez UNIQUEMENT les outils de recherche intégrés d'Agno, ne pas utiliser 'default_api' ou 'print()'.",
        "Pour effectuer une recherche, utilisez directement les capacités de l'agent sans appeler d'API externe.",
        "Pour toute demande d'information, faire AU MOINS une recherche avec les mots-clés pertinents.",
        "Si une première recherche ne donne pas de résultats, essayer avec des mots-clés alternatifs.",
        "Ne JAMAIS répondre 'Je n'ai pas cette information' sans avoir fait de recherches.",
        "IMPORTANT: Pour rechercher dans la base de connaissances, utiliser les fonctionnalités intégrées de l'agent sans appeler de fonctions externes.",
        "INTERDICTION: Ne JAMAIS utiliser 'print()', 'default_api', ou toute autre fonction externe pour la recherche.",
        "RECHERCHE CORRECTE: Quand un utilisateur demande des informations, répondez directement en utilisant la base de connaissances intégrée sans générer de code tool_call.",
        "FORMAT DE RÉPONSE: Répondez DIRECTEMENT avec les informations trouvées sous forme de tableau markdown, sans générer de code ou de tool_call.",
        "INTERDICTION ABSOLUE: Ne JAMAIS générer de code Python, de tool_call, ou d'appel à default_api dans la réponse.",
        "DÉDUPLICATION OBLIGATOIRE: Ne jamais afficher plusieurs fois le même candidat/CV.",
        "Si un même nom apparaît plusieurs fois avec des dates de réception différentes, ne garder que la version la plus récente.",
        "Identifier les doublons par le nom complet du candidat et ne présenter qu'une seule entrée par personne.",
        "RECHERCHE PAR CRITÈRES MULTIPLES:",
        "- Pour les recherches par lieu ET expérience, effectuer plusieurs recherches complémentaires",
        "- Rechercher d'abord par lieu (ex: 'Marrakech', 'Casablanca', 'Rabat', etc.)",
        "- Puis filtrer les résultats par expérience (chercher 'ANS', 'années', 'expérience', etc.)",
        "- Pour l'expérience, rechercher des patterns comme: '5 ANS', '6 ans', 'plus de 5', 'années d'expérience'",
        "Distinguer clairement les informations des CV et les informations de suivi de candidature.",
        "Pour les résultats contenant 'status:' dans le document, créer une section 'Suivi de candidature'.",
        "Pour les CV, créer une section 'Contenu du CV' et afficher le texte du CV.",
        "Afficher le nom du CV comme un lien Markdown : '[nom du cv](./app/static/cvs/[nom du cv])'",
        "Pour chaque ajout dans la base de connaissances, ajoute : 'DATE MAJ = [maintenant]'",
        "Ne pas montrer la colonne 'DATE MAJ' si ce n'est pas demandé",
        "Pour la colonne 'VISIO', afficher 'https://wa.me/[Tél]'. Supprimer les espaces de [Tél] et si le num commence avec '06' remplacer par '2126' et '07' par '2127'.",
        "Ne pas montrer la colonne 'Tél' si ce n'est pas demandé",
        "Ne pas montrer la colonne 'VISIO' si ce n'est pas demandé",
        "IMPORTANT: Chaque CV contient une date de réception au début du texte au format 'Date de réception : JJ/MM/AAAA à HH:MM'. Utiliser cette information pour filtrer les CV par date de réception.",
        "RECHERCHE PAR DATE - RÈGLES SPÉCIFIQUES:",
        "- PROBLÈME TECHNIQUE: La recherche avec deux-points ':' cause des erreurs de syntaxe",
        "- SOLUTION: Pour rechercher par date, utiliser plusieurs stratégies de recherche:",
        "- STRATÉGIE 1: Rechercher la date exacte au format demandé",
        "- STRATÉGIE 2: Rechercher avec différents formats de date (avec/sans zéros initiaux)",
        "- STRATÉGIE 3: Rechercher par composants (mois/année, année seule)",
        "- STRATÉGIE 4: Rechercher des termes associés avec 'réception' ou 'reçu'",
        "- STRATÉGIE 5: Si aucun résultat, rechercher des mots-clés du mois en français",
        "- TOUJOURS effectuer AU MOINS 3-4 recherches différentes avant de conclure qu'il n'y a pas de CV",
        "- Formats de date à essayer OBLIGATOIREMENT: 'JJ/MM/AAAA', 'J/MM/AAAA', 'JJ/M/AAAA', 'J/M/AAAA', 'JJ/MM/AA'",
        "- Si aucun résultat après TOUTES ces tentatives, indiquer 'Aucun CV reçu le [date demandée]'",
        "Analyser le contenu complet des CV pour extraire toutes les informations pertinentes même si elles contiennent des caractères spéciaux comme les deux-points.",
        "ENVOI D'EMAIL - FONCTIONNALITÉ:",
        "- Vous pouvez envoyer des emails aux candidats en utilisant l'outil email.",
        "- Pour envoyer un email, utilisez la fonction send_email avec les paramètres : destinataire, sujet, contenu.",
        "- Personnalisez toujours le contenu de l'email avec les informations du candidat trouvées dans la base.",
        "- Demandez confirmation avant d'envoyer un email.",
        "- Formats d'email supportés : entretien, refus, demande d'information, convocation.",
    ]


class DebugPgVector(PgVector):
    """Extension de PgVector avec debugging des scores de similarité"""
    
    def search(self, query: str, limit: int = 5, **kwargs):
        """Override search to add debug information about similarity scores"""
        print(f"[DEBUG] 🔍 Recherche vectorielle: '{query}' (limit={limit})")
        if kwargs:
            print(f"[DEBUG] 📋 Arguments additionnels: {kwargs}")
        
        # Call the parent search method with all arguments
        results = super().search(query, limit, **kwargs)
        
        # Log the vector search results with scores
        if results:
            print(f"[DEBUG] 📊 SCORES DE SIMILARITÉ VECTORIELLE:")
            print(f"[DEBUG] ==========================================")
            for i, doc in enumerate(results):
                # Try to extract score information
                score_info = "Score non disponible"
                if hasattr(doc, 'metadata') and doc.metadata:
                    # Check for various score fields
                    score_fields = ['_distance', 'similarity_score', 'score', 'cosine_distance']
                    for field in score_fields:
                        if field in doc.metadata:
                            score_info = f"{field}: {doc.metadata[field]:.4f}"
                            break
                
                doc_name = getattr(doc, 'name', f'Document {i+1}')
                content_preview = getattr(doc, 'content', '')[:80] + "..." if hasattr(doc, 'content') else "Contenu non disponible"
                
                print(f"[DEBUG] 📄 Vector Doc {i+1}: {doc_name}")
                print(f"[DEBUG]    {score_info}")
                print(f"[DEBUG]    Aperçu: {content_preview}")
                print(f"[DEBUG] ------------------------------------------")
        else:
            print(f"[DEBUG] ❌ Aucun résultat trouvé pour la recherche vectorielle: '{query}'")
        
        return results


def create_vector_db():
    """Crée et configure la base de données vectorielle avec debugging"""
    return DebugPgVector(
        table_name="cvs_embeddings_bge_m3",
        db_url="postgresql://CTM:CTM1234@localhost:5532/Agent_CTM",
        search_type=SearchType.hybrid,
        embedder=OllamaEmbedder(id="bge-m3", dimensions=1024),
    )


class FlagRerankerWrapper:
    """Wrapper pour FlagReranker compatible avec agno"""
    
    def __init__(self, flag_reranker):
        self.flag_reranker = flag_reranker
        self.id = getattr(flag_reranker, 'model_name', 'BAAI/bge-reranker-v2-m3')
        print(f"[DEBUG] 🔧 FlagRerankerWrapper initialisé avec modèle: {self.id}")
        
    def rerank(self, query, documents, **kwargs):
        """Rerank documents using FlagReranker"""
        try:
            print(f"[DEBUG] 🔄 === DÉBUT DU RERANKING ===")
            print(f"[DEBUG] 🔄 Reranking {len(documents)} documents avec BAAI/bge-reranker-v2-m3")
            print(f"[DEBUG] 🔄 Requête: '{query}'")
            
            # Prepare pairs for FlagReranker
            pairs = []
            for i, doc in enumerate(documents):
                content = getattr(doc, 'content', str(doc))
                pairs.append([query, content])
                print(f"[DEBUG] 🔄 Document {i+1} préparé pour reranking: {getattr(doc, 'name', 'Sans nom')[:50]}...")
            
            # Compute reranking scores with BAAI/bge-reranker-v2-m3
            print(f"[DEBUG] 🔄 Calcul des scores avec BAAI/bge-reranker-v2-m3...")
            scores = self.flag_reranker.compute_score(pairs)
            
            print(f"[DEBUG] 📊 === SCORES DE RERANKING BAAI/bge-reranker-v2-m3 ===")
            for i, score in enumerate(scores):
                doc_name = getattr(documents[i], 'name', f'Document {i+1}')
                print(f"[DEBUG] 📊 Rerank Doc {i+1}: {doc_name}")
                print(f"[DEBUG] 📊    Score BAAI/bge-reranker-v2-m3: {score:.6f}")
            
            # Sort documents by scores (higher is better)
            doc_score_pairs = list(zip(documents, scores))
            doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            print(f"[DEBUG] 🔄 === ORDRE APRÈS RERANKING ===")
            
            # Add scores to document metadata
            reranked_docs = []
            for rank, (doc, score) in enumerate(doc_score_pairs):
                doc_name = getattr(doc, 'name', f'Document {rank+1}')
                print(f"[DEBUG] 🔄 Rang {rank+1}: {doc_name} (Score: {score:.6f})")
                
                # Add reranking score to metadata
                if hasattr(doc, 'metadata') and doc.metadata:
                    doc.metadata['rerank_score_bge_v2_m3'] = float(score)
                    doc.metadata['rerank_rank'] = rank + 1
                else:
                    # If no metadata, create it
                    setattr(doc, 'metadata', {
                        'rerank_score_bge_v2_m3': float(score),
                        'rerank_rank': rank + 1
                    })
                
                # Also set as direct attributes for easier access
                setattr(doc, 'rerank_score', float(score))
                setattr(doc, 'rerank_rank', rank + 1)
                
                reranked_docs.append(doc)
            
            print(f"[DEBUG] ✅ === RERANKING TERMINÉ ===")
            print(f"[DEBUG] ✅ {len(reranked_docs)} documents réordonnés par BAAI/bge-reranker-v2-m3")
            return reranked_docs
            
        except Exception as e:
            print(f"[DEBUG] ❌ Erreur lors du reranking avec BAAI/bge-reranker-v2-m3: {e}")
            print(f"[DEBUG] ❌ Retour aux documents originaux sans reranking")
            return documents  # Return original documents if reranking fails


def create_reranker():
    """Crée et configure le reranker BAAI bge-reranker avec FlagEmbedding"""
    try:
        print(f"[DEBUG] � Tentative de création du reranker avec FlagEmbedding...")
        
        # Try to import FlagEmbedding
        try:
            from FlagEmbedding import FlagReranker
            print(f"[DEBUG] ✅ FlagEmbedding importé avec succès")
        except ImportError as e:
            print(f"[DEBUG] ❌ FlagEmbedding non disponible: {e}")
            print(f"[DEBUG] 💡 Installation automatique...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "FlagEmbedding"])
                from FlagEmbedding import FlagReranker
                print(f"[DEBUG] ✅ FlagEmbedding installé et importé avec succès")
            except Exception as install_error:
                print(f"[DEBUG] ❌ Échec de l'installation automatique: {install_error}")
                return None
        
        # Use only BAAI/bge-reranker-v2-m3 as requested
        model_name = "BAAI/bge-reranker-v2-m3"
        print(f"[DEBUG] 🔧 Utilisation du modèle: {model_name}")
        
        # Try different configurations for bge-reranker-v2-m3
        reranker_configs = [
            {"use_fp16": True},                          # Use fp16 for speed (default device)
            {"use_fp16": False},                         # No fp16 (default device)
            {"devices": ["cpu"], "use_fp16": False},     # Force CPU, no fp16
            {"devices": ["cpu"], "use_fp16": True},      # Force CPU, with fp16
            {}                                           # Default config
        ]
        
        for config in reranker_configs:
            try:
                print(f"[DEBUG] 🔧 Configuration: {config}")
                reranker = FlagReranker(model_name, **config)
                
                # Test the reranker with French query as per documentation
                test_query = "conducteurs dakhla"
                test_passage = "CV Otmane Abrouk habitant Cité Dakhla, conducteur expérimenté"
                
                # Test with single pair as shown in documentation
                test_score = reranker.compute_score([test_query, test_passage])
                print(f"[DEBUG] ✅ Reranker BAAI/bge-reranker-v2-m3 créé et testé avec succès!")
                print(f"[DEBUG]    Configuration: {config}")
                print(f"[DEBUG]    Score de test: {test_score}")
                
                # Test with normalization (0-1 range)
                normalized_score = reranker.compute_score([test_query, test_passage], normalize=True)
                print(f"[DEBUG]    Score normalisé: {normalized_score}")
                
                # Wrap the FlagReranker for agno compatibility
                wrapped_reranker = FlagRerankerWrapper(reranker)
                return wrapped_reranker
                
            except Exception as config_error:
                print(f"[DEBUG] ❌ Configuration {config} échouée: {config_error}")
                continue
        
        print(f"[DEBUG] ⚠️ Impossible de charger BAAI/bge-reranker-v2-m3")
        print(f"[DEBUG] 💡 Le système fonctionnera sans reranking")
        return None
        
    except Exception as e:
        print(f"[DEBUG] ❌ Erreur générale lors de la création du reranker: {e}")
        return None


class DebugTextKnowledgeBase(TextKnowledgeBase):
    """Extension de TextKnowledgeBase avec debugging des scores de reranking"""
    
    def __init__(self, *args, reranker=None, **kwargs):
        """Initialize with explicit reranker assignment"""
        print(f"[DEBUG] 📚 DebugTextKnowledgeBase.__init__ appelé avec reranker: {type(reranker).__name__ if reranker else 'None'}")
        
        # Pass reranker to parent constructor
        if reranker:
            kwargs['reranker'] = reranker
            print(f"[DEBUG] 📚 Reranker passé au constructeur parent: {type(reranker).__name__}")
        
        super().__init__(*args, **kwargs)
        
        # Store reranker reference for debugging
        self._debug_reranker = reranker
        
        # Check if parent constructor accepted the reranker
        parent_reranker = getattr(self, 'reranker', None)
        print(f"[DEBUG] 📚 Reranker après constructeur parent: {type(parent_reranker).__name__ if parent_reranker else 'None'}")
        print(f"[DEBUG] 📚 Debug reranker stocké: {type(self._debug_reranker).__name__ if self._debug_reranker else 'None'}")
        
        # Force assignment if needed
        if reranker and not parent_reranker:
            try:
                self.reranker = reranker
                print(f"[DEBUG] 📚 Reranker forcé manuellement")
            except Exception as e:
                print(f"[DEBUG] 📚 Impossible de forcer le reranker: {e}")
        
        print(f"[DEBUG] 📚 DebugTextKnowledgeBase initialisé avec reranker: {type(reranker).__name__ if reranker else 'None'}")
    
    def search(self, query: str, num_documents: int = None, **kwargs):
        """Override search to add debug information and force reranker usage"""
        print(f"[DEBUG] 🔍 Recherche dans la base de connaissances: '{query}'")
        
        # Safely check for reranker attribute  
        has_reranker = (hasattr(self, 'reranker') and getattr(self, 'reranker', None) is not None) or \
                      (hasattr(self, '_debug_reranker') and getattr(self, '_debug_reranker', None) is not None)
        print(f"[DEBUG] 📋 Paramètres: num_documents={num_documents}, reranker={has_reranker}")
        if kwargs:
            print(f"[DEBUG] 📋 Arguments additionnels: {kwargs}")
        
        # Get the reranker
        reranker = getattr(self, 'reranker', None) or getattr(self, '_debug_reranker', None)
        
        # Call the parent search method first
        results = super().search(query, num_documents, **kwargs)
        
        # Force reranking if reranker is available and we have results
        if reranker and results and len(results) > 1:
            print(f"[DEBUG] 🔄 FORÇAGE DU RERANKING avec {type(reranker).__name__}")
            try:
                # Apply reranking manually
                reranked_results = reranker.rerank(query, results)
                results = reranked_results
                print(f"[DEBUG] 🔄 Reranking forcé appliqué avec succès")
            except Exception as e:
                print(f"[DEBUG] ❌ Erreur lors du reranking forcé: {e}")
        elif reranker:
            print(f"[DEBUG] 🔄 Reranking ignoré: {len(results) if results else 0} résultats (besoin de >1)")
        else:
            print(f"[DEBUG] 🔄 Pas de reranker disponible")
        
        # Enhanced debugging for all search results
        if results:
            print(f"[DEBUG] 📊 RÉSULTATS DE RECHERCHE COMPLETS:")
            print(f"[DEBUG] ==========================================")
            
            for i, doc in enumerate(results):
                doc_name = getattr(doc, 'name', f'Document {i+1}')
                content_preview = getattr(doc, 'content', '')[:150] + "..." if hasattr(doc, 'content') else "Contenu non disponible"
                
                print(f"[DEBUG] 📄 Document {i+1}: {doc_name}")
                print(f"[DEBUG]    Aperçu: {content_preview}")
                
                # Try to extract all available metadata including reranking scores
                if hasattr(doc, 'metadata') and doc.metadata:
                    print(f"[DEBUG]    📊 Métadonnées disponibles:")
                    for key, value in doc.metadata.items():
                        if isinstance(value, (int, float)):
                            print(f"[DEBUG]       {key}: {value:.6f}")
                        else:
                            print(f"[DEBUG]       {key}: {value}")
                
                # Try to extract scores from various attributes including rerank scores
                score_attrs = ['rerank_score', 'rerank_score_bge_v2_m3', 'rerank_rank', 'score', 'similarity_score', 'vector_score', 'distance']
                for attr in score_attrs:
                    if hasattr(doc, attr):
                        value = getattr(doc, attr)
                        if isinstance(value, (int, float)):
                            print(f"[DEBUG]    🎯 {attr}: {value:.6f}")
                        else:
                            print(f"[DEBUG]    🎯 {attr}: {value}")
                
                print(f"[DEBUG] ------------------------------------------")
            
            # Log reranker-specific information
            if has_reranker:
                reranker = getattr(self, 'reranker', None) or getattr(self, '_debug_reranker', None)
                print(f"[DEBUG] 🔄 RERANKER ACTIF:")
                print(f"[DEBUG]    Type: {type(reranker).__name__}")
                print(f"[DEBUG]    Model ID: {getattr(reranker, 'id', 'Non spécifié')}")
            else:
                print(f"[DEBUG] 🔄 RERANKER: Non disponible")
        else:
            print(f"[DEBUG] ❌ Aucun résultat trouvé pour la requête: '{query}'")
        
        print(f"[DEBUG] ✅ Recherche terminée - {len(results) if results else 0} documents trouvés")
        return results


def create_knowledge_base():
    """Crée et configure la base de connaissances avec reranking et debugging"""
    vector_db = create_vector_db()
    reranker = create_reranker()
    
    print(f"[DEBUG] 📚 Initializing knowledge base from path: 'txt'")
    print(f"[DEBUG] 📚 Vector DB: {type(vector_db).__name__}")
    print(f"[DEBUG] 📚 Reranker: {type(reranker).__name__ if reranker else 'None'}")
    
    knowledge_base = DebugTextKnowledgeBase(
        path="txt", 
        vector_db=vector_db, 
        num_documents=5,
        reranker=reranker
    )
    
    # Verify reranker is properly set
    if hasattr(knowledge_base, 'reranker'):
        actual_reranker = getattr(knowledge_base, 'reranker', None)
        print(f"[DEBUG] 📚 Knowledge base reranker vérifié: {type(actual_reranker).__name__ if actual_reranker else 'None'}")
    else:
        print(f"[DEBUG] 📚 Knowledge base n'a pas d'attribut reranker")
    
    return knowledge_base


def create_storage(user_id=None):
    """Crée et configure le stockage avec un nom de table unique par utilisateur"""
    table_name = f"agent_sessions_{user_id.replace('@', '_').replace('.', '_')}" if user_id else "agent_sessions"
    return SqliteStorage(
        table_name=table_name, 
        db_file="sqlite.db", 
        auto_upgrade_schema=True
    )


def as_stream(chunks):
    """Génère un stream à partir des chunks de réponse"""
    # Si chunks est un objet unique, le mettre dans une liste
    if not hasattr(chunks, '__iter__') or isinstance(chunks, str):
        chunks = [chunks]
    
    try:
        for chunk in chunks:
            if isinstance(chunk, RunResponse) and isinstance(chunk.content, str):
                if chunk.event == RunEvent.run_response:
                    yield chunk.content
            elif isinstance(chunk, str):
                yield chunk
    except TypeError:
        # Si chunks n'est pas itérable, essayer de l'utiliser directement
        if isinstance(chunks, RunResponse) and isinstance(chunks.content, str):
            if chunks.event == RunEvent.run_response:
                yield chunks.content
        elif isinstance(chunks, str):
            yield chunks


# Configuration des composants
def create_agent(user_id=None, api_key=None):
    """Crée et configure l'agent d'IA"""
    # Utilisation de la rotation des clés API pour distribuer la charge
    gemini_api_key = api_key or get_api_key()
    print(f"[DEBUG] Utilisation de la clé API: {gemini_api_key[:10]}...")

    # Configuration des composants
    cvs_base = create_knowledge_base()
    storage = create_storage(user_id)
    email_tool = EmailTool()
    
    return Agent(
        model=Gemini(api_key=gemini_api_key),
        storage=storage,
        knowledge=cvs_base, 
        tools=[email_tool],       
        add_datetime_to_instructions=True,
        read_chat_history=True,
        add_history_to_messages=True,
        read_tool_call_history=True,
        update_knowledge=True,
        search_knowledge=True,
        instructions=get_agent_instructions(),
        show_tool_calls=False,  # Désactiver l'affichage des tool_calls pour éviter la génération de code
    )


def create_agent_with_fresh_key(user_id=None):
    """Crée un agent avec une nouvelle clé API pour chaque requête"""
    # Sélectionner une nouvelle clé API pour chaque requête
    gemini_api_key = get_api_key()
    print(f"[DEBUG] Création d'agent avec nouvelle clé API: {gemini_api_key[:10]}...")
    
    return create_agent(user_id=user_id, api_key=gemini_api_key)


# Instanciation de l'agent
agent = create_agent()

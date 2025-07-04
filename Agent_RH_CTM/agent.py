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
from utils.env_config import GEMINI_API_KEY_12
from mcp_email_tool import EmailTool

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
def create_agent():
    """Crée et configure l'agent d'IA"""
    # Utilisation de la variable d'environnement pour la clé API
    gemini_api_key = GEMINI_API_KEY_12
    
    vector_db = LanceDb(
        table_name="cvs",
        uri="lancedb",
        search_type=SearchType.hybrid,
        embedder=OllamaEmbedder(id="nomic-embed-text", dimensions=768),
    )

    print(f"[DEBUG] Initializing knowledge base from path: 'txt'")
    cvs_base = TextKnowledgeBase(path="txt", vector_db=vector_db, num_documents=5)
      # Vérification de la base de connaissances (debug uniquement)
    #if os.environ.get("AGNO_DEBUG") == "True":
        #try:
            # Lister les fichiers dans le répertoire txt
            #print(f"[DEBUG] Files in txt directory:")
            #files = [f for f in os.listdir("txt") if f.endswith(".txt")]
            #print(f"[DEBUG] Found {len(files)} text files")
            
            # Vérifier spécifiquement le fichier FOUAD ESSELIMANI
            # fouad_file = "(CV)ESSELIMANIFOUAD.pdf.txt"
            # if fouad_file in files:
            #     print(f"[DEBUG] Found FOUAD ESSELIMANI file: {fouad_file}")
            #     # Test de recherche spécifique
            #     test_results = vector_db.search("FOUAD ESSELIMANI", limit=5)
            #     print(f"[DEBUG] Search results for 'FOUAD ESSELIMANI': {len(test_results)}")
            #     test_results = vector_db.search("27/08/2024", limit=5)
            #     print(f"[DEBUG] Search results for '27/08/2024': {len(test_results)}")
            #     test_results = vector_db.search("27/8/2024", limit=5)
            #     print(f"[DEBUG] Search results for '27/8/2024': {len(test_results)}")
            # else:
            #     print(f"[DEBUG] FOUAD ESSELIMANI file NOT FOUND in txt directory")
            
            # Test simple de recherche pour vérifier que la base fonctionne
            #if files:
                # Utiliser le premier fichier comme test plutôt qu'un nom codé en dur
                #test_term = os.path.splitext(files[0])[0]
                #print(f"[DEBUG] Testing search with first file name: '{test_term}'...")
                #test_results = vector_db.search(test_term, limit=5)
                #print(f"[DEBUG] Search results count: {len(test_results)}")
        #except Exception as e:
            #print(f"[DEBUG] Error during knowledge base verification: {e}")
    

    storage = SqliteStorage(
        table_name="agent_sessions", db_file="sqlite.db", auto_upgrade_schema=True
    )

    # Configuration de l'outil d'email
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
        instructions=[
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
            "Ne pas montrer la colonne 'VISIO' si ce n'est pas demandé",            "IMPORTANT: Chaque CV contient une date de réception au début du texte au format 'Date de réception : JJ/MM/AAAA à HH:MM'. Utiliser cette information pour filtrer les CV par date de réception.",            "RECHERCHE PAR DATE - RÈGLES SPÉCIFIQUES:",
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
    
        ],
        show_tool_calls=False,  # Désactiver l'affichage des tool_calls pour éviter la génération de code
    )


# Instanciation de l'agent
agent = create_agent()
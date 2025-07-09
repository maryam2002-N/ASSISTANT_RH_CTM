
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from agno.document.chunking.fixed import FixedSizeChunking
from agno.vectordb.search import SearchType
from agno.vectordb.pgvector import PgVector



# vector_db = LanceDb(
#     table_name="cvs",
#     uri="lancedb",
#     embedder=OllamaEmbedder(id="nomic-embed-text", dimensions=768),
# )

vector_db = PgVector(
        table_name="cvs_embeddings_bge_m3",
        db_url="postgresql://CTM:CTM1234@localhost:5532/Agent_CTM",
        embedder=OllamaEmbedder(id="bge-m3", dimensions=1024),
)

#

chunking_strategy = FixedSizeChunking(overlap=15)

knowledge_base = TextKnowledgeBase(
    path="./txt",
    vector_db=vector_db,
    chunking_strategy=chunking_strategy
)

if __name__ == "__main__":
    try:
        knowledge_base.load()
        print("Knowledge base loaded successfully.")
    except Exception as e:
        print(f"Error loading knowledge base: {e}")

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Lightweight embedding model
create_embedding = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

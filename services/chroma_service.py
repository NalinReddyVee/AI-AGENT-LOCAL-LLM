import chromadb
from chromadb.config import Settings
from embeddings import create_embedding  # Your custom embedding function

# ChromaDB persistent directory
CHROMA_DIR = "./chroma_storage"

# Initialize persistent client
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

# Get or create a collection with embedding support
def get_collection(name: str):
    return chroma_client.get_or_create_collection(
        name=name,
        embedding_function=create_embedding
    )

# Delete a document by ID from a collection
def delete_document(collection_name: str, doc_id: str):
    collection = get_collection(collection_name)
    collection.delete(ids=[doc_id])

# Delete the entire collection
def delete_collection(collection_name: str):
    chroma_client.delete_collection(name=collection_name)

# List all collection names
def list_collections():
    return [c.name for c in chroma_client.list_collections()]

# Get all documents (with IDs) from a collection
def get_all_documents(collection_name: str):
    collection = get_collection(collection_name)
    # By default, Chroma returns up to 100 docs
    # Use limit=None to fetch all
    return collection.get(include=['documents', 'ids'])

# Check if a document exists by ID
def document_exists(collection_name: str, doc_id: str):
    collection = get_collection(collection_name)
    result = collection.get(ids=[doc_id], include=['documents'])
    return bool(result['documents'])

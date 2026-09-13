import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import config


def get_embeddings_model():
    """Get embeddings model"""
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    return embeddings


def create_vector_store(documents, embedding_model):
    """Create and save vector store from documents"""
    os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
    
    try:
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_model
        )
        vector_store.save_local(config.VECTOR_STORE_PATH)
        return vector_store
    except Exception as e:
        raise Exception(f"Failed to create vector store: {str(e)}")


def load_vector_store(embedding_model):
    """Load existing vector store"""
    try:
        if os.path.exists(config.VECTOR_STORE_PATH):
            vector_store = FAISS.load_local(
                config.VECTOR_STORE_PATH,
                embedding_model,
                allow_dangerous_deserialization=True
            )
            return vector_store
        return None
    except Exception as e:
        print(f"Failed to load vector store: {str(e)}")
        return None


def retrieve_documents(query, vector_store, k=4):
    """Retrieve relevant documents from vector store"""
    if vector_store is None:
        return []
    
    try:
        results = vector_store.similarity_search(query, k=k)
        return results
    except Exception as e:
        print(f"Failed to retrieve documents: {str(e)}")
        return []

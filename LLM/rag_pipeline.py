from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import os
import config
from embeddings import get_embeddings_model, create_vector_store, load_vector_store


class RAGPipeline:
    """RAG Pipeline for PDF processing and retrieval"""
    
    def __init__(self):
        self.embeddings_model = get_embeddings_model()
        self.vector_store = load_vector_store(self.embeddings_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def ingest_pdf(self, pdf_path: str):
        """Ingest and process PDF"""
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Split documents
            split_docs = self.text_splitter.split_documents(documents)
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = create_vector_store(split_docs, self.embeddings_model)
            else:
                # Add new documents to existing store
                self.vector_store.add_documents(split_docs)
            
            return len(split_docs), "PDF ingested successfully"
        
        except Exception as e:
            return 0, f"Error ingesting PDF: {str(e)}"
    
    def retrieve_context(self, query: str, k: int = 4) -> str:
        """Retrieve context from vector store"""
        if self.vector_store is None:
            return ""
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            context = "\n\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return ""
    
    def rag_query(self, query: str) -> dict:
        """Execute RAG query"""
        context = self.retrieve_context(query)
        
        return {
            "query": query,
            "context": context,
            "has_context": len(context) > 0
        }

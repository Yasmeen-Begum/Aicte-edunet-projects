"""
ChromaDB vector store management
"""

import logging
from typing import List, Dict, Any
import uuid

import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import CONFIG

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages ChromaDB vector store operations"""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=CONFIG["vectorstore"]["persist_directory"],
            anonymized_telemetry=False
        ))
        self.collection_name = CONFIG["vectorstore"]["collection_name"]
        self.embeddings = HuggingFaceEmbeddings(
            model_name=CONFIG["embeddings"]["model_name"]
        )
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get existing collection"""
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(self.collection_name)
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, chunks: List[str], metadata: Dict[str, Any]) -> str:
        """Add document chunks to vector store"""
        doc_id = str(uuid.uuid4())
        
        # Generate embeddings
        embeddings = self.embeddings.embed_documents(chunks)
        
        # Prepare metadata for each chunk
        metadatas = [{"doc_id": doc_id, "chunk_index": i, **metadata} 
                     for i in range(len(chunks))]
        
        # Add to collection
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks to vector store with doc_id: {doc_id}")
        return doc_id
    
    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """Query vector store for relevant chunks"""
        query_embedding = self.embeddings.embed_query(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

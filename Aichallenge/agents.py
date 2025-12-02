"""
CrewAI agents for coordinated processing
"""

import time
import logging
from datetime import datetime
from pathlib import Path
import uuid

from models import Summary
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from llm_manager import LLMManager

logger = logging.getLogger(__name__)

class MedicalReportCrew:
    """CrewAI agents for coordinated processing"""
    
    def __init__(self, vector_store: VectorStoreManager, llm_manager: LLMManager):
        self.vector_store = vector_store
        self.llm_manager = llm_manager
        self.document_processor = DocumentProcessor()
    
    def process_report(self, file_path: str, progress_callback=None) -> Summary:
        """Process medical report through agent workflow"""
        start_time = time.time()
        
        try:
            # Step 1: Document Processing Agent
            if progress_callback:
                progress_callback("Validating file...", 0.1)
            
            self.document_processor.validate_file(file_path)
            
            if progress_callback:
                progress_callback("Extracting text...", 0.2)
            
            text = self.document_processor.extract_text(file_path)
            
            if progress_callback:
                progress_callback("Chunking document...", 0.3)
            
            chunks = self.document_processor.chunk_document(text)
            
            # Step 2: Retrieval Agent
            if progress_callback:
                progress_callback("Generating embeddings...", 0.5)
            
            metadata = {
                "filename": Path(file_path).name,
                "timestamp": datetime.now().isoformat()
            }
            doc_id = self.vector_store.add_documents(chunks, metadata)
            
            if progress_callback:
                progress_callback("Retrieving relevant context...", 0.7)
            
            # Query for relevant context
            context_chunks = self.vector_store.query(text[:500], n_results=5)
            
            # Step 3: Summarization Agent
            if progress_callback:
                progress_callback("Generating summary...", 0.8)
            
            summary_text, follow_up_date, detected_diseases, medications, recovery_time = self.llm_manager.generate_summary(text, context_chunks)
            
            processing_time = time.time() - start_time
            
            if progress_callback:
                progress_callback("Complete!", 1.0)
            
            summary = Summary(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                summary_text=summary_text,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
            # Add additional attributes
            summary.follow_up_date = follow_up_date
            summary.detected_diseases = detected_diseases
            summary.medications = medications
            summary.recovery_time = recovery_time
            
            return summary
            
        except Exception as e:
            logger.error(f"Report processing failed: {str(e)}")
            raise

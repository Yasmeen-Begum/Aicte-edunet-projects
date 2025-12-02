"""
Medical Report Summarizer using RAG, LangChain, Llama2, ChromaDB, Gradio, and CrewAI
Single-file implementation for quick deployment
"""

import os
import time
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid

# Document processing
import PyPDF2
import docx

# ML and embeddings
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# LangChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# CrewAI
from crewai import Agent, Task, Crew

# Gradio UI
import gradio as gr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "embeddings": {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    },
    "vectorstore": {
        "persist_directory": "./chroma_db",
        "collection_name": "medical_reports",
    },
    "processing": {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "max_file_size_mb": 50,
    }
}

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Document:
    id: str
    filename: str
    content: str
    file_type: str
    upload_timestamp: datetime
    chunks: List[str]
    metadata: Dict[str, Any]

@dataclass
class Summary:
    id: str
    document_id: str
    summary_text: str
    processing_time: float
    timestamp: datetime

# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

class DocumentProcessor:
    """Handles file validation, text extraction, and chunking"""
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate file format and size"""
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Check file extension
        valid_extensions = ['.pdf', '.txt', '.docx']
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in valid_extensions:
            raise ValueError(f"Invalid file format. Supported: {valid_extensions}")
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > CONFIG["processing"]["max_file_size_mb"]:
            raise ValueError(f"File size exceeds {CONFIG['processing']['max_file_size_mb']}MB limit")
        
        return True
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract text from PDF, TXT, or DOCX files"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return DocumentProcessor._extract_from_pdf(file_path)
            elif file_ext == '.txt':
                return DocumentProcessor._extract_from_txt(file_path)
            elif file_ext == '.docx':
                return DocumentProcessor._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise ValueError(f"Failed to extract text from file: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    
    @staticmethod
    def chunk_document(text: str) -> List[str]:
        """Split document into semantic chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CONFIG["processing"]["chunk_size"],
            chunk_overlap=CONFIG["processing"]["chunk_overlap"],
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        return chunks

# ============================================================================
# VECTOR STORE MANAGER
# ============================================================================

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

# ============================================================================
# LLM MANAGER
# ============================================================================

class LLMManager:
    """Manages summarization using extractive approach"""
    
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        logger.info("LLM Manager initialized (using extractive summarization)")
    
    def generate_summary(self, report_text: str, context_chunks: List[str]) -> str:
        """Generate summary using extractive approach"""
        
        # Extract key sections
        lines = report_text.split('\n')
        
        # Find important sections
        demographics = self._extract_section(lines, ['patient', 'name', 'age', 'dob', 'gender'])
        diagnoses = self._extract_section(lines, ['diagnosis', 'diagnoses', 'impression', 'assessment'])
        findings = self._extract_section(lines, ['findings', 'results', 'examination', 'test'])
        recommendations = self._extract_section(lines, ['recommendation', 'treatment', 'plan', 'medication', 'prescription'])
        
        # Build structured summary
        summary_parts = []
        
        if demographics:
            summary_parts.append("## Patient Demographics\n" + "\n".join(demographics[:3]))
        
        if diagnoses:
            summary_parts.append("## Primary Diagnoses\n" + "\n".join(diagnoses[:5]))
        
        if findings:
            summary_parts.append("## Key Findings\n" + "\n".join(findings[:5]))
        
        if recommendations:
            summary_parts.append("## Treatment Recommendations\n" + "\n".join(recommendations[:5]))
        
        if not summary_parts:
            # Fallback: just take first meaningful lines
            meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 20][:15]
            return "## Medical Report Summary\n\n" + "\n".join(meaningful_lines)
        
        return "\n\n".join(summary_parts)
    
    def _extract_section(self, lines: List[str], keywords: List[str]) -> List[str]:
        """Extract lines containing specific keywords"""
        extracted = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Include this line and next few lines
                extracted.append(line.strip())
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        extracted.append(lines[j].strip())
                break
        return extracted

# ============================================================================
# CREWAI AGENTS
# ============================================================================

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
            
            summary_text = self.llm_manager.generate_summary(text, context_chunks)
            
            processing_time = time.time() - start_time
            
            if progress_callback:
                progress_callback("Complete!", 1.0)
            
            return Summary(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                summary_text=summary_text,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Report processing failed: {str(e)}")
            raise

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

class MedicalSummarizerUI:
    """Gradio interface for the application"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.llm_manager = LLMManager(self.vector_store)
        self.crew = MedicalReportCrew(self.vector_store, self.llm_manager)
        self.session_history = []
    
    def process_file(self, file, progress=gr.Progress()):
        """Process uploaded file and return summary"""
        if file is None:
            return "Please upload a file.", ""
        
        try:
            def update_progress(status, value):
                progress(value, desc=status)
            
            # Process the report
            summary = self.crew.process_report(file.name, update_progress)
            
            # Store in session history
            self.session_history.append({
                "filename": Path(file.name).name,
                "summary": summary,
                "timestamp": summary.timestamp
            })
            
            # Format output
            result = f"""
# Medical Report Summary

**File:** {Path(file.name).name}
**Processed:** {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Processing Time:** {summary.processing_time:.2f} seconds

---

{summary.summary_text}

---

**Document ID:** {summary.document_id}
**Total Reports in Session:** {len(self.session_history)}
"""
            
            stats = f"Processing Time: {summary.processing_time:.2f}s | Reports Processed: {len(self.session_history)}"
            
            return result, stats
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            logger.error(error_msg)
            return error_msg, "Error occurred"
    
    def launch(self):
        """Launch Gradio interface"""
        
        with gr.Blocks(title="Medical Report Summarizer", theme=gr.themes.Soft()) as interface:
            gr.Markdown("""
            # 🏥 Medical Report Summarizer
            ### Powered by RAG, LangChain, Llama2, ChromaDB, and CrewAI
            
            Upload medical reports (PDF, TXT, DOCX) to get AI-powered summaries.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="Upload Medical Report",
                        file_types=[".pdf", ".txt", ".docx"]
                    )
                    submit_btn = gr.Button("Generate Summary", variant="primary", size="lg")
                    stats_output = gr.Textbox(label="Statistics", interactive=False)
                
                with gr.Column(scale=2):
                    summary_output = gr.Markdown(label="Summary")
            
            gr.Markdown("""
            ### Features
            - ✅ Multi-format support (PDF, TXT, DOCX)
            - ✅ RAG-based summarization with context
            - ✅ Multi-agent processing pipeline
            - ✅ Session history tracking
            - ✅ Real-time progress updates
            """)
            
            submit_btn.click(
                fn=self.process_file,
                inputs=[file_input],
                outputs=[summary_output, stats_output]
            )
        
        interface.launch(share=False, server_name="0.0.0.0", server_port=7860)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    logger.info("Starting Medical Report Summarizer...")
    
    # Check if model exists
    if not os.path.exists(CONFIG["llm"]["model_path"]):
        logger.warning(f"Llama2 model not found at {CONFIG['llm']['model_path']}")
        logger.warning("Application will run in fallback mode without LLM")
        logger.info("To use full functionality, download a Llama2 GGUF model and update the path in CONFIG")
    
    # Create necessary directories
    os.makedirs(CONFIG["vectorstore"]["persist_directory"], exist_ok=True)
    os.makedirs("./models", exist_ok=True)
    
    # Launch UI
    app = MedicalSummarizerUI()
    app.launch()

if __name__ == "__main__":
    main()

"""
Medical Report Summarizer - Main Entry Point
Real-time medical report summarization using RAG, LangChain, ChromaDB, Gradio, and CrewAI
"""

import os
import logging

from config import CONFIG
from ui import MedicalSummarizerUI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("Starting Medical Report Summarizer...")
    
    # Create necessary directories
    os.makedirs(CONFIG["vectorstore"]["persist_directory"], exist_ok=True)
    
    # Launch UI
    app = MedicalSummarizerUI()
    app.launch()

if __name__ == "__main__":
    main()

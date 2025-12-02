# Medical Report Summarizer

Real-time medical report summarization using RAG, LangChain, Llama2, ChromaDB, Gradio, and CrewAI.

## Features

- **Multi-format Support**: PDF, TXT, DOCX, JPG, PNG (with OCR)
- **RAG-based Summarization**: Context-aware summaries using retrieval-augmented generation
- **Multi-agent Processing**: CrewAI agents for document processing, retrieval, and summarization
- **Personalized Food Recommendations**: Dietary suggestions based on detected conditions
- **PDF Export**: Download summaries as professional PDF documents
- **Vector Storage**: ChromaDB for persistent embeddings
- **Web Interface**: Clean Gradio UI with real-time progress
- **Session History**: Track all processed reports
- **OCR Support**: Extract text from medical report images

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (for image support)

To enable image upload and OCR text extraction, install Tesseract OCR:

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Or use Chocolatey: `choco install tesseract`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

See [TESSERACT_SETUP.md](TESSERACT_SETUP.md) for detailed installation instructions.

**Note:** The application works without Tesseract for PDF, TXT, and DOCX files. Image support requires Tesseract OCR.

### 3. Update Configuration (Optional)

Edit `config.py` to customize settings:

```python
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
```

### 4. Run the Application

```bash
python main.py
```

The application will launch at `http://localhost:7860`

## Usage

1. Open the web interface at `http://localhost:7860`
2. Upload a medical report:
   - **Documents**: PDF, TXT, DOCX
   - **Images**: JPG, PNG (requires Tesseract OCR)
3. Click "Generate Summary"
4. View the AI-generated summary with:
   - Patient demographics
   - Primary diagnoses
   - Key findings
   - Treatment recommendations
   - Personalized food recommendations
5. Download the summary as a PDF

## Configuration

Edit `config.py` to customize settings:

```python
CONFIG = {
    "embeddings": {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    },
    "vectorstore": {
        "persist_directory": "./chroma_db",
        "collection_name": "medical_reports",
    },
    "processing": {
        "chunk_size": 500,          # Size of text chunks
        "chunk_overlap": 50,        # Overlap between chunks
        "max_file_size_mb": 50,     # Maximum file size
    }
}
```

## System Requirements

- **Minimum**: 8GB RAM, CPU
- **Recommended**: 16GB RAM for better performance
- **Disk Space**: 2GB for embeddings and vector store

## Troubleshooting

### Out of Memory
- Reduce `chunk_size` in config.py
- Process smaller files
- Close other applications

### Slow Processing
- First run downloads embedding models (one-time)
- Subsequent runs are faster
- Reduce number of retrieved chunks in vector_store.py

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

### Port Already in Use
Edit `ui.py` and change the port:
```python
interface.launch(share=False, server_name="0.0.0.0", server_port=7861)
```

## Architecture

```
User Upload → Document Agent → Retrieval Agent → Summarization Agent → Display
                    ↓                ↓                    ↓
              Text Extract      ChromaDB Store      Llama2 + RAG
```

## File Structure

```
.
├── main.py                 # Main entry point
├── config.py              # Configuration settings
├── models.py              # Data models
├── document_processor.py  # File upload & text extraction
├── vector_store.py        # ChromaDB vector storage
├── llm_manager.py         # Summarization logic
├── agents.py              # CrewAI multi-agent workflow
├── ui.py                  # Gradio web interface
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── chroma_db/            # Vector store (auto-created)
```

## License

MIT License

## Notes

- This is a demo application for educational purposes
- Not intended for clinical use without proper validation
- Ensure HIPAA compliance if handling real patient data
- Always verify AI-generated summaries with medical professionals

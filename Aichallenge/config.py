"""
Configuration settings for Medical Report Summarizer
"""

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

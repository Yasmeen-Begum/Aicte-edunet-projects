"""
Data models for Medical Report Summarizer
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

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

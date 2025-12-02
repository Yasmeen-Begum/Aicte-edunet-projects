"""
Document processing: file validation, text extraction, and chunking
"""

import os
from pathlib import Path
from typing import List
import logging

import PyPDF2
import docx
from PIL import Image
import pytesseract
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CONFIG

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles file validation, text extraction, and chunking"""
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate file format and size"""
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Check file extension
        valid_extensions = ['.pdf', '.txt', '.docx', '.jpg', '.jpeg', '.png', '.webp']
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
        """Extract text from PDF, TXT, DOCX, or Image files"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return DocumentProcessor._extract_from_pdf(file_path)
            elif file_ext == '.txt':
                return DocumentProcessor._extract_from_txt(file_path)
            elif file_ext == '.docx':
                return DocumentProcessor._extract_from_docx(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                return DocumentProcessor._extract_from_image(file_path)
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
    def _extract_from_image(file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Open image
            image = Image.open(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                raise ValueError("No text could be extracted from the image")
            
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise ValueError(f"Failed to extract text from image. Make sure Tesseract OCR is installed: {str(e)}")
    
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

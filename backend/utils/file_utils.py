"""
File handling utilities for document processing.
"""
import os
import PyPDF2
import docx
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from config import get_settings

settings = get_settings()
print("\n\n")


def ensure_upload_dir():
    """Ensure the upload directory exists."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def validate_file(file: UploadFile, allowed_extensions: list[str] = None) -> None:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file
        allowed_extensions: List of allowed file extensions
        
    Raises:
        HTTPException: If validation fails
    """
    if allowed_extensions is None:
        allowed_extensions = [".pdf", ".docx", ".doc"]
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size (if we can)
    if hasattr(file, 'size') and file.size:
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )


async def save_upload_file(file: UploadFile, user_id: int) -> Tuple[str, int]:
    """
    Save an uploaded file to disk.
    
    Args:
        file: Uploaded file
        user_id: ID of the user uploading
        
    Returns:
        Tuple of (file_path, file_size)
    """
    ensure_upload_dir()
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    safe_filename = f"user_{user_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_size = len(content)
    
    return file_path, file_size


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    try:
        text_parts = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n".join(text_parts)
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted text
    """
    try:
        doc = docx.Document(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text_parts.append(paragraph.text)
        
        return "\n".join(text_parts)
    
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_file(file_path: str) -> Tuple[str, str]:
    """
    Extract text from a file (PDF or DOCX).
    
    Args:
        file_path: Path to file
        
    Returns:
        Tuple of (extracted_text, method_used)
    """
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == ".pdf":
        text = extract_text_from_pdf(file_path)
        method = "pypdf2"
    elif file_ext in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
        method = "python-docx"
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    return text, method

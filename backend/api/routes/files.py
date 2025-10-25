"""
File upload and management API endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
import shutil
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from utils.config import settings
from utils.logger import setup_logger
from services.file_processing import FileProcessor
from config.database import get_db
from models.document import Document
from services.embeddings.embedding_service import embed_document_chunks

router = APIRouter()
logger = setup_logger(__name__)
file_processor = FileProcessor()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a single file and save to database with embeddings
    
    Args:
        file: File to upload
        category: Optional category (e.g., 'financial', 'legal', 'market')
        description: Optional file description
        db: Database session
    
    Returns:
        File metadata, database ID, and upload status
    """
    try:
        # Validate file extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.get_allowed_extensions_list():
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_ext}' not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_id}_{file.filename}"
        
        # Create category subdirectory if specified
        if category:
            upload_path = Path(settings.UPLOAD_DIR) / category
        else:
            upload_path = Path(settings.UPLOAD_DIR)
        
        upload_path.mkdir(parents=True, exist_ok=True)
        file_path = upload_path / safe_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        # Check file size
        if file_size > settings.get_max_upload_size_bytes():
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Extract text content from file
        try:
            extracted_text = file_processor.extract_text(str(file_path))
        except Exception as e:
            logger.warning(f"Could not extract text from {safe_filename}: {str(e)}")
            extracted_text = ""
        
        # Create document record in database
        document = Document(
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_ext,
            file_size=file_size,
            document_type=category or "general",
            full_text=extracted_text,
            metadata_={
                "safe_filename": safe_filename,
                "description": description,
                "category": category
            },
            is_vectorized=False  # Will be set to True after embedding
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Generate embeddings in the background (non-blocking)
        embedding_status = "pending"
        try:
            if extracted_text:
                await embed_document_chunks(db, document.id)
                embedding_status = "completed"
                logger.info(f"Embeddings generated for document {document.id}")
        except Exception as e:
            logger.error(f"Error generating embeddings for {safe_filename}: {str(e)}")
            embedding_status = "failed"
        
        logger.info(f"File uploaded and saved to database: {safe_filename} (ID: {document.id})")
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "document_id": document.id,
            "file_id": file_id,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_type": file_ext,
            "category": category,
            "description": description,
            "text_extracted": bool(extracted_text),
            "embedding_status": embedding_status,
            "uploaded_at": document.upload_date.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        # Clean up file if database save failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/upload/batch")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    category: Optional[str] = Form(None)
):
    """
    Upload multiple files at once
    
    Args:
        files: List of files to upload
        category: Optional category for all files
    
    Returns:
        List of uploaded file metadata
    """
    results = []
    errors = []
    
    for file in files:
        try:
            # Validate file extension
            file_ext = file.filename.split('.')[-1].lower()
            if file_ext not in settings.get_allowed_extensions_list():
                errors.append({
                    "filename": file.filename,
                    "error": f"File type '{file_ext}' not allowed"
                })
                continue
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file_id}_{file.filename}"
            
            # Create category subdirectory if specified
            if category:
                upload_path = Path(settings.UPLOAD_DIR) / category
            else:
                upload_path = Path(settings.UPLOAD_DIR)
            
            upload_path.mkdir(parents=True, exist_ok=True)
            file_path = upload_path / safe_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            
            # Check file size
            if file_size > settings.get_max_upload_size_bytes():
                os.remove(file_path)
                errors.append({
                    "filename": file.filename,
                    "error": f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB"
                })
                continue
            
            logger.info(f"File uploaded successfully: {safe_filename}")
            
            results.append({
                "success": True,
                "file_id": file_id,
                "filename": file.filename,
                "safe_filename": safe_filename,
                "file_path": str(file_path),
                "file_size": file_size,
                "file_type": file_ext,
                "category": category,
                "uploaded_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "uploaded_count": len(results),
        "error_count": len(errors),
        "files": results,
        "errors": errors
    }


@router.get("/list")
async def list_files(category: Optional[str] = None):
    """
    List all uploaded files
    
    Args:
        category: Optional category filter
    
    Returns:
        List of files with metadata
    """
    try:
        if category:
            search_path = Path(settings.UPLOAD_DIR) / category
        else:
            search_path = Path(settings.UPLOAD_DIR)
        
        if not search_path.exists():
            return {
                "success": True,
                "files": [],
                "count": 0
            }
        
        files = []
        for file_path in search_path.rglob('*'):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
        
        return {
            "success": True,
            "files": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    """
    Delete a file by filename
    
    Args:
        filename: Filename or file_id to delete
    
    Returns:
        Deletion status
    """
    try:
        # Search for file with this name or ID
        upload_path = Path(settings.UPLOAD_DIR)
        deleted = False
        deleted_path = None
        
        for file_path in upload_path.rglob(f"*{filename}*"):
            if file_path.is_file():
                os.remove(file_path)
                deleted = True
                deleted_path = str(file_path)
                logger.info(f"File deleted: {file_path.name}")
                break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "deleted_file": deleted_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@router.get("/info/{file_id}")
async def get_file_info(file_id: str):
    """
    Get detailed information about a file
    
    Args:
        file_id: File ID
    
    Returns:
        Detailed file metadata
    """
    try:
        upload_path = Path(settings.UPLOAD_DIR)
        
        for file_path in upload_path.rglob(f"*{file_id}*"):
            if file_path.is_file():
                stat = file_path.stat()
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "extension": file_path.suffix,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
        
        raise HTTPException(status_code=404, detail="File not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")

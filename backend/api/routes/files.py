"""
File upload and management API endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
import shutil
from datetime import datetime
import uuid

from utils.config import settings
from utils.logger import setup_logger
from services.file_processor import FileProcessor

router = APIRouter()
logger = setup_logger(__name__)
file_processor = FileProcessor()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a single file
    
    Args:
        file: File to upload
        category: Optional category (e.g., 'financial', 'legal', 'market')
        description: Optional file description
    
    Returns:
        File metadata and upload status
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
        
        # Save file
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
        
        logger.info(f"File uploaded successfully: {safe_filename}")
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_type": file_ext,
            "category": category,
            "description": description,
            "uploaded_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
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


@router.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file by ID
    
    Args:
        file_id: File ID to delete
    
    Returns:
        Deletion status
    """
    try:
        # Search for file with this ID
        upload_path = Path(settings.UPLOAD_DIR)
        deleted = False
        
        for file_path in upload_path.rglob(f"*{file_id}*"):
            if file_path.is_file():
                os.remove(file_path)
                deleted = True
                logger.info(f"File deleted: {file_path.name}")
                break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "message": "File deleted successfully"
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

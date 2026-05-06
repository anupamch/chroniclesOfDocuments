import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import UploadFile
from app.services.mongodb import mongodb
from app.services.case_service import CaseService
from app.core.config import settings


class DocumentService:
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def validate_file(file: UploadFile) -> tuple[bool, str]:
        """Validate uploaded file"""
        
        # Check extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in DocumentService.ALLOWED_EXTENSIONS:
            return False, f"File type '{file_ext}' not allowed. Allowed: {', '.join(DocumentService.ALLOWED_EXTENSIONS)}"
        
        return True, ""
    
    @staticmethod
    def calculate_file_hash(content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    async def upload_documents(case_id: str, files: List[UploadFile], user_id: str) -> dict:
        """Upload multiple documents to a case"""
        
        # Validate case exists
        case = await CaseService.get_case(case_id)
        case_folder = Path(case["folder_path"])
        
        uploaded_files = []
        failed_files = []
        
        db = mongodb.get_db()
        
        for file in files:
            try:
                # Validate file
                is_valid, error_msg = DocumentService.validate_file(file)
                if not is_valid:
                    failed_files.append({
                        "file_name": file.filename,
                        "error": error_msg
                    })
                    continue
                
                # Read file content
                content = await file.read()
                file_size = len(content)
                
                # Check file size
                if file_size > DocumentService.MAX_FILE_SIZE:
                    failed_files.append({
                        "file_name": file.filename,
                        "error": f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds limit (50MB)"
                    })
                    continue
                
                # Calculate file hash
                file_hash = DocumentService.calculate_file_hash(content)
                
                # Check for duplicates
                if db is not None:
                    existing = await db.documents.find_one({
                        "case_id": case_id,
                        "file_hash": file_hash
                    })
                    if existing:
                        failed_files.append({
                            "file_name": file.filename,
                            "error": "Duplicate file already exists in this case"
                        })
                        continue
                
                # Generate document ID
                document_id = str(uuid.uuid4())
                
                # Save file
                file_ext = Path(file.filename).suffix.lower()
                safe_filename = f"{document_id}{file_ext}"
                file_path = case_folder / safe_filename
                
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Create document metadata
                doc_metadata = {
                    "document_id": document_id,
                    "case_id": case_id,
                    "file_name": file.filename,
                    "file_size": file_size,
                    "file_type": file_ext,
                    "file_hash": file_hash,
                    "file_path": str(file_path),
                    "status": "pending",
                    "created_by": user_id,
                    "uploaded_at": datetime.utcnow(),
                    "processed_at": None
                }
                
                # Save to MongoDB
                if db is not None:
                    await db.documents.insert_one(doc_metadata)
                
                uploaded_files.append({
                    "document_id": document_id,
                    "file_name": file.filename,
                    "file_size": file_size,
                    "status": "pending"
                })
                
            except Exception as e:
                failed_files.append({
                    "file_name": file.filename,
                    "error": str(e)
                })
        
        # Update case document count
        if db is not None:
            total_docs = await db.documents.count_documents({"case_id": case_id})
            await CaseService.update_case_document_count(case_id, total_docs)
        
        return {
            "case_id": case_id,
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "total_uploaded": len(uploaded_files),
            "total_failed": len(failed_files)
        }
    
    @staticmethod
    async def get_case_documents(case_id: str) -> List[dict]:
        """Get all documents for a case"""
        db = mongodb.get_db()
        if db is None:
            return []
        
        cursor = db.documents.find({"case_id": case_id})
        documents = await cursor.to_list(length=None)
        return documents
    
    @staticmethod
    async def get_document(case_id: str, document_id: str) -> dict:
        """Get document metadata by ID"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
            
        doc = await db.documents.find_one({"case_id": case_id, "document_id": document_id})
        if not doc:
            raise ValueError(f"Document '{document_id}' not found in case '{case_id}'")
            
        return doc
    @staticmethod
    async def update_document_status(document_id: str, status: str, error: str = None):
        """Update document processing status"""
        db = mongodb.get_db()
        if db is not None:
            update_data = {
                "status": status,
                "processed_at": datetime.utcnow()
            }
            if error:
                update_data["error"] = error
            
            await db.documents.update_one(
                {"document_id": document_id},
                {"$set": update_data}
            )

    @staticmethod
    async def delete_document(case_id: str, document_id: str) -> bool:
        """Permanently delete a single document from a case"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
        
        # Find document
        doc = await db.documents.find_one({"case_id": case_id, "document_id": document_id})
        if not doc:
            raise ValueError(f"Document '{document_id}' not found in case '{case_id}'")
        
        # Remove file from disk
        if doc.get("file_path"):
            file_path = Path(doc["file_path"])
            if file_path.exists():
                file_path.unlink()
                
        # Remove from MongoDB
        await db.documents.delete_one({"_id": doc["_id"]})
        
        # Update case document count
        total_docs = await db.documents.count_documents({"case_id": case_id})
        await CaseService.update_case_document_count(case_id, total_docs)
        
        # Note: If ChromaDB is used, it would be ideal to delete chunks here too.
        
        return True
        
    @staticmethod
    async def delete_all_documents(case_id: str) -> int:
        """Permanently delete all documents for a case"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
            
        # Get all documents
        cursor = db.documents.find({"case_id": case_id})
        docs = await cursor.to_list(length=None)
        
        deleted_count = 0
        for doc in docs:
            # Remove file from disk
            if doc.get("file_path"):
                file_path = Path(doc["file_path"])
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except OSError:
                        pass
            deleted_count += 1
            
        # Remove all from MongoDB
        await db.documents.delete_many({"case_id": case_id})
        
        # Update case document count to 0
        await CaseService.update_case_document_count(case_id, 0)
        
        return deleted_count

import uuid
from datetime import datetime
from pathlib import Path
from app.services.mongodb import mongodb
from app.core.config import settings


class CaseService:
    
    @staticmethod
    async def create_case(case_number: str, title: str, description: str = None, user_id: str = None) -> dict:
        """Create a new case and its folder"""
        
        # Check if case number already exists
        db = mongodb.get_db()
        if db is not None:
            existing = await db.cases.find_one({"case_number": case_number})
            if existing:
                raise ValueError(f"Case number '{case_number}' already exists")
        
        # Generate case ID
        case_id = str(uuid.uuid4())
        
        # Create case folder
        case_folder = Path(settings.input_folder) / case_id
        case_folder.mkdir(parents=True, exist_ok=True)
        
        # Create case document
        case_doc = {
            "case_id": case_id,
            "user_id": user_id,  # Associate with user
            "case_number": case_number,
            "title": title,
            "description": description,
            "status": "active",
            "folder_path": str(case_folder),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "total_documents": 0
        }
        
        # Save to MongoDB
        if db is not None:
            await db.cases.insert_one(case_doc)
        
        return case_doc
    
    @staticmethod
    async def get_case(case_id: str, user_id: str = None, is_admin: bool = False) -> dict:
        """Get case by ID, verifying ownership if not admin"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
        
        query = {"case_id": case_id}
        if user_id and not is_admin:
            query["user_id"] = user_id
            
        case = await db.cases.find_one(query)
        if not case:
            raise ValueError(f"Case '{case_id}' not found or access denied")
        
        return case
    
    @staticmethod
    async def update_case_document_count(case_id: str, count: int):
        """Update total document count for a case"""
        db = mongodb.get_db()
        if db is not None:
            await db.cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "total_documents": count,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

    @staticmethod
    async def list_cases(
        page: int = 1,
        page_size: int = 10,
        search: str = None,
        status: str = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        user_id: str = None,
        is_admin: bool = False
    ) -> dict:
        """List cases with pagination, search, and sorting"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")

        # Build query
        query = {}
        if user_id and not is_admin:
            query["user_id"] = user_id
            
        if search:
            query["$or"] = [
                {"case_number": {"$regex": search, "$options": "i"}},
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Exclude deleted cases by default, unless explicitly requested
        if status:
            query["status"] = status
        else:
            query["status"] = {"$ne": "deleted"}

        # Get total count
        total = await db.cases.count_documents(query)

        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size
        skip = (page - 1) * page_size

        # Determine sort direction: 1 = ascending, -1 = descending
        sort_direction = 1 if sort_order == "asc" else -1

        # Get cases with dynamic sorting
        cursor = db.cases.find(query).sort(sort_by, sort_direction).skip(skip).limit(page_size)
        cases = await cursor.to_list(length=None)

        # Convert ObjectId and datetime
        case_list = []
        for case in cases:
            case_list.append({
                "case_id": case.get("case_id"),
                "case_number": case.get("case_number"),
                "title": case.get("title"),
                "description": case.get("description"),
                "status": case.get("status"),
                "created_at": case.get("created_at"),
                "updated_at": case.get("updated_at"),
                "total_documents": case.get("total_documents", 0),
                "timeline_story": case.get("timeline_story")
            })

        return {
            "cases": case_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    async def get_case_with_documents(case_id: str) -> dict:
        """Get case details with all documents"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")

        # Get case
        case = await db.cases.find_one({"case_id": case_id})
        if not case:
            raise ValueError(f"Case '{case_id}' not found")

        # Get documents for this case
        docs_cursor = db.documents.find({"case_id": case_id})
        documents = await docs_cursor.to_list(length=None)

        doc_list = []
        for doc in documents:
            doc_list.append({
                "document_id": doc.get("document_id"),
                "case_id": doc.get("case_id"),
                "file_name": doc.get("file_name"),
                "file_size": doc.get("file_size"),
                "file_type": doc.get("file_type"),
                "file_path": doc.get("file_path"),
                "status": doc.get("status"),
                "uploaded_at": doc.get("uploaded_at")
            })

        return {
            "case": case,
            "documents": doc_list,
            "total_documents": len(doc_list)
        }

    @staticmethod
    async def delete_case(case_id: str) -> bool:
        """Soft delete a case by marking its status as deleted"""
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
            
        case = await db.cases.find_one({"case_id": case_id})
        if not case:
            raise ValueError(f"Case '{case_id}' not found")
            
        await db.cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "status": "deleted",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return True

import uuid
from datetime import datetime
from typing import Optional, List
from app.services.mongodb import mongodb
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    
    @staticmethod
    async def get_by_email(email: str) -> Optional[dict]:
        db = mongodb.get_db()
        if db is None:
            return None
        return await db.users.find_one({"email": email})

    @staticmethod
    async def get_by_phone(phone_number: str) -> Optional[dict]:
        """Get user by phone number"""
        db = mongodb.get_db()
        if db is None:
            return None
        return await db.users.find_one({"phone_number": phone_number})

    @staticmethod
    async def get_by_email_or_phone(identifier: str) -> Optional[dict]:
        """Get user by email or phone number (identifier)"""
        db = mongodb.get_db()
        if db is None:
            return None
        # Try to find by email first
        user = await db.users.find_one({"email": identifier})
        if user:
            return user
        # If not found, try by phone number
        user = await db.users.find_one({"phone_number": identifier})
        return user

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[dict]:
        db = mongodb.get_db()
        if db is None:
            return None
        return await db.users.find_one({"user_id": user_id})

    @staticmethod
    async def create_user(user_in: UserCreate) -> dict:
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
            
        # Check for existing email (including soft-deleted users)
        existing_user = await db.users.find_one({"email": user_in.email})
        if existing_user:
            if existing_user.get("is_deleted"):
                raise ValueError("This email was previously registered and cannot be reused")
            else:
                raise ValueError("User with this email already exists")
        
        # Check if phone number is already registered (if provided)
        if user_in.phone_number:
            existing_phone = await db.users.find_one({"phone_number": user_in.phone_number})
            if existing_phone:
                if existing_phone.get("is_deleted"):
                    raise ValueError("This phone number was previously registered and cannot be reused")
                else:
                    raise ValueError("User with this phone number already exists")
            
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_in.password)
        
        user_doc = {
            "user_id": user_id,
            "email": user_in.email,
            "full_name": user_in.full_name,
            "phone_number": user_in.phone_number,
            "role": user_in.role,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_deleted": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_doc)
        return user_doc

    @staticmethod
    async def update_user(user_id: str, user_in: UserUpdate) -> dict:
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
            
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise ValueError("User not found")
            
        update_data = {"updated_at": datetime.utcnow()}
        
        if user_in.full_name is not None:
            update_data["full_name"] = user_in.full_name

        if user_in.phone_number is not None:
            update_data["phone_number"] = user_in.phone_number
            
        if user_in.password is not None:
            update_data["hashed_password"] = get_password_hash(user_in.password)
            
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        return await db.users.find_one({"user_id": user_id})

    @staticmethod
    async def soft_delete_user(user_id: str) -> bool:
        db = mongodb.get_db()
        if db is None:
            raise ValueError("Database not available")
            
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_deleted": True, "is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise ValueError("User not found or already deleted")
            
        return True

    @staticmethod
    async def list_users() -> List[dict]:
        db = mongodb.get_db()
        if db is None:
            return []
            
        cursor = db.users.find({"is_deleted": False})
        return await cursor.to_list(length=None)

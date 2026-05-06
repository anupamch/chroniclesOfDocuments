from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.api.dependencies import get_current_active_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(current_admin: dict = Depends(get_current_active_admin)):
    """
    List all active users (Admin only).
    """
    users = await UserService.list_users()
    return users


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_admin: dict = Depends(get_current_active_admin)):
    """
    Soft delete a user (Admin only).
    """
    # Prevent self-deletion
    if current_admin["user_id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account"
        )
        
    try:
        await UserService.soft_delete_user(user_id)
        return {"status": "success", "message": "User soft deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

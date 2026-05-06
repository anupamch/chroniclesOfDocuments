from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password
from app.core.config import settings
from app.schemas.user import (
    UserCreate, UserResponse, UserUpdate, Token, 
    LoginRequest, LoginPhoneRequest, LoginEmailRequest
)
from app.services.user_service import UserService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    """
    Register a new user.
    """
    try:
        user = await UserService.create_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await UserService.get_by_email(email=form_data.username)
    if not user or user.get("is_deleted"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
        
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user["user_id"], expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/email", response_model=Token)
async def login_with_email(form_data: LoginEmailRequest):
    """
    Login using email address OR phone number and password.
    
    - **email**: User's email address (optional)
    - **phone_number**: User's phone number (optional)
    - **password**: User's password
    """
    # Validate that either email or phone number is provided
    try:
        form_data.validate_identifier()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Get user by email or phone number
    if form_data.email:
        user = await UserService.get_by_email(email=form_data.email)
        error_detail = "Incorrect email or password"
    else:
        user = await UserService.get_by_phone(phone_number=form_data.phone_number)
        error_detail = "Incorrect phone number or password"
    
    if not user or user.get("is_deleted"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail,
        )
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail,
        )
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
        
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user["user_id"], expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/phone", response_model=Token)
async def login_with_phone(form_data: LoginPhoneRequest):
    """
    Login using phone number and password.
    
    - **phone_number**: User's phone number
    - **password**: User's password
    """
    user = await UserService.get_by_phone(phone_number=form_data.phone_number)
    if not user or user.get("is_deleted"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
        )
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
        )
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
        
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user["user_id"], expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/flexible", response_model=Token)
async def login_flexible(form_data: LoginRequest):
    """
    Login using email OR phone number and password.
    
    The system will automatically detect whether the identifier is an email or phone number.
    
    - **identifier**: Email address or phone number
    - **password**: User's password
    """
    user = await UserService.get_by_email_or_phone(identifier=form_data.identifier)
    if not user or user.get("is_deleted"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
        )
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
        )
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
        
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user["user_id"], expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user profile.
    """
    user = await UserService.update_user(current_user["user_id"], user_in)
    return user

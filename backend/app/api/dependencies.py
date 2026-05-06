from fastapi import Depends, HTTPException, status, Query
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.user import TokenPayload
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except JWTError:
        raise credentials_exception
        
    user = await UserService.get_by_id(user_id=token_data.sub)
    if user is None or user.get("is_deleted"):
        raise credentials_exception
    if not user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


async def get_current_user_flexible(
    token_query: Optional[str] = Query(None, alias="token"),
    token_header: Optional[str] = Depends(oauth2_scheme_optional)
) -> dict:
    token = token_query or token_header
    
    if not token:
        print(f"[AUTH] No token found in query or header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    print(f"[AUTH] Validating token: {token[:10]}...")
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await UserService.get_by_id(user_id=user_id)
    if user is None or user.get("is_deleted") or not user.get("is_active"):
        raise credentials_exception
        
    return user


async def get_current_active_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Properties to receive via API on creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    role: str = "customer" # "admin" or "customer"


# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime


# Additional properties to return via API
class UserResponse(UserInDBBase):
    pass


# Properties to store in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Login with phone or email
class LoginRequest(BaseModel):
    """Login with email or phone number"""
    identifier: str = Field(..., description="Email or phone number")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "user@example.com",
                "password": "your_password"
            }
        }


class LoginPhoneRequest(BaseModel):
    """Login with phone number"""
    phone_number: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")


class LoginEmailRequest(BaseModel):
    """Login with email or phone number"""
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    password: str = Field(..., description="Password")
    
    def validate_identifier(self):
        """Ensure either email or phone number is provided"""
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone number must be provided")
        if self.email and self.phone_number:
            raise ValueError("Provide either email or phone number, not both")

"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=15, examples=["9876543210"])
    password: str = Field(..., min_length=4, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    customer_id: int
    name: str


class RegisterRequest(BaseModel):
    """Used by admin (or a registration endpoint) to create new customer accounts."""
    name: str = Field(..., min_length=1, max_length=120)
    mobile: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=4, max_length=128)

"""
Pydantic schemas for customer resources.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    mobile: str = Field(..., min_length=10, max_length=15)


class CustomerCreate(CustomerBase):
    password: str = Field(..., min_length=4, max_length=128)


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

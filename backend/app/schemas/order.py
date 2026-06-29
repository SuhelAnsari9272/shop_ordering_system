"""
Pydantic schemas for order and order-item resources.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import OrderStatus


# ---------- Request schemas ----------

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, le=50)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[OrderItemCreate]) -> list[OrderItemCreate]:
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ---------- Response schemas ----------

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_name: str
    customer_mobile: str
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut]


class OrderSummaryOut(BaseModel):
    """Lightweight representation used in list views."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_name: str
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    item_count: int

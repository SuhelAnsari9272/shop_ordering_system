"""
Import all models here so that Base.metadata is aware of every table
when create_all() is called, and so other modules can do
`from app.models import Customer, Product, Order, OrderItem`.
"""
from app.models.customer import Customer
from app.models.enums import VALID_STATUS_TRANSITIONS, OrderStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product

__all__ = [
    "Customer",
    "Product",
    "Order",
    "OrderItem",
    "OrderStatus",
    "VALID_STATUS_TRANSITIONS",
]

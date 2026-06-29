"""
Order routes.

Customers can create orders and view only their own orders.
Admins can view all orders and update order status.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_customer
from app.database import get_db
from app.models.customer import Customer
from app.models.enums import OrderStatus
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderItemOut, OrderOut, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


def _to_order_out(order: Order) -> OrderOut:
    """Convert an ORM Order (with loaded relationships) into the response schema."""
    items_out = [
        OrderItemOut(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else "Unknown",
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.unit_price * item.quantity,
        )
        for item in order.items
    ]
    return OrderOut(
        id=order.id,
        customer_id=order.customer_id,
        customer_name=order.customer.name if order.customer else "Unknown",
        customer_mobile=order.customer.mobile if order.customer else "",
        status=OrderStatus(order.status),
        total_amount=order.total_amount,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items_out,
    )


@router.post("", response_model=OrderOut, status_code=201, summary="Place a new order")
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
) -> OrderOut:
    service = OrderService(db)
    order = service.create_order(customer_id=current_customer.id, items=payload.items)
    order = service.get_order(order.id)  # reload with relationships for response
    return _to_order_out(order)


@router.get("", response_model=list[OrderOut], summary="List orders (own orders for customers, all for admin)")
def list_orders(
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    today_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
) -> list[OrderOut]:
    service = OrderService(db)

    if current_customer.is_admin:
        orders = service.list_all_orders(status=status_filter, today_only=today_only)
    else:
        orders = service.list_orders_for_customer(current_customer.id)
        if status_filter is not None:
            orders = [o for o in orders if o.status == status_filter.value]

    return [_to_order_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut, summary="Get a single order's details/status")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
) -> OrderOut:
    service = OrderService(db)
    if current_customer.is_admin:
        order = service.get_order(order_id)
    else:
        order = service.get_order_for_customer(order_id, current_customer.id)
    return _to_order_out(order)


@router.put("/{order_id}/status", response_model=OrderOut, summary="[Admin] Update an order's status")
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
) -> OrderOut:
    service = OrderService(db)
    order = service.update_status(order_id, payload.status)
    order = service.get_order(order.id)  # reload with relationships
    return _to_order_out(order)

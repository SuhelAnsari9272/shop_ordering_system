"""
Service layer for order placement, retrieval, and status management.

This is the core business-logic module of the system:
- Validates products before allowing them into an order
- Computes line-item subtotals and the order total server-side
  (never trusts client-supplied prices)
- Enforces a valid order-status state machine
- Enforces that customers can only access their own orders
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    AuthorizationError,
    InvalidStatusTransitionError,
    NotFoundError,
    ValidationError,
)
from app.core.logging_config import get_logger
from app.models.enums import VALID_STATUS_TRANSITIONS, OrderStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderItemCreate

logger = get_logger(__name__)


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Creation ----------

    def create_order(self, customer_id: int, items: list[OrderItemCreate]) -> Order:
        if not items:
            raise ValidationError("Order must contain at least one item")

        # Merge duplicate product_id entries (defensive, in case the client sends dupes)
        merged: dict[int, int] = {}
        for item in items:
            merged[item.product_id] = merged.get(item.product_id, 0) + item.quantity

        order_items: list[OrderItem] = []
        total = Decimal("0.00")

        for product_id, quantity in merged.items():
            product = self.db.get(Product, product_id)
            if product is None:
                raise NotFoundError(f"Product with id={product_id} not found")
            if not product.is_active:
                raise ValidationError(f"Product '{product.name}' is currently unavailable")

            unit_price = Decimal(str(product.price))
            subtotal = unit_price * quantity
            total += subtotal

            order_items.append(
                OrderItem(product_id=product.id, quantity=quantity, unit_price=unit_price)
            )

        order = Order(
            customer_id=customer_id,
            status=OrderStatus.RECEIVED.value,
            total_amount=total,
            items=order_items,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        logger.info(
            "Created order id=%s customer_id=%s total=%s items=%d",
            order.id, customer_id, total, len(order_items),
        )
        return order

    # ---------- Retrieval ----------

    def get_order(self, order_id: int) -> Order:
        order = (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer))
            .filter(Order.id == order_id)
            .first()
        )
        if order is None:
            raise NotFoundError(f"Order with id={order_id} not found")
        return order

    def get_order_for_customer(self, order_id: int, customer_id: int) -> Order:
        """Fetch an order and verify it belongs to the requesting customer."""
        order = self.get_order(order_id)
        if order.customer_id != customer_id:
            raise AuthorizationError("You do not have access to this order")
        return order

    def list_orders_for_customer(self, customer_id: int) -> list[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer))
            .filter(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def list_all_orders(
        self,
        status: OrderStatus | None = None,
        today_only: bool = False,
    ) -> list[Order]:
        """Used by the admin dashboard. Optionally filter by status and/or today's date."""
        query = self.db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer)
        )
        if status is not None:
            query = query.filter(Order.status == status.value)
        if today_only:
            today = datetime.now(timezone.utc).date()
            query = query.filter(Order.created_at >= datetime(today.year, today.month, today.day, tzinfo=timezone.utc))
        return query.order_by(Order.created_at.desc()).all()

    # ---------- Status updates ----------

    def update_status(self, order_id: int, new_status: OrderStatus) -> Order:
        order = self.get_order(order_id)
        current_status = OrderStatus(order.status)

        if new_status == current_status:
            # Idempotent no-op: allow re-setting the same status without error
            return order

        allowed_next = VALID_STATUS_TRANSITIONS.get(current_status, set())
        if new_status not in allowed_next:
            raise InvalidStatusTransitionError(
                f"Cannot change order status from {current_status.value} to {new_status.value}"
            )

        order.status = new_status.value
        self.db.commit()
        self.db.refresh(order)
        logger.info("Order id=%s status changed %s -> %s", order_id, current_status.value, new_status.value)
        return order

    # ---------- Dashboard metrics ----------

    def get_today_metrics(self) -> dict:
        orders_today = self.list_all_orders(today_only=True)
        pending_statuses = {OrderStatus.RECEIVED.value, OrderStatus.PREPARING.value, OrderStatus.READY.value}
        return {
            "total_orders_today": len(orders_today),
            "pending_orders": sum(1 for o in orders_today if o.status in pending_statuses),
            "completed_orders": sum(1 for o in orders_today if o.status == OrderStatus.COMPLETED.value),
        }

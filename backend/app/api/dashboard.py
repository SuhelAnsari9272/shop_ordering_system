"""
Admin dashboard metrics route.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.customer import Customer
from app.services.order_service import OrderService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", summary="[Admin] Today's order metrics for the dashboard")
def get_metrics(
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
) -> dict:
    service = OrderService(db)
    return service.get_today_metrics()

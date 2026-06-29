"""
Customer routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_customer
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerOut
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/me", response_model=CustomerOut, summary="Get the logged-in customer's profile")
def get_my_profile(current_customer: Customer = Depends(get_current_customer)) -> Customer:
    return current_customer


@router.get("", response_model=list[CustomerOut], summary="[Admin] List all customers")
def list_customers(
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
) -> list[Customer]:
    return db.query(Customer).order_by(Customer.created_at.desc()).all()


@router.post("", response_model=CustomerOut, status_code=201, summary="[Admin] Register a new customer")
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
) -> Customer:
    service = CustomerService(db)
    return service.create_customer(name=payload.name, mobile=payload.mobile, password=payload.password)

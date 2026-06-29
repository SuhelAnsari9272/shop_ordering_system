"""
Authentication routes: login issues a JWT for both customers and the admin
(the admin is simply a Customer row with is_admin=True).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.core.security import create_access_token
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.customer_service import CustomerService

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, summary="Login with mobile number and password")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = CustomerService(db)
    customer = service.authenticate(mobile=payload.mobile, password=payload.password)

    role = "admin" if customer.is_admin else "customer"
    token = create_access_token(subject=customer.mobile, role=role)

    logger.info("Login success mobile=%s role=%s", customer.mobile, role)

    return TokenResponse(
        access_token=token,
        role=role,
        customer_id=customer.id,
        name=customer.name,
    )

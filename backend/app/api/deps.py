"""
Shared FastAPI dependencies: DB session injection, JWT-based current-user
resolution, and admin-only authorization guard.
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.customer import Customer
from app.services.customer_service import CustomerService

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Customer:
    """
    Resolves the JWT bearer token into the authenticated Customer row.
    Used as a dependency on every protected route.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    mobile = payload.get("sub")
    if mobile is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    service = CustomerService(db)
    customer = service.get_by_mobile(mobile)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    if not customer.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    return customer


def get_current_admin(
    current_customer: Customer = Depends(get_current_customer),
) -> Customer:
    """Guard for admin-only routes. Requires a valid token AND is_admin=True."""
    if not current_customer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges",
        )
    return current_customer

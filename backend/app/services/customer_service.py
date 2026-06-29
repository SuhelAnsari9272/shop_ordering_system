"""
Service layer for customer authentication and lookup.

Keeping this logic out of the route handlers makes it independently
testable and reusable (e.g. by the admin bootstrap routine on startup).
"""
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AlreadyExistsError,
    InactiveAccountError,
    InvalidCredentialsError,
    NotFoundError,
)
from app.core.logging_config import get_logger
from app.core.security import hash_password, verify_password
from app.models.customer import Customer

logger = get_logger(__name__)


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: int) -> Customer:
        customer = self.db.get(Customer, customer_id)
        if customer is None:
            raise NotFoundError(f"Customer with id={customer_id} not found")
        return customer

    def get_by_mobile(self, mobile: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.mobile == mobile).first()

    def create_customer(
        self, name: str, mobile: str, password: str, is_admin: bool = False
    ) -> Customer:
        existing = self.get_by_mobile(mobile)
        if existing is not None:
            raise AlreadyExistsError(f"A customer with mobile {mobile} already exists")

        customer = Customer(
            name=name.strip(),
            mobile=mobile.strip(),
            password_hash=hash_password(password),
            is_active=True,
            is_admin=is_admin,
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        logger.info("Created customer id=%s mobile=%s is_admin=%s", customer.id, customer.mobile, is_admin)
        return customer

    def authenticate(self, mobile: str, password: str) -> Customer:
        """
        Validate mobile + password. Raises InvalidCredentialsError on mismatch
        and InactiveAccountError if the account has been deactivated.
        We intentionally do not distinguish "mobile not found" from "wrong
        password" in the error message, to avoid leaking which mobiles are registered.
        """
        customer = self.get_by_mobile(mobile)
        if customer is None or not verify_password(password, customer.password_hash):
            raise InvalidCredentialsError("Invalid mobile number or password")

        if not customer.is_active:
            raise InactiveAccountError("This account has been deactivated. Contact the shop.")

        return customer

    def ensure_admin_exists(self, name: str, mobile: str, password: str) -> Customer:
        """
        Idempotent bootstrap: creates the admin account if it doesn't exist yet.
        Called once on application startup.
        """
        existing = self.get_by_mobile(mobile)
        if existing is not None:
            if not existing.is_admin:
                existing.is_admin = True
                self.db.commit()
                logger.info("Promoted existing customer mobile=%s to admin", mobile)
            return existing

        return self.create_customer(name=name, mobile=mobile, password=password, is_admin=True)

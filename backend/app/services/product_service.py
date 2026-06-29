"""
Service layer for product catalog operations.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.models.product import Product

logger = get_logger(__name__)


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def list_active_products(self) -> list[Product]:
        return (
            self.db.query(Product)
            .filter(Product.is_active.is_(True))
            .order_by(Product.id.asc())
            .all()
        )

    def list_all_products(self) -> list[Product]:
        return self.db.query(Product).order_by(Product.id.asc()).all()

    def get_by_id(self, product_id: int) -> Product:
        product = self.db.get(Product, product_id)
        if product is None:
            raise NotFoundError(f"Product with id={product_id} not found")
        return product

    def create_product(self, name: str, description: str, price, is_active: bool = True) -> Product:
        product = Product(name=name.strip(), description=description, price=price, is_active=is_active)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        logger.info("Created product id=%s name=%s", product.id, product.name)
        return product

    def seed_if_empty(self, default_products: list[dict]) -> None:
        """Populate the catalog with default items if no products exist yet."""
        count = self.db.query(Product).count()
        if count > 0:
            return
        for item in default_products:
            self.db.add(Product(**item))
        self.db.commit()
        logger.info("Seeded %d default products", len(default_products))

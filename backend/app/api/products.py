"""
Product routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_customer
from app.database import get_db
from app.models.customer import Customer
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOut], summary="List active products (customer menu)")
def list_products(
    db: Session = Depends(get_db),
    _current: Customer = Depends(get_current_customer),
) -> list:
    service = ProductService(db)
    return service.list_active_products()


@router.get("/all", response_model=list[ProductOut], summary="[Admin] List all products including inactive")
def list_all_products(
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
) -> list:
    service = ProductService(db)
    return service.list_all_products()


@router.get("/{product_id}", response_model=ProductOut, summary="Get a single product by id")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _current: Customer = Depends(get_current_customer),
):
    service = ProductService(db)
    return service.get_by_id(product_id)


@router.post("", response_model=ProductOut, status_code=201, summary="[Admin] Create a new product")
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
):
    service = ProductService(db)
    return service.create_product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        is_active=payload.is_active,
    )


@router.put("/{product_id}", response_model=ProductOut, summary="[Admin] Update a product")
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _admin: Customer = Depends(get_current_admin),
):
    service = ProductService(db)
    product = service.get_by_id(product_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

"""
FastAPI application entrypoint.

Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, customers, dashboard, orders, products
from app.api.error_handlers import status_code_for
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging_config import get_logger, setup_logging
from app.database import Base, SessionLocal, engine
from app.services.customer_service import CustomerService
from app.services.product_service import ProductService

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

DEFAULT_PRODUCTS = [
    {"name": "Veg Sandwich", "description": "Grilled sandwich with fresh vegetables and cheese", "price": 60, "is_active": True},
    {"name": "Chicken Roll", "description": "Spiced chicken wrapped in a soft paratha", "price": 90, "is_active": True},
    {"name": "Masala Dosa", "description": "Crispy dosa with spiced potato filling", "price": 80, "is_active": True},
    {"name": "Cold Coffee", "description": "Chilled coffee blended with milk and ice cream", "price": 70, "is_active": True},
    {"name": "Paneer Wrap", "description": "Paneer tikka wrapped in a soft tortilla", "price": 85, "is_active": True},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Starting up: creating database tables if they do not exist")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        customer_service = CustomerService(db)
        customer_service.ensure_admin_exists(
            name=settings.admin_name,
            mobile=settings.admin_mobile,
            password=settings.admin_password,
        )

        product_service = ProductService(db)
        product_service.seed_if_empty(DEFAULT_PRODUCTS)
    finally:
        db.close()

    logger.info("Startup complete")
    yield
    # --- Shutdown ---
    logger.info("Shutting down")


app = FastAPI(
    title="Shop Pre-Ordering System API",
    description="Phase-1 backend for a single-shop pre-order & pickup system.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: Streamlit apps run on different ports/origins, so allow them through.
# For a single-shop internal tool this permissive policy is acceptable;
# tighten allow_origins for a public-facing deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Global handler: converts domain exceptions into clean HTTP responses."""
    logger.warning("AppError on %s %s: %s", request.method, request.url.path, exc.message)
    return JSONResponse(status_code=status_code_for(exc), content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all so unexpected errors never leak stack traces to clients."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"], summary="Health check")
def health_check() -> dict:
    return {"status": "ok", "service": "shop-ordering-system"}

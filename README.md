# 🛍️ Shop Pre-Ordering System — Phase 1

A production-style **pre-order & pickup system** for a small food shop. Registered
customers place orders ahead of time so the shop can prepare food in advance and
reduce in-store waiting time.

> **This is NOT a delivery app.** There is no delivery address, courier, or live
> tracking. Customers order ahead, the shop prepares the food, and the customer
> picks it up in person.

---

## 1. Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│  Customer Streamlit  │     │   Admin Streamlit    │
│   App (port 8501)    │     │   App (port 8502)    │
└──────────┬───────────┘     └──────────┬───────────┘
           │         REST + JWT          │
           └──────────────┬──────────────┘
                           ▼
                 ┌───────────────────┐
                 │   FastAPI Backend  │
                 │    (port 8000)     │
                 │  ─────────────────│
                 │  Routes → Services │
                 │  → SQLAlchemy ORM  │
                 └─────────┬──────────┘
                           ▼
                    ┌─────────────┐
                    │   SQLite    │
                    └─────────────┘
```

**Design principles applied:**
- **Service layer pattern** — all business logic (auth, order totals, status
  state machine) lives in `app/services/`, never inside route handlers.
- **Dependency injection** — DB sessions and the authenticated user are
  injected via FastAPI `Depends()`.
- **Domain exceptions** — services raise typed exceptions
  (`NotFoundError`, `ValidationError`, etc.) that a global FastAPI exception
  handler converts into proper HTTP status codes, so routes stay thin.
- **Server-side pricing** — order totals are always computed from the
  product's current price in the database, never trusted from the client.
- **Order status state machine** — `RECEIVED → PREPARING → READY →
  COMPLETED` (or `CANCELLED` at any point before `COMPLETED`), enforced in
  `OrderService.update_status`.

---

## 2. Project Structure

```
shop_ordering_system/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers (thin — delegate to services)
│   │   │   ├── auth.py
│   │   │   ├── customers.py
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   ├── dashboard.py
│   │   │   ├── deps.py           # JWT auth dependencies
│   │   │   └── error_handlers.py
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings (.env loader)
│   │   │   ├── security.py       # bcrypt hashing + JWT
│   │   │   ├── logging_config.py
│   │   │   └── exceptions.py     # Domain exception types
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── customer.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── order_item.py
│   │   │   └── enums.py          # OrderStatus + valid transitions
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── customer.py
│   │   │   ├── product.py
│   │   │   └── order.py
│   │   ├── services/                # Business logic layer
│   │   │   ├── customer_service.py
│   │   │   ├── product_service.py
│   │   │   └── order_service.py
│   │   ├── database.py            # Engine / session / Base
│   │   └── main.py                # FastAPI app, startup seeding, exception handlers
│   ├── Dockerfile
│   └── requirements.txt
├── customer_app/
│   ├── app.py                     # Streamlit customer UI
│   ├── api_client.py              # HTTP client wrapper
│   ├── Dockerfile
│   └── requirements.txt
├── admin_app/
│   ├── app.py                     # Streamlit admin dashboard UI
│   ├── api_client.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── requirements.txt                # Combined deps, for local (non-Docker) dev
├── .env.example
├── .gitignore
└── README.md
```

---

## 3. Database Schema

| Table         | Key Columns                                                                 |
|---------------|------------------------------------------------------------------------------|
| `customers`   | id, name, mobile (unique), password_hash, is_active, is_admin, created_at  |
| `products`    | id, name, description, price, is_active                                    |
| `orders`      | id, customer_id (FK), status, total_amount, created_at, updated_at         |
| `order_items` | id, order_id (FK), product_id (FK), quantity, unit_price                   |

**Relationships**
- One `Customer` → many `Orders` (`Customer.orders`, cascade delete)
- One `Order` → many `OrderItems` (`Order.items`, cascade delete)
- One `Product` → many `OrderItems` (`Product.order_items`)

The **admin is just a `Customer` row with `is_admin=True`** — there's no
separate admin table, which keeps Phase-1 simple while still fully
supporting role-based access control via the `is_admin` flag and JWT `role`
claim.

---

## 4. Authentication

- Passwords are hashed with **bcrypt** (via `passlib`) — plaintext passwords
  are never stored or logged.
- `POST /auth/login` validates mobile + password and returns a signed **JWT**
  (`PyJWT`, HS256) containing the user's mobile (`sub`) and `role`
  (`customer` or `admin`).
- Every protected route depends on `get_current_customer` (validates the JWT
  and loads the user) or `get_current_admin` (additionally requires
  `is_admin=True`).
- Customers can only view **their own** orders; attempting to access another
  customer's order returns `403 Forbidden`.

---

## 5. API Reference

| Method | Path                     | Auth          | Description                              |
|--------|--------------------------|---------------|-------------------------------------------|
| POST   | `/auth/login`             | none          | Login, returns JWT                       |
| GET    | `/customers/me`           | customer      | Get logged-in user's profile             |
| GET    | `/customers`              | admin         | List all customers                       |
| POST   | `/customers`              | admin         | Register a new customer                  |
| GET    | `/products`               | customer      | List active products (menu)              |
| GET    | `/products/all`           | admin         | List all products incl. inactive         |
| GET    | `/products/{id}`          | customer      | Get a single product                     |
| POST   | `/products`               | admin         | Create a product                         |
| PUT    | `/products/{id}`          | admin         | Update a product                         |
| POST   | `/orders`                 | customer      | Place a new order                        |
| GET    | `/orders`                 | customer/admin| List orders (own / all, with filters)    |
| GET    | `/orders/{id}`            | customer/admin| Get order detail / status                |
| PUT    | `/orders/{id}/status`     | admin         | Update order status                      |
| GET    | `/dashboard/metrics`      | admin         | Today's orders / pending / completed     |

Interactive API docs are available at **http://localhost:8000/docs** (Swagger UI)
once the backend is running.

---

## 6. Running with Docker (recommended)

### Prerequisites
- Docker
- Docker Compose (v2, bundled with modern Docker Desktop / Docker Engine)

### Steps

```bash
# 1. Clone / unzip the project, then move into it
cd shop_ordering_system

# 2. Copy the example environment file and adjust secrets
cp .env.example .env
# At minimum, change JWT_SECRET_KEY and ADMIN_PASSWORD before any real use.

# 3. Build and start everything
docker-compose up --build
```

This starts three containers:

| Service       | URL                          |
|---------------|-------------------------------|
| Backend API   | http://localhost:8000        |
| API Docs      | http://localhost:8000/docs   |
| Customer App  | http://localhost:8501        |
| Admin App     | http://localhost:8502        |

On first startup, the backend automatically:
1. Creates all database tables.
2. Seeds an **admin account** using `ADMIN_MOBILE` / `ADMIN_PASSWORD` from `.env`.
3. Seeds **5 default menu items** if the products table is empty.

The SQLite database file persists in a named Docker volume (`shop_db_data`),
so your data survives `docker-compose down` / restarts. Use
`docker-compose down -v` to wipe it.

To stop everything:
```bash
docker-compose down
```

---

## 7. Running locally without Docker

### Prerequisites
- Python 3.11+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# create a .env in backend/ (or set env vars directly)
cp ../.env.example .env
# edit DATABASE_URL to e.g. sqlite:///./shop.db for local file-based dev

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Customer App (in a new terminal)

```bash
cd customer_app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export API_BASE_URL=http://localhost:8000   # Windows: set API_BASE_URL=http://localhost:8000
streamlit run app.py --server.port 8501
```

### Admin App (in a new terminal)

```bash
cd admin_app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export API_BASE_URL=http://localhost:8000
streamlit run app.py --server.port 8502
```

---

## 8. Default / Seeded Credentials

| Role  | Mobile        | Password    |
|-------|---------------|-------------|
| Admin | `9999999999`  | `admin123`  |

⚠️ **Change `ADMIN_MOBILE` / `ADMIN_PASSWORD` in `.env` before any real
deployment.** The seeded password is for local development only.

Customers have no public self-signup screen in Phase 1 (by design — only
*registered* customers should be able to order). The admin registers new
customers from the **Admin Dashboard → Customers tab**, or via
`POST /customers`.

---

## 9. Using the System

### As a customer
1. Get registered by the shop admin (they'll give you a mobile number +
   temporary password).
2. Open the Customer App, log in.
3. Browse the menu, set quantities, and click **Place Order**.
4. Check the **My Orders** tab to track status: RECEIVED → PREPARING → READY
   → COMPLETED.

### As the admin
1. Log into the Admin Dashboard with the admin credentials.
2. The **Orders** tab shows all incoming orders, with one-click buttons to
   advance status (e.g. "Mark PREPARING", "Mark READY").
3. The dashboard auto-refreshes every 5 seconds (toggle in the sidebar).
4. Use the **Customers** tab to register new customers or view the customer
   list.
5. Use the **Menu** tab to add new products or activate/deactivate existing
   ones.

---

## 10. Order Status State Machine

```
RECEIVED ──► PREPARING ──► READY ──► COMPLETED
    │             │            │
    └─────────────┴────────────┴──► CANCELLED
```

Invalid transitions (e.g. `COMPLETED → RECEIVED`, or skipping straight from
`RECEIVED → READY`) are rejected by the backend with `409 Conflict` —
enforced in `OrderService.update_status` using the
`VALID_STATUS_TRANSITIONS` map in `app/models/enums.py`.

---

## 11. Environment Variables (`.env`)

| Variable                      | Description                                        | Default                          |
|--------------------------------|-----------------------------------------------------|-----------------------------------|
| `DATABASE_URL`                 | SQLAlchemy connection string                       | `sqlite:////app/data/shop.db`    |
| `JWT_SECRET_KEY`                | Secret used to sign JWTs — **change in production** | (insecure placeholder)           |
| `JWT_ALGORITHM`                 | JWT signing algorithm                              | `HS256`                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | JWT lifetime in minutes                            | `720` (12 hours)                 |
| `ADMIN_MOBILE`                  | Bootstrap admin mobile number                      | `9999999999`                     |
| `ADMIN_PASSWORD`                | Bootstrap admin password                           | `admin123`                       |
| `ADMIN_NAME`                    | Bootstrap admin display name                       | `Shop Admin`                     |
| `API_BASE_URL`                  | URL the Streamlit apps use to reach the backend    | `http://backend:8000` (Docker)   |
| `LOG_LEVEL`                     | Logging verbosity                                  | `INFO`                           |

---

## 12. Notes on Scaling Beyond Phase 1

This system is intentionally scoped for **50–100 customers, single shop,
single admin**. If/when you outgrow that:

- Swap `DATABASE_URL` to PostgreSQL (SQLAlchemy code requires no changes).
- Replace Streamlit's 5-second polling refresh with WebSockets / Server-Sent
  Events for real-time order updates.
- Add Alembic migrations instead of `Base.metadata.create_all()`.
- Add rate limiting and refresh tokens if exposing the API publicly.
- Move `allow_origins=["*"]` in CORS to an explicit allow-list.

---

## 13. Troubleshooting

- **Streamlit apps show "Could not reach the server"** — ensure the backend
  container/process is running and `API_BASE_URL` points to it (in Docker,
  it should be `http://backend:8000`; locally, `http://localhost:8000`).
- **"Invalid mobile number or password"** — verify the customer was
  registered by the admin, and double-check for typos in the mobile number.
- **Port already in use** — change the left-hand side of the port mapping in
  `docker-compose.yml` (e.g. `"8001:8000"`) if 8000/8501/8502 are taken.
- **Reset all data** — run `docker-compose down -v` to remove the database
  volume and start fresh on next `up`.

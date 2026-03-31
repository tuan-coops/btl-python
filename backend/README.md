# Pet Shop Backend

Backend FastAPI cho website ban san pham thu cung, to chuc theo huong MVP/do an va de mo rong.

Luu y: toan bo backend hien nam trong thu muc `backend/`. Hay `cd backend` truoc khi chay cac lenh ben duoi.

## Stack

- Python 3.12
- FastAPI
- MySQL
- SQLAlchemy 2.0
- Alembic
- JWT auth
- Pytest
- Docker Compose

## Cau truc chinh

```text
app/
  api/v1/routes/
  core/
  db/
  models/
  repositories/
  schemas/
  services/
  main.py
alembic/
scripts/
tests/
requirements.txt
.env.example
docker-compose.yml
README.md
AGENTS.md
```

## Cai dependencies

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Cau hinh `.env`

```powershell
Copy-Item .env.example .env
```

Bien moi truong chinh:

```env
APP_NAME=Pet Shop Backend
APP_VERSION=0.1.0
API_V1_PREFIX=/api/v1
DEBUG=true
JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
LOW_STOCK_THRESHOLD=5
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DB=pet_shop
```

## Chay MySQL bang Docker Compose

```powershell
docker compose up -d
docker compose ps
```

## Chay migration

```powershell
alembic upgrade head
```

Tao migration moi:

```powershell
alembic revision --autogenerate -m "message"
```

## Seed data

```powershell
python scripts/seed_data.py
```

Seed hien tao:

- roles: `seller`, `customer`
- 1 seller demo
- 1 customer demo
- 3 category mau
- 3 product mau
- 2 article mau

Tai khoan demo:

- Seller: `seller@example.com` / `Seller123!`
- Customer: `customer@example.com` / `Customer123!`

## Chay app

```powershell
uvicorn app.main:app --reload
```

URL mac dinh:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Nhom endpoint chinh

Auth:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Customer:

- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `GET /api/v1/categories`
- `GET /api/v1/cart`
- `POST /api/v1/cart/items`
- `PATCH /api/v1/cart/items/{item_id}`
- `DELETE /api/v1/cart/items/{item_id}`
- `POST /api/v1/orders/checkout`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{order_id}`
- `GET /api/v1/articles`
- `GET /api/v1/articles/{article_id}`

Seller:

- `GET /api/v1/seller/dashboard`
- `POST /api/v1/seller/categories`
- `GET /api/v1/seller/categories`
- `PATCH /api/v1/seller/categories/{category_id}`
- `DELETE /api/v1/seller/categories/{category_id}`
- `POST /api/v1/seller/products`
- `GET /api/v1/seller/products`
- `PATCH /api/v1/seller/products/{product_id}`
- `DELETE /api/v1/seller/products/{product_id}`
- `GET /api/v1/seller/users`
- `GET /api/v1/seller/orders`
- `GET /api/v1/seller/orders/{order_id}`
- `PATCH /api/v1/seller/orders/{order_id}/status`
- `POST /api/v1/seller/articles`
- `GET /api/v1/seller/articles`
- `PATCH /api/v1/seller/articles/{article_id}`
- `DELETE /api/v1/seller/articles/{article_id}`

## Logging va Error Handling

- Logging dung `logging` chuan cua Python, cau hinh tai [app/core/logging.py](/C:/Users/admin/OneDrive/Máy%20tính/Python/btl/backend/app/core/logging.py)
- Co log startup/shutdown, auth fail quan trong, checkout tao order, seller update order status, unhandled exception
- Error handling tap trung tai [app/core/exceptions.py](/C:/Users/admin/OneDrive/Máy%20tính/Python/btl/backend/app/core/exceptions.py)
- Validation loi tra `detail` + `errors`
- Unhandled exception duoc log server-side va tra message an toan cho client

## Chay test

```powershell
pytest
```

Chay theo nhom:

```powershell
pytest tests/test_auth.py
pytest tests/test_customer_flow.py
pytest tests/test_seller_flow.py
pytest tests/test_milestone6.py
```

## Trang thai hien tai

- Customer flow da co products, categories, cart, checkout, order history
- Seller flow da co dashboard, category/product management, user list, order management
- Article/blog da co public list/detail va seller CRUD
- Co seed script, logging co ban, centralized error handling

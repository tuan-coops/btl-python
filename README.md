# Pet Shop Backend

Backend FastAPI cho website bán sản phẩm thú cưng. Codebase hiện có scaffold cơ bản, cấu hình `.env`, PostgreSQL bằng Docker Compose, SQLAlchemy 2.0, Alembic, health check endpoint và bộ models dữ liệu cốt lõi cho milestone 2.

## Công nghệ sử dụng

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Docker Compose
- Pytest

## Cấu trúc thư mục

```text
app/
  api/
    v1/
      routes/
  core/
  db/
  models/
  repositories/
  schemas/
  services/
  utils/
  main.py
tests/
alembic/
  versions/
requirements.txt
.env.example
docker-compose.yml
alembic.ini
README.md
```

## 1. Cài dependencies

Tạo môi trường ảo và cài package:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Neu may khong co `py`, co the dung duong dan Python 3.12 da cai san.

## 2. Tạo file .env

Tạo file `.env` từ mẫu:

```powershell
Copy-Item .env.example .env
```

Có thể chỉnh lại các biến nếu cần:

```env
APP_NAME=Pet Shop Backend
APP_VERSION=0.1.0
API_V1_PREFIX=/api/v1
DEBUG=true
JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=pet_shop
```

## 3. Chạy PostgreSQL bằng Docker Compose

```powershell
docker compose up -d
```

Kiểm tra container:

```powershell
docker compose ps
```

## 4. Chạy app local

```powershell
uvicorn app.main:app --reload
```

App mặc định chạy tại:

- API: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 5. Health check

Endpoint:

```text
GET /health
```

Ví dụ response:

```json
{
  "status": "ok"
}
```

## 6. Auth endpoints

Milestone 3 hiện có các endpoint:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

`/auth/login` trả về JWT access token kiểu bearer. Dùng token này với header:

```text
Authorization: Bearer <access_token>
```

## 7. Chạy migration

Apply migration hiện có:

```powershell
alembic upgrade head
```

Tạo migration mới sau khi thêm model:

```powershell
alembic revision --autogenerate -m "create products table"
```

## 8. Chạy test

```powershell
pytest
```

Chạy riêng auth tests:

```powershell
pytest tests/test_auth.py
```

## Ghi chú thiết kế

- `app/api`: chứa router và versioning API.
- `app/core`: chứa config và các thành phần lõi.
- `app/db`: chứa SQLAlchemy base, engine, session.
- `app/models`: chứa ORM models cho `Role`, `User`, `Category`, `Product`, `ProductImage`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Address`, `Article`.
- `app/repositories`: dành cho tầng truy vấn DB ở milestone sau.
- `app/services`: dành cho business logic ở milestone sau.
- `app/schemas`: chứa request/response schemas.
- `tests`: chứa test cơ bản cho endpoint.

## Dữ liệu hiện có

- `roles`: role phân quyền cơ bản, có seed `admin` và `customer` trong migration đầu tiên.
- `users`: thông tin tài khoản, liên kết `role`, `addresses`, `cart`, `orders`.
- `categories`, `products`, `product_images`: phục vụ danh mục và hiển thị shop/product detail.
- `carts`, `cart_items`: mỗi user có một cart, mỗi item unique theo cặp `cart + product`.
- `orders`, `order_items`: lưu đơn hàng và snapshot sản phẩm khi mua.
- `addresses`: địa chỉ giao hàng của user.
- `articles`: bài viết chia sẻ kiến thức chăm sóc thú cưng.

## Milestone 3 gợi ý

- Thêm module `auth` với đăng ký, đăng nhập, JWT, hash password.
- Thêm dependency kiểm tra user hiện tại và phân quyền admin/customer.
- Bắt đầu API CRUD cho `categories`, `products`, `users`.
- Viết test cho auth flow, permission và repository/service.

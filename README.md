# Pet Shop Backend - Milestone 1

Milestone 1 dựng khung backend bằng FastAPI cho website bán sản phẩm thú cưng. Project tập trung vào cấu trúc rõ ràng, cấu hình bằng `.env`, kết nối PostgreSQL, SQLAlchemy 2.0, Alembic và một health check endpoint cơ bản.

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

## 6. Chạy migration

Apply migration hiện có:

```powershell
alembic upgrade head
```

Tạo migration mới sau khi thêm model:

```powershell
alembic revision --autogenerate -m "create products table"
```

## 7. Chạy test

```powershell
pytest
```

## Ghi chú thiết kế

- `app/api`: chứa router và versioning API.
- `app/core`: chứa config và các thành phần lõi.
- `app/db`: chứa SQLAlchemy base, engine, session.
- `app/models`: chứa ORM models.
- `app/repositories`: dành cho tầng truy vấn DB ở milestone sau.
- `app/services`: dành cho business logic ở milestone sau.
- `app/schemas`: chứa request/response schemas.
- `tests`: chứa test cơ bản cho endpoint.

## Milestone 2 gợi ý

- Thêm module `users`, `auth` và JWT authentication.
- Tách repository/service cho từng domain.
- Thiết kế entity chính: `User`, `Category`, `Product`, `Cart`, `Order`.
- Bổ sung bộ test cho database, auth và luồng CRUD cơ bản.

# Pet Shop

Đây là dự án web bán sản phẩm thú cưng gồm 2 phần tách biệt:

- `backend/`: REST API viết bằng FastAPI, dùng MySQL, JWT auth, Alembic và pytest
- `frontend/`: giao diện thuần HTML/CSS/JavaScript, gọi API bằng `fetch`, không cần build

Repo phù hợp để demo đồ án, học mô hình full-stack cơ bản, hoặc tiếp tục mở rộng thêm tính năng cho cửa hàng thú cưng.

## Tính năng chính

### Khách hàng

- Đăng ký, đăng nhập, xem thông tin cá nhân
- Xem danh mục sản phẩm và chi tiết sản phẩm
- Thêm vào giỏ hàng, cập nhật số lượng, xóa khỏi giỏ
- Checkout và xem lịch sử đơn hàng
- Xem danh sách bài viết/public article

### Quản trị viên

- Đăng nhập seller
- Xem dashboard thống kê tổng quan
- CRUD danh mục
- CRUD sản phẩm và cập nhật tồn kho
- Xem danh sách khách hàng
- Xem và cập nhật trạng thái đơn hàng
- CRUD bài viết

## Công nghệ sử dụng

- Backend: Python, FastAPI, SQLAlchemy 2.0, Alembic, MySQL, JWT, pytest
- Frontend: HTML, CSS, JavaScript, `fetch`, `localStorage`
- Hạ tầng local: Docker Compose cho MySQL

## Cấu trúc thư mục

```text
btl/
  backend/
    app/
    alembic/
    scripts/
    tests/
    docker-compose.yml
    requirements.txt
    README.md
  frontend/
    assets/
    pages/
    index.html
    README.md
  README.md
```

## Chạy nhanh dự án

### 1. Chạy backend

```powershell
cd backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
python scripts/seed_data.py
uvicorn app.main:app --reload
```

Backend mặc định:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

Biến môi trường backend hiện có default trong code, gồm các giá trị chính:

- `APP_NAME=Pet Shop Backend`
- `APP_VERSION=0.1.0`
- `API_V1_PREFIX=/api/v1`
- `JWT_SECRET_KEY=change-me`
- `MYSQL_SERVER=localhost`
- `MYSQL_PORT=3306`
- `MYSQL_USER=root`
- `MYSQL_PASSWORD=root`
- `MYSQL_DB=pet_shop`
- `CORS_ALLOW_ORIGINS=*`

Nếu muốn cấu hình riêng, tạo file `.env` trong thư mục `backend/`.

### 2. Chạy frontend

Frontend không cần build. Sau khi backend đang chạy, mở thư mục `frontend/` bằng Live Server hoặc mở trực tiếp file HTML để demo.

Khuyến nghị:

```powershell
cd frontend
```

Sau đó mở `index.html` bằng VS Code Live Server.

Base URL mặc định của frontend:

```text
http://127.0.0.1:8000/api/v1
```

Giá trị này nằm trong `frontend/assets/js/config.js` và cũng có thể được ghi đè qua `localStorage`.

## Tài khoản demo sau khi seed

- Seller: `seller@example.com` / `Seller123!`
- Customer: `customer@example.com` / `Customer123!`

## Các trang giao diện chính

### Customer

- Trang chủ: `frontend/index.html`
- Danh mục: `frontend/pages/categories.html`
- Sản phẩm: `frontend/pages/products.html`
- Chi tiết sản phẩm: `frontend/pages/product-detail.html?id=1`
- Đăng ký: `frontend/pages/register.html`
- Đăng nhập: `frontend/pages/login.html`
- Hồ sơ: `frontend/pages/profile.html`
- Giỏ hàng: `frontend/pages/cart.html`
- Checkout: `frontend/pages/checkout.html`
- Đơn hàng: `frontend/pages/orders.html`

### Seller

- Đăng nhập người bán: `frontend/pages/seller-login.html`
- Dashboard: `frontend/pages/seller-dashboard.html`
- Quản lý danh mục: `frontend/pages/seller-categories.html`
- Quản lý sản phẩm: `frontend/pages/seller-products.html`
- Quản lý đơn hàng: `frontend/pages/seller-orders.html`
- Quản lý khách hàng: `frontend/pages/seller-customers.html`
- Quản lý bài viết: `frontend/pages/seller-articles.html`

## API nổi bật

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Customer

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

### Admin

- `GET /api/v1/seller/dashboard`
- `GET /api/v1/seller/users`
- `GET /api/v1/seller/orders`
- `PATCH /api/v1/seller/orders/{order_id}/status`
- `POST /api/v1/seller/categories`
- `PATCH /api/v1/seller/categories/{category_id}`
- `POST /api/v1/seller/products`
- `PATCH /api/v1/seller/products/{product_id}`
- `POST /api/v1/seller/articles`
- `PATCH /api/v1/seller/articles/{article_id}`

## Kiểm thử

Chạy toàn bộ test:

```powershell
cd backend
pytest
```

Một số nhóm test hiện có:

- `tests/test_health.py`
- `tests/test_auth.py`
- `tests/test_customer_flow.py`
- `tests/test_seller_flow.py`
- `tests/test_milestone6.py`

Các test đang bao phủ những luồng chính như:

- health check
- đăng ký/đăng nhập/JWT auth
- danh mục, sản phẩm, giỏ hàng, checkout, lịch sử đơn hàng
- phân quyền seller
- dashboard và quản trị bài viết
- seed data chạy an toàn nhiều lần

## Tài liệu chi tiết hơn

- Backend: [backend/README.md](/C:/Users/admin/OneDrive/Máy tính/Python/btl/backend/README.md)
- Frontend: [frontend/README.md](/C:/Users/admin/OneDrive/Máy tính/Python/btl/frontend/README.md)

## Gợi ý mở rộng

- Thêm upload ảnh thật cho sản phẩm/bài viết
- Thêm thanh toán online
- Thêm tìm kiếm, lọc và phân trang ở frontend
- Thêm CI chạy test tự động
- Deploy backend/frontend lên môi trường public

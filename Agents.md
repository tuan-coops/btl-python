# AGENTS.md

## Project Overview
Backend cho website giới thiệu và bán sản phẩm thú cưng, phục vụ:
- customer web app
- admin dashboard

Mục tiêu là xây dựng một backend MVP rõ ràng, dễ bảo trì, dễ mở rộng, phù hợp đồ án hoặc sản phẩm thử nghiệm.

## Tech Stack
- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Pydantic
- JWT Authentication
- Pytest
- Docker Compose

## Architecture Principles
- Code phải tách lớp rõ ràng:
  - `router`: khai báo API endpoints
  - `service`: xử lý business logic
  - `repository`: truy vấn database
  - `schema`: request/response schema
  - `models`: ORM models
- Không nhét business logic trực tiếp vào router
- Không viết query SQL lẫn trong router nếu có thể tách qua repository/service
- Ưu tiên code đơn giản, dễ đọc, dễ test
- Ưu tiên RESTful API nhất quán

## Project Scope
### Customer features
- đăng ký
- đăng nhập
- xem thông tin tài khoản
- xem danh sách sản phẩm
- lọc sản phẩm
- xem chi tiết sản phẩm
- quản lý giỏ hàng
- checkout tạo đơn hàng
- xem lịch sử đơn hàng

### Admin features
- quản lý category
- quản lý product
- cập nhật tồn kho
- xem danh sách users
- xem danh sách orders
- cập nhật trạng thái order
- xem dashboard thống kê
- quản lý article/blog cơ bản

## Main Modules
- auth
- users
- categories
- products
- cart
- orders
- admin
- articles
- dashboard
- core
- db

## Required Entities
- User
- Role
- Category
- Product
- ProductImage
- Cart
- CartItem
- Order
- OrderItem
- Address
- Article

## Business Rules
- User có role: `customer` hoặc `admin`
- Product phải có:
  - name
  - slug nếu cần
  - description
  - price
  - stock_quantity
  - brand
  - pet_type
  - category_id
  - is_active
- Order status chỉ gồm:
  - `pending`
  - `confirmed`
  - `shipping`
  - `completed`
  - `cancelled`
- Cart item và Order item phải lưu snapshot giá tại thời điểm thêm/mua
- Không cho checkout nếu số lượng vượt tồn kho
- Khi checkout thành công phải trừ tồn kho
- Chỉ admin mới dùng được admin endpoints
- Mọi input đều phải validate bằng Pydantic
- Password phải được hash an toàn
- JWT secret không được hardcode
- Config lấy từ `.env`
- Mọi thay đổi database phải có migration Alembic

## Folder Structure Expectation
Ưu tiên scaffold gần giống:

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
requirements.txt
.env.example
docker-compose.yml
README.md
AGENTS.md
# Pet Shop Frontend

Frontend thuần cho dự án Pet Shop, chỉ dùng:

- HTML
- CSS
- JavaScript
- `fetch`
- `localStorage`

Không dùng framework, không dùng TypeScript, không cần build.

## Cấu trúc

```text
frontend/
  index.html
  pages/
  assets/
    css/
    js/
    images/
```

## Chuẩn bị backend

Chạy backend FastAPI trước:

```powershell
cd ../backend
uvicorn app.main:app --reload
```

Backend mặc định:

- API: `http://127.0.0.1:8000/api/v1`
- Docs: `http://127.0.0.1:8000/docs`

## Chạy frontend

Khuyến nghị mở bằng Live Server:

1. Mở thư mục `frontend/` trong VS Code
2. Click phải vào `index.html`
3. Chọn `Open with Live Server`

Bạn cũng có thể mở trực tiếp file HTML, nhưng Live Server ổn định hơn khi demo.

## Cấu hình API base URL

Base URL mặc định nằm trong:

- `assets/js/config.js`

Giá trị mặc định:

```js
http://127.0.0.1:8000/api/v1
```

Nếu backend chạy ở URL khác, sửa trong file này.

## Tài khoản demo

Sau khi seed backend:

- Seller: `seller@example.com` / `Seller123!`
- Customer: `customer@example.com` / `Customer123!`

## Luồng customer

- Trang chủ: `index.html`
- Danh mục: `pages/categories.html`
- Sản phẩm: `pages/products.html`
- Chi tiết sản phẩm: `pages/product-detail.html?id=1`
- Đăng ký: `pages/register.html`
- Đăng nhập: `pages/login.html`
- Tài khoản: `pages/profile.html`
- Giỏ hàng: `pages/cart.html`
- Checkout: `pages/checkout.html`
- Lịch sử đơn hàng: `pages/orders.html`

## Luồng seller

- Đăng nhập seller: `pages/seller-login.html`
- Dashboard: `pages/seller-dashboard.html`
- Quản lý danh mục: `pages/seller-categories.html`
- Quản lý sản phẩm: `pages/seller-products.html`
- Quản lý đơn hàng: `pages/seller-orders.html`
- Quản lý khách hàng: `pages/seller-customers.html`
- Quản lý bài viết: `pages/seller-articles.html`

## Những gì đã có ở milestone 4

- Responsive cơ bản cho desktop và mobile
- Validate form phía client
- Loading state cho form submit và danh sách chính
- Toast thông báo thành công/thất bại
- Xử lý lỗi request tập trung trong `assets/js/api.js`
- Guard customer/seller dùng token trong `localStorage`
- Seller pages xác thực lại qua `/auth/me`

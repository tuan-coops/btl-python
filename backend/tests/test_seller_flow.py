from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User


def register_and_login(
    client: TestClient,
    *,
    email: str,
    password: str = "Password123",
    role: str = "customer",
) -> dict:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": email.split("@")[0],
            "email": email,
            "phone": "0123456789",
            "password": password,
            "role": role,
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def promote_user_to_seller(db_session: Session, email: str) -> None:
    seller_role = db_session.query(Role).filter(Role.name == "seller").first()
    user = db_session.query(User).filter(User.email == email).first()
    user.role_id = seller_role.id
    db_session.commit()


def create_category(client: TestClient, token: str) -> dict:
    response = client.post(
        "/api/v1/seller/categories",
        headers=auth_headers(token),
        json={
            "name": "Seller Dog Food",
            "slug": "seller-dog-food",
            "description": "Managed by seller",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_product(client: TestClient, token: str, category_id: int) -> dict:
    response = client.post(
        "/api/v1/seller/products",
        headers=auth_headers(token),
        json={
            "name": "Seller Premium Product",
            "slug": "seller-premium-product",
            "sku": "SELLER-001",
            "description": "Premium product",
            "price": "150000.00",
            "stock_quantity": 12,
            "brand": "Royal Pets",
            "pet_type": "dog",
            "category_id": category_id,
            "is_active": True,
            "primary_image_url": "https://example.com/seller-product.jpg",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_customer_order(client: TestClient, token: str, product_id: int) -> dict:
    add_response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers(token),
        json={"product_id": product_id, "quantity": 1},
    )
    assert add_response.status_code == 201
    checkout_response = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers(token),
        json={
            "recipient_name": "Customer",
            "phone": "0123456789",
            "line1": "123 Pet Street",
            "district": "District 1",
            "city": "Ho Chi Minh City",
            "province": "Ho Chi Minh",
            "country": "Vietnam",
            "payment_method": "cod",
        },
    )
    assert checkout_response.status_code == 200
    return checkout_response.json()


def test_customer_cannot_access_seller_endpoint(client: TestClient) -> None:
    customer = register_and_login(client, email="customer-seller-block@example.com")

    response = client.get("/api/v1/seller/users", headers=auth_headers(customer["access_token"]))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this resource"


def test_seller_create_category_success(client: TestClient, db_session: Session) -> None:
    seller = register_and_login(client, email="seller-category@example.com", role="seller")

    response = client.post(
        "/api/v1/seller/categories",
        headers=auth_headers(seller["access_token"]),
        json={
            "name": "Food",
            "slug": "food",
            "description": "Category",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Food"


def test_promoted_seller_can_create_product_success(client: TestClient, db_session: Session) -> None:
    seller = register_and_login(client, email="seller-product@example.com")
    promote_user_to_seller(db_session, "seller-product@example.com")
    seller = client.post(
        "/api/v1/auth/login",
        json={"email": "seller-product@example.com", "password": "Password123"},
    ).json()
    category = create_category(client, seller["access_token"])

    product = create_product(client, seller["access_token"], category["id"])

    assert product["name"] == "Seller Premium Product"
    assert product["stock_quantity"] == 12
    assert product["images"][0]["is_primary"] is True


def test_seller_update_stock_success(client: TestClient, db_session: Session) -> None:
    seller = register_and_login(client, email="seller-stock@example.com", role="seller")
    category = create_category(client, seller["access_token"])
    product = create_product(client, seller["access_token"], category["id"])

    response = client.patch(
        f"/api/v1/seller/products/{product['id']}",
        headers=auth_headers(seller["access_token"]),
        json={"stock_quantity": 25},
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 25


def test_seller_list_users_success(client: TestClient) -> None:
    seller = register_and_login(client, email="seller-users@example.com", role="seller")
    register_and_login(client, email="customer-list@example.com")

    response = client.get("/api/v1/seller/users", headers=auth_headers(seller["access_token"]))

    assert response.status_code == 200
    assert response.json()["total"] >= 2
    assert all("hashed_password" not in item for item in response.json()["items"])


def test_seller_list_orders_success(client: TestClient) -> None:
    seller = register_and_login(client, email="seller-orders@example.com", role="seller")
    category = create_category(client, seller["access_token"])
    product = create_product(client, seller["access_token"], category["id"])
    customer = register_and_login(client, email="customer-order@example.com")
    create_customer_order(client, customer["access_token"], product["id"])

    response = client.get("/api/v1/seller/orders", headers=auth_headers(seller["access_token"]))

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["user"]["email"] == "customer-order@example.com"


def test_seller_update_order_status_success(client: TestClient) -> None:
    seller = register_and_login(client, email="seller-status@example.com", role="seller")
    category = create_category(client, seller["access_token"])
    product = create_product(client, seller["access_token"], category["id"])
    customer = register_and_login(client, email="customer-status@example.com")
    order = create_customer_order(client, customer["access_token"], product["id"])

    response = client.patch(
        f"/api/v1/seller/orders/{order['id']}/status",
        headers=auth_headers(seller["access_token"]),
        json={"status": "confirmed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_seller_update_order_status_invalid_transition_fails(client: TestClient) -> None:
    seller = register_and_login(client, email="seller-status-invalid@example.com", role="seller")
    category = create_category(client, seller["access_token"])
    product = create_product(client, seller["access_token"], category["id"])
    customer = register_and_login(client, email="customer-status-invalid@example.com")
    order = create_customer_order(client, customer["access_token"], product["id"])

    response = client.patch(
        f"/api/v1/seller/orders/{order['id']}/status",
        headers=auth_headers(seller["access_token"]),
        json={"status": "completed"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid order status transition"

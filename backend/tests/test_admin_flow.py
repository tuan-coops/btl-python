from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User


def register_and_login(
    client: TestClient,
    *,
    email: str,
    password: str = "Password123",
) -> dict:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": email.split("@")[0],
            "email": email,
            "phone": "0123456789",
            "password": password,
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


def promote_user_to_admin(db_session: Session, email: str) -> None:
    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    user = db_session.query(User).filter(User.email == email).first()
    user.role_id = admin_role.id
    db_session.commit()


def create_category(client: TestClient, token: str) -> dict:
    response = client.post(
        "/api/v1/admin/categories",
        headers=auth_headers(token),
        json={
            "name": "Admin Dog Food",
            "slug": "admin-dog-food",
            "description": "Managed by admin",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_product(client: TestClient, token: str, category_id: int) -> dict:
    response = client.post(
        "/api/v1/admin/products",
        headers=auth_headers(token),
        json={
            "name": "Admin Premium Product",
            "slug": "admin-premium-product",
            "sku": "ADMIN-001",
            "description": "Premium product",
            "price": "150000.00",
            "stock_quantity": 12,
            "brand": "Royal Pets",
            "pet_type": "dog",
            "category_id": category_id,
            "is_active": True,
            "primary_image_url": "https://example.com/admin-product.jpg",
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


def test_customer_cannot_access_admin_endpoint(client: TestClient) -> None:
    customer = register_and_login(client, email="customer-admin-block@example.com")

    response = client.get("/api/v1/admin/users", headers=auth_headers(customer["access_token"]))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this resource"


def test_admin_create_category_success(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-category@example.com")
    promote_user_to_admin(db_session, "admin-category@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-category@example.com", "password": "Password123"},
    ).json()

    response = client.post(
        "/api/v1/admin/categories",
        headers=auth_headers(admin["access_token"]),
        json={
            "name": "Food",
            "slug": "food",
            "description": "Category",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Food"


def test_admin_create_product_success(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-product@example.com")
    promote_user_to_admin(db_session, "admin-product@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-product@example.com", "password": "Password123"},
    ).json()
    category = create_category(client, admin["access_token"])

    product = create_product(client, admin["access_token"], category["id"])

    assert product["name"] == "Admin Premium Product"
    assert product["stock_quantity"] == 12
    assert product["images"][0]["is_primary"] is True


def test_admin_update_stock_success(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-stock@example.com")
    promote_user_to_admin(db_session, "admin-stock@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-stock@example.com", "password": "Password123"},
    ).json()
    category = create_category(client, admin["access_token"])
    product = create_product(client, admin["access_token"], category["id"])

    response = client.patch(
        f"/api/v1/admin/products/{product['id']}",
        headers=auth_headers(admin["access_token"]),
        json={"stock_quantity": 25},
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 25


def test_admin_list_users_success(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-users@example.com")
    promote_user_to_admin(db_session, "admin-users@example.com")
    register_and_login(client, email="customer-list@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-users@example.com", "password": "Password123"},
    ).json()

    response = client.get("/api/v1/admin/users", headers=auth_headers(admin["access_token"]))

    assert response.status_code == 200
    assert response.json()["total"] >= 2
    assert all("hashed_password" not in item for item in response.json()["items"])


def test_admin_list_orders_success(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-orders@example.com")
    promote_user_to_admin(db_session, "admin-orders@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-orders@example.com", "password": "Password123"},
    ).json()
    category = create_category(client, admin["access_token"])
    product = create_product(client, admin["access_token"], category["id"])
    customer = register_and_login(client, email="customer-order@example.com")
    create_customer_order(client, customer["access_token"], product["id"])

    response = client.get("/api/v1/admin/orders", headers=auth_headers(admin["access_token"]))

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["user"]["email"] == "customer-order@example.com"


def test_admin_update_order_status_success(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-status@example.com")
    promote_user_to_admin(db_session, "admin-status@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-status@example.com", "password": "Password123"},
    ).json()
    category = create_category(client, admin["access_token"])
    product = create_product(client, admin["access_token"], category["id"])
    customer = register_and_login(client, email="customer-status@example.com")
    order = create_customer_order(client, customer["access_token"], product["id"])

    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        headers=auth_headers(admin["access_token"]),
        json={"status": "confirmed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_admin_update_order_status_invalid_transition_fails(client: TestClient, db_session: Session) -> None:
    admin = register_and_login(client, email="admin-status-invalid@example.com")
    promote_user_to_admin(db_session, "admin-status-invalid@example.com")
    admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-status-invalid@example.com", "password": "Password123"},
    ).json()
    category = create_category(client, admin["access_token"])
    product = create_product(client, admin["access_token"], category["id"])
    customer = register_and_login(client, email="customer-status-invalid@example.com")
    order = create_customer_order(client, customer["access_token"], product["id"])

    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        headers=auth_headers(admin["access_token"]),
        json={"status": "completed"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid order status transition"

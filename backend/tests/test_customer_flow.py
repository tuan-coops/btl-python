from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage


def register_and_login(
    client: TestClient,
    *,
    email: str = "customer1@example.com",
    password: str = "Password123",
) -> dict:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Customer Test",
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


def seed_catalog(db_session: Session) -> dict[str, int]:
    category = Category(name="Dog Food", slug="dog-food", description="Dog products")
    other_category = Category(name="Cat Toy", slug="cat-toy", description="Cat products")
    db_session.add_all([category, other_category])
    db_session.flush()

    active_product = Product(
        category_id=category.id,
        name="Premium Dog Food",
        slug="premium-dog-food",
        sku="DOG-FOOD-001",
        description="Good food for dogs",
        price=Decimal("120000.00"),
        stock_quantity=10,
        brand="Royal Pets",
        pet_type="dog",
        is_active=True,
    )
    inactive_product = Product(
        category_id=other_category.id,
        name="Hidden Product",
        slug="hidden-product",
        sku="HIDDEN-001",
        description="Should not be listed",
        price=Decimal("50000.00"),
        stock_quantity=5,
        brand="Secret",
        pet_type="cat",
        is_active=False,
    )
    db_session.add_all([active_product, inactive_product])
    db_session.flush()

    db_session.add(
        ProductImage(
            product_id=active_product.id,
            image_url="https://example.com/dog-food.jpg",
            alt_text="Dog food",
            is_primary=True,
            sort_order=1,
        )
    )
    db_session.commit()

    return {
        "category_id": category.id,
        "product_id": active_product.id,
        "inactive_product_id": inactive_product.id,
    }


def test_list_products_returns_active_products_only(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == seed["product_id"]
    assert body["items"][0]["name"] == "Premium Dog Food"


def test_filter_products_by_category(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)

    response = client.get(f"/api/v1/products?category_id={seed['category_id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["category"] == "Dog Food"


def test_list_categories(client: TestClient, db_session: Session) -> None:
    seed_catalog(db_session)

    response = client.get("/api/v1/categories")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_add_to_cart_success(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)
    login_body = register_and_login(client)

    response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers(login_body["access_token"]),
        json={"product_id": seed["product_id"], "quantity": 2},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_quantity"] == 2
    assert len(body["items"]) == 1
    assert body["items"][0]["product_name"] == "Premium Dog Food"
    assert body["items"][0]["quantity"] == 2


def test_add_to_cart_cannot_exceed_stock(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)
    login_body = register_and_login(client)

    response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers(login_body["access_token"]),
        json={"product_id": seed["product_id"], "quantity": 99},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Requested quantity exceeds available stock"


def test_update_cart_item_quantity(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)
    login_body = register_and_login(client)

    add_response = client.post(
        "/api/v1/cart/items",
        headers=auth_headers(login_body["access_token"]),
        json={"product_id": seed["product_id"], "quantity": 1},
    )
    item_id = add_response.json()["items"][0]["id"]

    response = client.patch(
        f"/api/v1/cart/items/{item_id}",
        headers=auth_headers(login_body["access_token"]),
        json={"quantity": 3},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3


def test_checkout_success_reduces_stock_and_clears_cart(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)
    login_body = register_and_login(client)

    client.post(
        "/api/v1/cart/items",
        headers=auth_headers(login_body["access_token"]),
        json={"product_id": seed["product_id"], "quantity": 2},
    )

    checkout_response = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers(login_body["access_token"]),
        json={
            "recipient_name": "Customer Test",
            "phone": "0123456789",
            "line1": "123 Pet Street",
            "district": "District 1",
            "city": "Ho Chi Minh City",
            "province": "Ho Chi Minh",
            "country": "Vietnam",
            "payment_method": "cod",
            "note": "Leave at the door",
        },
    )

    assert checkout_response.status_code == 200
    checkout_body = checkout_response.json()
    assert checkout_body["status"] == "pending"
    assert checkout_body["items"][0]["quantity"] == 2
    assert checkout_body["shipping_address"]["recipient_name"] == "Customer Test"

    cart_response = client.get("/api/v1/cart", headers=auth_headers(login_body["access_token"]))
    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []

    db_session.expire_all()
    product = db_session.get(Product, seed["product_id"])
    assert product.stock_quantity == 8


def test_checkout_empty_cart_fails(client: TestClient) -> None:
    login_body = register_and_login(client)

    response = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers(login_body["access_token"]),
        json={
            "recipient_name": "Customer Test",
            "phone": "0123456789",
            "line1": "123 Pet Street",
            "district": "District 1",
            "city": "Ho Chi Minh City",
            "province": "Ho Chi Minh",
            "country": "Vietnam",
            "payment_method": "cod",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_view_own_order_history(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)
    login_body = register_and_login(client)

    client.post(
        "/api/v1/cart/items",
        headers=auth_headers(login_body["access_token"]),
        json={"product_id": seed["product_id"], "quantity": 1},
    )
    checkout_response = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers(login_body["access_token"]),
        json={
            "recipient_name": "Customer Test",
            "phone": "0123456789",
            "line1": "123 Pet Street",
            "district": "District 1",
            "city": "Ho Chi Minh City",
            "province": "Ho Chi Minh",
            "country": "Vietnam",
            "payment_method": "bank_transfer",
        },
    )
    order_id = checkout_response.json()["id"]

    list_response = client.get("/api/v1/orders", headers=auth_headers(login_body["access_token"]))
    detail_response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=auth_headers(login_body["access_token"]),
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == order_id
    assert detail_response.json()["items"][0]["product_name"] == "Premium Dog Food"


def test_cannot_view_other_users_order(client: TestClient, db_session: Session) -> None:
    seed = seed_catalog(db_session)
    first_user = register_and_login(client, email="buyer1@example.com")
    second_user = register_and_login(client, email="buyer2@example.com")

    client.post(
        "/api/v1/cart/items",
        headers=auth_headers(first_user["access_token"]),
        json={"product_id": seed["product_id"], "quantity": 1},
    )
    checkout_response = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers(first_user["access_token"]),
        json={
            "recipient_name": "Buyer One",
            "phone": "0123456789",
            "line1": "123 Pet Street",
            "district": "District 1",
            "city": "Ho Chi Minh City",
            "province": "Ho Chi Minh",
            "country": "Vietnam",
            "payment_method": "cod",
        },
    )
    order_id = checkout_response.json()["id"]

    response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=auth_headers(second_user["access_token"]),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

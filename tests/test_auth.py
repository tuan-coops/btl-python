from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str = "customer@example.com", password: str = "Password123") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Customer",
            "email": email,
            "phone": "0123456789",
            "password": password,
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, email: str = "customer@example.com", password: str = "Password123") -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def test_register_success(client: TestClient) -> None:
    body = register_user(client)

    assert body["email"] == "customer@example.com"
    assert body["role"]["name"] == "customer"
    assert "hashed_password" not in body


def test_register_duplicate_email(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Another Customer",
            "email": "customer@example.com",
            "phone": "0987654321",
            "password": "Password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"


def test_register_new_user_defaults_to_customer_role(client: TestClient) -> None:
    body = register_user(client, email="newuser@example.com")

    assert body["role"]["name"] == "customer"


def test_login_success(client: TestClient) -> None:
    register_user(client)

    body = login_user(client)

    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "customer@example.com"
    assert body["user"]["role"]["name"] == "customer"
    assert "hashed_password" not in body["user"]


def test_login_wrong_password(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "customer@example.com", "password": "WrongPassword123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_auth_me_with_valid_token(client: TestClient) -> None:
    register_user(client)
    login_body = login_user(client)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "customer@example.com"
    assert response.json()["role"]["name"] == "customer"


def test_auth_me_without_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_auth_me_with_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

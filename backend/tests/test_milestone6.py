from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.role import Role
from app.models.user import User
from scripts.seed_data import seed_data


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


def test_seller_can_access_dashboard(client: TestClient) -> None:
    seller = register_and_login(client, email="dashboard-seller@example.com", role="seller")

    response = client.get("/api/v1/seller/dashboard", headers=auth_headers(seller["access_token"]))

    assert response.status_code == 200
    body = response.json()
    assert "total_users" in body
    assert "total_products" in body
    assert "monthly_revenue" in body


def test_customer_cannot_access_dashboard(client: TestClient) -> None:
    customer = register_and_login(client, email="dashboard-customer@example.com")

    response = client.get("/api/v1/seller/dashboard", headers=auth_headers(customer["access_token"]))

    assert response.status_code == 403


def test_public_article_list_returns_only_published(client: TestClient, db_session: Session) -> None:
    db_session.add_all(
        [
            Article(
                title="Published Article",
                slug="published-article",
                summary="Shown",
                content="Published content",
                is_published=True,
            ),
            Article(
                title="Draft Article",
                slug="draft-article",
                summary="Hidden",
                content="Draft content",
                is_published=False,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/v1/articles")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]
    assert "Published Article" in titles
    assert "Draft Article" not in titles


def test_seller_create_and_update_article(client: TestClient, db_session: Session) -> None:
    seller = register_and_login(client, email="article-seller@example.com")
    promote_user_to_seller(db_session, "article-seller@example.com")
    seller = client.post(
        "/api/v1/auth/login",
        json={"email": "article-seller@example.com", "password": "Password123"},
    ).json()

    create_response = client.post(
        "/api/v1/seller/articles",
        headers=auth_headers(seller["access_token"]),
        json={
            "title": "Pet Care Tips",
            "slug": "pet-care-tips",
            "summary": "Basic tips",
            "content": "Keep pets active and hydrated.",
            "is_published": False,
        },
    )
    assert create_response.status_code == 201
    article_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/seller/articles/{article_id}",
        headers=auth_headers(seller["access_token"]),
        json={"is_published": True, "summary": "Updated summary"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["is_published"] is True
    assert update_response.json()["published_at"] is not None
    assert update_response.json()["summary"] == "Updated summary"


def test_seed_data_runs_safely(client: TestClient, db_session: Session) -> None:
    seed_data(db_session)
    seed_data(db_session)

    assert db_session.query(Role).filter(Role.name == "seller").count() == 1
    assert db_session.query(Role).filter(Role.name == "customer").count() == 1
    assert db_session.query(User).filter(User.email == "seller@example.com").count() == 1
    assert db_session.query(Article).filter(Article.slug == "how-to-choose-dog-food").count() == 1

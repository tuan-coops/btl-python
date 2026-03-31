from datetime import UTC, datetime
from pathlib import Path
import sys

from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import app.models  # noqa: F401
from app.core.logging import get_logger, setup_logging
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.article import Article
from app.models.category import Category
from app.models.enums import PetType
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.role import Role
from app.models.user import User

setup_logging()
logger = get_logger(__name__)

SELLER_EMAIL = "seller@example.com"
SELLER_PASSWORD = "Seller123!"
CUSTOMER_EMAIL = "customer@example.com"
CUSTOMER_PASSWORD = "Customer123!"


def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role is None:
        role = Role(name=name)
        db.add(role)
        db.flush()
    return role


def _get_or_create_user(db: Session, *, email: str, full_name: str, password: str, role: Role) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            role_id=role.id,
            full_name=full_name,
            email=email,
            phone="0123456789",
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(user)
        db.flush()
    return user


def seed_data(db: Session) -> None:
    seller_role = _get_or_create_role(db, "seller")
    customer_role = _get_or_create_role(db, "customer")

    _get_or_create_user(
        db,
        email=SELLER_EMAIL,
        full_name="Seller Demo",
        password=SELLER_PASSWORD,
        role=seller_role,
    )
    _get_or_create_user(
        db,
        email=CUSTOMER_EMAIL,
        full_name="Customer Demo",
        password=CUSTOMER_PASSWORD,
        role=customer_role,
    )

    categories = [
        ("Thuc an cho cho", "dog-food", "Cac dong thuc an kho va uot danh cho cho"),
        ("Cat ve sinh cho meo", "cat-litter", "San pham cat ve sinh va khu mui cho meo"),
        ("Do choi thu cung", "pet-toy", "Cac loai do choi giup thu cung van dong va giai tri"),
    ]
    category_map: dict[str, Category] = {}
    for name, slug, description in categories:
        category = db.query(Category).filter(Category.slug == slug).first()
        if category is None:
            category = Category(name=name, slug=slug, description=description, is_active=True)
            db.add(category)
            db.flush()
        category_map[slug] = category

    products = [
        {
            "name": "Thuc an cho cao cap 5kg",
            "slug": "premium-dog-food-5kg",
            "sku": "DOG-001",
            "description": "Cong thuc can bang dinh duong cho cho truong thanh.",
            "price": "250000.00",
            "stock_quantity": 20,
            "brand": "Royal Pets",
            "pet_type": PetType.DOG,
            "category": category_map["dog-food"],
            "image_url": "https://example.com/dog-food-5kg.jpg",
        },
        {
            "name": "Cat ve sinh meo huong lavender",
            "slug": "cat-litter-lavender",
            "sku": "CAT-001",
            "description": "Cat ve sinh giup khu mui hieu qua cho meo.",
            "price": "120000.00",
            "stock_quantity": 15,
            "brand": "Clean Paws",
            "pet_type": PetType.CAT,
            "category": category_map["cat-litter"],
            "image_url": "https://example.com/cat-litter.jpg",
        },
        {
            "name": "Do choi day thung cho thu cung",
            "slug": "pet-rope-toy",
            "sku": "TOY-001",
            "description": "Do choi day ben chac giup thu cung van dong moi ngay.",
            "price": "50000.00",
            "stock_quantity": 30,
            "brand": "Happy Tail",
            "pet_type": PetType.DOG,
            "category": category_map["pet-toy"],
            "image_url": "https://example.com/pet-rope-toy.jpg",
        },
    ]
    for product_data in products:
        product = db.query(Product).filter(Product.slug == product_data["slug"]).first()
        if product is None:
            product = Product(
                category_id=product_data["category"].id,
                name=product_data["name"],
                slug=product_data["slug"],
                sku=product_data["sku"],
                description=product_data["description"],
                price=product_data["price"],
                stock_quantity=product_data["stock_quantity"],
                brand=product_data["brand"],
                pet_type=product_data["pet_type"],
                is_active=True,
            )
            product.images.append(
                ProductImage(
                    image_url=product_data["image_url"],
                    alt_text=product_data["name"],
                    is_primary=True,
                    sort_order=1,
                )
            )
            db.add(product)

    articles = [
        {
            "title": "Cach chon thuc an phu hop cho cho",
            "slug": "how-to-choose-dog-food",
            "summary": "Mot vai goi y don gian de chon dung loai thuc an cho cho.",
            "content": "Hay bat dau tu do tuoi, giong cho va muc do van dong hang ngay de chon khau phan phu hop.",
            "is_published": True,
            "published_at": datetime.now(UTC),
        },
        {
            "title": "Nhung dieu co ban khi chon cat ve sinh cho meo",
            "slug": "cat-litter-basics",
            "summary": "Cac tieu chi nen can nhac truoc khi mua cat ve sinh cho meo.",
            "content": "Ban nen xem xet kha nang khu mui, do bui va kha nang von cuc truoc khi lua chon.",
            "is_published": False,
            "published_at": None,
        },
    ]
    for article_data in articles:
        article = db.query(Article).filter(Article.slug == article_data["slug"]).first()
        if article is None:
            article = Article(**article_data)
            db.add(article)

    db.commit()
    logger.info("Seed data completed")


def main() -> None:
    with SessionLocal() as db:
        seed_data(db)


if __name__ == "__main__":
    main()

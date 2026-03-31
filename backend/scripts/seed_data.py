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

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"
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
    admin_role = _get_or_create_role(db, "admin")
    customer_role = _get_or_create_role(db, "customer")

    _get_or_create_user(
        db,
        email=ADMIN_EMAIL,
        full_name="Quản trị viên Demo",
        password=ADMIN_PASSWORD,
        role=admin_role,
    )
    _get_or_create_user(
        db,
        email=CUSTOMER_EMAIL,
        full_name="Khách hàng Demo",
        password=CUSTOMER_PASSWORD,
        role=customer_role,
    )

    categories = [
        ("Thức ăn cho chó", "dog-food", "Các dòng thức ăn khô và ướt dành cho chó"),
        ("Cát vệ sinh cho mèo", "cat-litter", "Sản phẩm cát vệ sinh và khử mùi cho mèo"),
        ("Đồ chơi thú cưng", "pet-toy", "Các loại đồ chơi giúp thú cưng vận động và giải trí"),
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
            "name": "Thức ăn chó cao cấp 5kg",
            "slug": "premium-dog-food-5kg",
            "sku": "DOG-001",
            "description": "Công thức cân bằng dinh dưỡng cho chó trưởng thành.",
            "price": "250000.00",
            "stock_quantity": 20,
            "brand": "Royal Pets",
            "pet_type": PetType.DOG,
            "category": category_map["dog-food"],
            "image_url": "https://example.com/dog-food-5kg.jpg",
        },
        {
            "name": "Cát vệ sinh mèo hương lavender",
            "slug": "cat-litter-lavender",
            "sku": "CAT-001",
            "description": "Cát vệ sinh giúp khử mùi hiệu quả cho mèo.",
            "price": "120000.00",
            "stock_quantity": 15,
            "brand": "Clean Paws",
            "pet_type": PetType.CAT,
            "category": category_map["cat-litter"],
            "image_url": "https://example.com/cat-litter.jpg",
        },
        {
            "name": "Đồ chơi dây thừng cho thú cưng",
            "slug": "pet-rope-toy",
            "sku": "TOY-001",
            "description": "Đồ chơi dây bền chắc giúp thú cưng vận động mỗi ngày.",
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
            "title": "Cách chọn thức ăn phù hợp cho chó",
            "slug": "how-to-choose-dog-food",
            "summary": "Một vài gợi ý đơn giản để chọn đúng loại thức ăn cho chó.",
            "content": "Hãy bắt đầu từ độ tuổi, giống chó và mức độ vận động hằng ngày để chọn khẩu phần phù hợp.",
            "is_published": True,
            "published_at": datetime.now(UTC),
        },
        {
            "title": "Những điều cơ bản khi chọn cát vệ sinh cho mèo",
            "slug": "cat-litter-basics",
            "summary": "Các tiêu chí nên cân nhắc trước khi mua cát vệ sinh cho mèo.",
            "content": "Bạn nên xem xét khả năng khử mùi, độ bụi và khả năng vón cục trước khi lựa chọn.",
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

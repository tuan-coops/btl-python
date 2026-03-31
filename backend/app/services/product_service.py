from decimal import Decimal

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductDetailResponse,
    ProductImageResponse,
    ProductListItemResponse,
    ProductListResponse,
)


def _primary_image_url(product: Product) -> str | None:
    primary = next((image for image in product.images if image.is_primary), None)
    if primary is not None:
        return primary.image_url
    if product.images:
        return product.images[0].image_url
    return None


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def list_products(
        self,
        *,
        search: str | None,
        category_id: int | None,
        pet_type: str | None,
        brand: str | None,
        price_min: Decimal | None,
        price_max: Decimal | None,
        page: int,
        page_size: int,
    ) -> ProductListResponse:
        products, total = self.repository.list_products(
            search=search,
            category_id=category_id,
            pet_type=pet_type,
            brand=brand,
            price_min=price_min,
            price_max=price_max,
            page=page,
            page_size=page_size,
        )
        items = [
            ProductListItemResponse(
                id=product.id,
                name=product.name,
                slug=product.slug,
                price=product.price,
                stock_quantity=product.stock_quantity,
                brand=product.brand,
                pet_type=product.pet_type.value,
                category=product.category.name,
                primary_image=_primary_image_url(product),
            )
            for product in products
        ]
        return ProductListResponse(items=items, total=total, page=page, page_size=page_size)

    def get_product_detail(self, product_id: int) -> ProductDetailResponse | None:
        product = self.repository.get_product_by_id(product_id)
        if product is None:
            return None
        return ProductDetailResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            brand=product.brand,
            pet_type=product.pet_type.value,
            category=product.category.name,
            images=[
                ProductImageResponse(
                    id=image.id,
                    image_url=image.image_url,
                    alt_text=image.alt_text,
                    is_primary=image.is_primary,
                    sort_order=image.sort_order,
                )
                for image in product.images
            ],
        )

from fastapi import APIRouter

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.articles import router as articles_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.cart import router as cart_router
from app.api.v1.routes.categories import router as categories_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.orders import router as orders_router
from app.api.v1.routes.products import router as products_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(articles_router)
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(products_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(health_router, tags=["health"])

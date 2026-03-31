from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.article_repository import ArticleRepository
from app.schemas.article import ArticleDetailResponse, ArticleListResponse
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
def list_articles(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ArticleListResponse:
    return ArticleService(ArticleRepository(db)).list_articles(search=search, page=page, page_size=page_size)


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article(article_id: int, db: Session = Depends(get_db)) -> ArticleDetailResponse:
    return ArticleService(ArticleRepository(db)).get_article(article_id)

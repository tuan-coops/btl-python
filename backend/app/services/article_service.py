from fastapi import HTTPException, status

from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.schemas.article import ArticleDetailResponse, ArticleListItemResponse, ArticleListResponse


class ArticleService:
    def __init__(self, repository: ArticleRepository) -> None:
        self.repository = repository

    def list_articles(self, *, search: str | None, page: int, page_size: int) -> ArticleListResponse:
        items, total = self.repository.list_published_articles(search=search, page=page, page_size=page_size)
        return ArticleListResponse(
            items=[ArticleListItemResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_article(self, article_id: int) -> ArticleDetailResponse:
        article = self.repository.get_published_by_id(article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return ArticleDetailResponse.model_validate(article)

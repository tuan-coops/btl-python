from sqlalchemy.orm import Session

from app.models.article import Article


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_published_articles(
        self,
        *,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Article], int]:
        query = self.db.query(Article).filter(Article.is_published.is_(True))
        if search:
            query = query.filter(Article.title.ilike(f"%{search.strip()}%"))
        total = query.count()
        items = (
            query.order_by(Article.published_at.desc(), Article.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_published_by_id(self, article_id: int) -> Article | None:
        return (
            self.db.query(Article)
            .filter(Article.id == article_id, Article.is_published.is_(True))
            .first()
        )

    def get_by_id(self, article_id: int) -> Article | None:
        return self.db.query(Article).filter(Article.id == article_id).first()

    def get_by_slug(self, slug: str) -> Article | None:
        return self.db.query(Article).filter(Article.slug == slug).first()

    def list_all(
        self,
        *,
        is_published: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Article], int]:
        query = self.db.query(Article)
        if is_published is not None:
            query = query.filter(Article.is_published.is_(is_published))
        total = query.count()
        items = (
            query.order_by(Article.created_at.desc(), Article.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

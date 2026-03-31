from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArticleListItemResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ArticleDetailResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    content: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    items: list[ArticleListItemResponse]
    total: int
    page: int
    page_size: int


class SellerArticleCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    content: str = Field(min_length=1)
    is_published: bool = False


class SellerArticleUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    content: str | None = None
    is_published: bool | None = None


class SellerArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    content: str
    is_published: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SellerArticleListResponse(BaseModel):
    items: list[SellerArticleResponse]
    total: int
    page: int
    page_size: int

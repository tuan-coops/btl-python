from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)

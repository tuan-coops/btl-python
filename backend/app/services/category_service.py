from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryResponse


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def list_categories(self) -> list[CategoryResponse]:
        return [CategoryResponse.model_validate(category) for category in self.repository.list_categories()]

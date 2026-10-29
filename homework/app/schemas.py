from pydantic import BaseModel, Field


class IngredientBase(BaseModel):
    """Базовая схема ингредиента."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Название ингредиента"
    )
    quantity: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Количество, например '2 стакана'",
    )


class IngredientIn(IngredientBase):
    """Схема для создания ингредиента (приходит в запросе)."""

    ...


class IngredientOut(IngredientBase):
    """Схема для возврата ингредиента (с id)."""

    id: int = Field(..., description="Уникальный идентификатор ингредиента")

    model_config = {"from_attributes": True}


class RecipeBase(BaseModel):
    """Базовая схема рецепта."""

    name: str = Field(..., min_length=1, max_length=255, description="Название блюда")
    cooking_time: int = Field(..., gt=0, description="Время приготовления в минутах")
    description: str = Field(
        ..., min_length=1, description="Текстовое описание рецепта"
    )


class RecipeCreate(RecipeBase):
    """Схема для создания рецепта (POST-запрос)."""

    ingredients: list[IngredientIn] = Field(
        ..., min_length=1, description="Список ингредиентов"
    )


class RecipeShort(BaseModel):
    """Краткая схема рецепта для списка (экран 1)."""

    id: int = Field(..., description="Уникальный идентификатор рецепта")
    name: str = Field(..., description="Название блюда")
    views: int = Field(..., description="Количество просмотров")
    cooking_time: int = Field(..., description="Время приготовления в минутах")

    model_config = {"from_attributes": True}


class RecipeDetail(BaseModel):
    """Полная схема рецепта для детальной страницы (экран 2)."""

    id: int = Field(..., description="Уникальный идентификатор рецепта")
    name: str = Field(..., description="Название блюда")
    cooking_time: int = Field(..., description="Время приготовления в минутах")
    description: str = Field(..., description="Текстовое описание рецепта")
    views: int = Field(..., description="Количество просмотров")
    ingredients: list[IngredientOut] = Field(..., description="Список ингредиентов")

    model_config = {"from_attributes": True}

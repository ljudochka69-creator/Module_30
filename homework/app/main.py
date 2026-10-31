from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import .models
import schemas
import uvicorn
from database import SessionLocal, engine
from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Создаёт таблицы при старте, закрывает соединение при остановке."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Кулинарная книга",
    description=(
        "API для управления рецептами. "
        "Список рецептов сортируется по популярности (просмотры) "
        "и времени приготовления."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/recipes", response_model=list[schemas.RecipeShort], tags=["Recipes"])
async def get_recipes(
    db: AsyncSession = Depends(get_session),
) -> list[schemas.RecipeShort]:
    """
    Получить список всех рецептов.

    Возвращает краткую информацию по каждому рецепту:
    - название блюда
    - количество просмотров
    - время приготовления в минутах

    **Сортировка:** по убыванию количества просмотров (популярные первыми),
    при равенстве — по возрастанию времени приготовления.
    """

    async with SessionLocal() as s:
        stmt = select(models.Recipe).order_by(
            models.Recipe.views.desc(),
            models.Recipe.cooking_time.asc(),
        )
        result = await s.execute(stmt)
        recipes = result.scalars().all()
        return [schemas.RecipeShort.model_validate(r) for r in recipes]


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetail,
    tags=["Recipes"],
)
async def get_recipe(recipe_id: int) -> schemas.RecipeDetail:
    """
    Получить детальную информацию о конкретном рецепте.

    Возвращает полную информацию:
    - название блюда
    - время приготовления
    - список ингредиентов
    - текстовое описание

    **Побочный эффект:** при каждом вызове увеличивает счётчик просмотров на 1.
    """
    async with SessionLocal() as s:
        stmt = (
            select(models.Recipe)
            .where(models.Recipe.id == recipe_id)
            .options(selectinload(models.Recipe.ingredients))
        )
        result = await s.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рецепт с id={recipe_id} не найден",
            )

        recipe.views += 1
        await s.commit()
        await s.refresh(recipe)

        return schemas.RecipeDetail.model_validate(recipe)


@app.post(
    "/recipes",
    response_model=schemas.RecipeDetail,
    status_code=status.HTTP_201_CREATED,
    tags=["Recipes"],
)
async def create_recipe(recipe: schemas.RecipeCreate) -> schemas.RecipeDetail:
    """
    Создать новый рецепт.

    Тело запроса:
    - `name` — название блюда
    - `cooking_time` — время приготовления в минутах
    - `description` — текстовое описание
    - `ingredients` — список ингредиентов (минимум один)

    Возвращает созданный рецепт с присвоенным id и пустым счётчиком просмотров.
    """
    async with SessionLocal() as s:
        new_recipe = models.Recipe(
            name=recipe.name,
            cooking_time=recipe.cooking_time,
            description=recipe.description,
            ingredients=[
                models.Ingredient(name=ing.name, quantity=ing.quantity)
                for ing in recipe.ingredients
            ],
        )
        s.add(new_recipe)
        await s.commit()
        await s.refresh(new_recipe)

        return schemas.RecipeDetail.model_validate(new_recipe)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient) -> None:
    """Создание рецепта — POST /recipes."""
    payload = {
        "name": "Борщ",
        "cooking_time": 90,
        "description": "Классический борщ со свёклой.",
        "ingredients": [
            {"name": "Свёкла", "quantity": "2 шт"},
            {"name": "Капуста", "quantity": "300 г"},
        ],
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/recipes", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Борщ"
    assert data["cooking_time"] == 90
    assert data["views"] == 0
    assert len(data["ingredients"]) == 2


@pytest.mark.anyio
async def test_get_recipe_increments_views() -> None:
    """Открытие детального рецепта увеличивает просмотры."""
    payload = {
        "name": "Паста Карбонара",
        "cooking_time": 25,
        "description": "Итальянская паста с беконом.",
        "ingredients": [{"name": "Спагетти", "quantity": "200 г"}],
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/recipes", json=payload)
        recipe_id = created.json()["id"]

        resp1 = await client.get(f"/recipes/{recipe_id}")
        resp2 = await client.get(f"/recipes/{recipe_id}")

    assert resp1.json()["views"] == 1
    assert resp2.json()["views"] == 2


@pytest.mark.anyio
async def test_get_recipe_not_found() -> None:
    """Запрос несуществующего рецепта — 404."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/recipes/9999")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_recipe_list_sorted_by_views() -> None:
    """
    Список рецептов отсортирован по просмотрам (убывание), затем по времени.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        r1 = await client.post(
            "/recipes",
            json={
                "name": "Омлет",
                "cooking_time": 10,
                "description": "...",
                "ingredients": [{"name": "Яйцо", "quantity": "3 шт"}],
            },
        )
        r2 = await client.post(
            "/recipes",
            json={
                "name": "Суп",
                "cooking_time": 60,
                "description": "...",
                "ingredients": [{"name": "Вода", "quantity": "1 л"}],
            },
        )

        # Открываем омлет 3 раза, суп — 1 раз
        for _ in range(3):
            await client.get(f"/recipes/{r1.json()['id']}")
        await client.get(f"/recipes/{r2.json()['id']}")

        resp = await client.get("/recipes")
        recipes = resp.json()

    assert recipes[0]["name"] == "Омлет"
    assert recipes[0]["views"] == 3
    assert recipes[1]["name"] == "Суп"
    assert recipes[1]["views"] == 1

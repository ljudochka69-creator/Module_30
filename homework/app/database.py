from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from types import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# URL для базы данных
DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"

# Создаем движок с дополнительными параметрами
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Включаем логирование SQL запросов
    future=True,  # Используем Future-совместимый движок
    connect_args={"check_same_thread": False}  # Для SQLite
)

# Создаем фабрику сессий
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Функция для получения сессии
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
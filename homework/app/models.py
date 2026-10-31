from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    """Модель рецепта."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Название блюда")
    cooking_time = Column(
        Integer, nullable=False, comment="Время приготовления в минутах"
    )
    description = Column(Text, nullable=False, comment="Текстовое описание рецепта")
    views: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Количество просмотров"
    )

    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Ingredient(Base):
    """Модель ингредиента."""

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="Название ингредиента")
    quantity = Column(
        String(100), nullable=False, comment="Количество, например '2 стакана'"
    )
    recipe_id = Column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )

    recipe = relationship("Recipe", back_populates="ingredients")

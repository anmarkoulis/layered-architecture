from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.concrete import SQLPizzaDAO
from layered_architecture.dto.pizza import PizzaDTO


class TestSQLPizzaDAO:
    @pytest.mark.asyncio
    async def test_get_by_id(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLPizzaDAO(db)
        # Get a pizza ID from the seeded data
        result = await db.execute(
            text("SELECT id FROM pizza WHERE name = 'Margherita' LIMIT 1")
        )
        pizza_id = result.scalar_one()

        # When
        pizza = await dao.get_by_id(str(pizza_id))

        # Then
        assert pizza is not None
        assert isinstance(pizza, PizzaDTO)
        assert pizza.name == "Margherita"
        assert pizza.price == Decimal("12.99")
        assert (
            pizza.description
            == "Classic tomato sauce, mozzarella, fresh basil"
        )

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLPizzaDAO(db)
        nonexistent_id = str(uuid4())

        # When
        pizza = await dao.get_by_id(nonexistent_id)

        # Then
        assert pizza is None

    @pytest.mark.asyncio
    async def test_get_by_name(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLPizzaDAO(db)
        pizza_name = "Pepperoni"

        # When
        pizza = await dao.get_by_name(pizza_name)

        # Then
        assert pizza is not None
        assert isinstance(pizza, PizzaDTO)
        assert pizza.name == pizza_name
        assert pizza.price == Decimal("14.99")
        assert pizza.description == "Tomato sauce, mozzarella, spicy pepperoni"

    @pytest.mark.asyncio
    async def test_get_by_name_nonexistent(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLPizzaDAO(db)
        nonexistent_name = "NonexistentPizza"

        # When
        pizza = await dao.get_by_name(nonexistent_name)

        # Then
        assert pizza is None

    @pytest.mark.asyncio
    async def test_get_all(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLPizzaDAO(db)

        # When
        pizzas = await dao.get_all()

        # Then
        assert len(pizzas) > 0
        assert all(isinstance(pizza, PizzaDTO) for pizza in pizzas)
        # Verify we have some known pizzas
        pizza_names = {pizza.name for pizza in pizzas}
        assert "Margherita" in pizza_names
        assert "Pepperoni" in pizza_names
        assert "Quattro Formaggi" in pizza_names

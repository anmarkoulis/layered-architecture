from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.concrete import SQLBeerDAO
from layered_architecture.dto.beer import BeerDTO


class TestSQLBeerDAO:
    @pytest.mark.asyncio
    async def test_get_by_id(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLBeerDAO(db)
        # Get a beer ID from the seeded data
        result = await db.execute(
            text("SELECT id FROM beer WHERE name = 'Heineken' LIMIT 1")
        )
        beer_id = result.scalar_one()

        # When
        beer = await dao.get_by_id(str(beer_id))

        # Then
        assert beer is not None
        assert isinstance(beer, BeerDTO)
        assert beer.name == "Heineken"
        assert beer.price == Decimal("5.99")

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLBeerDAO(db)
        nonexistent_id = str(uuid4())

        # When
        beer = await dao.get_by_id(nonexistent_id)

        # Then
        assert beer is None

    @pytest.mark.asyncio
    async def test_get_by_name(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLBeerDAO(db)
        beer_name = "Stella Artois"

        # When
        beer = await dao.get_by_name(beer_name)

        # Then
        assert beer is not None
        assert isinstance(beer, BeerDTO)
        assert beer.name == beer_name
        assert beer.price == Decimal("6.49")

    @pytest.mark.asyncio
    async def test_get_by_name_nonexistent(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLBeerDAO(db)
        nonexistent_name = "NonexistentBeer"

        # When
        beer = await dao.get_by_name(nonexistent_name)

        # Then
        assert beer is None

    @pytest.mark.asyncio
    async def test_get_all(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLBeerDAO(db)

        # When
        beers = await dao.get_all()

        # Then
        assert len(beers) > 0
        assert all(isinstance(beer, BeerDTO) for beer in beers)
        # Verify we have both bottled and tap beers
        beer_names = {beer.name for beer in beers}
        assert "Heineken" in beer_names  # Bottled beer
        assert "Pilsner Urquell" in beer_names  # Tap beer

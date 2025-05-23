from typing import List, Optional

from sqlalchemy import Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.interfaces import BeerDAOInterface
from layered_architecture.db.models import Beer
from layered_architecture.dto.beer import BeerDTO


class SQLBeerDAO(BeerDAOInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, beer_id: str) -> Optional[BeerDTO]:
        result = await self.session.execute(
            select(Beer).where(Beer.id == beer_id)
        )
        beer = result.scalar_one_or_none()
        if not beer:
            return None
        return BeerDTO.model_validate(beer)

    async def get_by_name(self, name: str) -> Optional[BeerDTO]:
        result = await self.session.execute(
            select(Beer).where(Beer.name == name)
        )
        beer = result.scalar_one_or_none()
        if not beer:
            return None
        return BeerDTO.model_validate(beer)

    async def get_all(self) -> List[BeerDTO]:
        result = await self.session.execute(
            select(Beer).where(Beer.is_available == Boolean(True))
        )
        beers = result.scalars().all()
        return [BeerDTO.model_validate(beer) for beer in beers]

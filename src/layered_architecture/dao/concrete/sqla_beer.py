from typing import List, Optional

from sqlalchemy import Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.interfaces.beer import BeerDAO
from layered_architecture.db.models.beer import Beer
from layered_architecture.dto.order import OrderItemDTO


class SQLBeerDAO(BeerDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, beer_id: str) -> Optional[OrderItemDTO]:
        result = await self.session.execute(
            select(Beer).where(Beer.id == beer_id)
        )
        beer = result.scalar_one_or_none()
        if not beer:
            return None
        return OrderItemDTO(
            product_id=beer.id,
            quantity=1,  # Default quantity
            price=beer.price,
        )

    async def get_all(self) -> List[OrderItemDTO]:
        result = await self.session.execute(
            select(Beer).where(Beer.is_available == Boolean(True))
        )
        beers = result.scalars().all()
        return [
            OrderItemDTO(
                product_id=beer.id,
                quantity=1,  # Default quantity
                price=beer.price,
            )
            for beer in beers
        ]

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.interfaces import PizzaDAOInterface
from layered_architecture.db.models import Pizza
from layered_architecture.dto.pizza import PizzaDTO


class SQLPizzaDAO(PizzaDAOInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pizza_id: str) -> Optional[PizzaDTO]:
        result = await self.session.execute(
            select(Pizza).where(Pizza.id == pizza_id)
        )
        pizza = result.scalar_one_or_none()
        if not pizza:
            return None
        return PizzaDTO.model_validate(pizza)

    async def get_by_name(self, name: str) -> Optional[PizzaDTO]:
        result = await self.session.execute(
            select(Pizza).where(Pizza.name == name)
        )
        pizza = result.scalar_one_or_none()
        if not pizza:
            return None
        return PizzaDTO.model_validate(pizza)

    async def get_all(self) -> List[PizzaDTO]:
        result = await self.session.execute(select(Pizza))
        pizzas = result.scalars().all()
        return [PizzaDTO.model_validate(pizza) for pizza in pizzas]

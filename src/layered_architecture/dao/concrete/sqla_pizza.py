from typing import List, Optional

from sqlalchemy import Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.interfaces.pizza import PizzaDAO
from layered_architecture.db.models.pizza import Pizza
from layered_architecture.dto.order import OrderItemDTO


class SQLPizzaDAO(PizzaDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pizza_id: str) -> Optional[OrderItemDTO]:
        result = await self.session.execute(
            select(Pizza).where(Pizza.id == pizza_id)
        )
        pizza = result.scalar_one_or_none()
        if not pizza:
            return None
        return OrderItemDTO(
            product_id=pizza.id,
            quantity=1,  # Default quantity
            price=pizza.price,
        )

    async def get_all(self) -> List[OrderItemDTO]:
        result = await self.session.execute(
            select(Pizza).where(Pizza.is_available == Boolean(True))
        )
        pizzas = result.scalars().all()
        return [
            OrderItemDTO(
                product_id=pizza.id,
                quantity=1,  # Default quantity
                price=pizza.price,
            )
            for pizza in pizzas
        ]

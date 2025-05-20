from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.interfaces.order import OrderDAO
from layered_architecture.db.models.beer import Beer
from layered_architecture.db.models.order import Order
from layered_architecture.db.models.order_beer import OrderBeer
from layered_architecture.db.models.order_pizza import OrderPizza
from layered_architecture.db.models.pizza import Pizza
from layered_architecture.dto.order import (
    OrderDTO,
    OrderInputDTO,
    OrderItemDTO,
)


class SQLOrderDAO(OrderDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order_input: OrderInputDTO) -> OrderDTO:
        # Create order
        order = Order(
            store_type=order_input.store_type,
            customer_id=order_input.customer_id,
            status="pending",
            total_amount=str(order_input.total),
        )

        # Add items to order
        for item in order_input.items:
            if item.type == "pizza":
                order_pizza = OrderPizza(
                    order_id=order.id,
                    pizza_id=item.product_id,
                    quantity=item.quantity,
                )
                self.session.add(order_pizza)
            elif item.type == "beer":
                order_beer = OrderBeer(
                    order_id=order.id,
                    beer_id=item.product_id,
                    quantity=item.quantity,
                )
                self.session.add(order_beer)

        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)

        return OrderDTO(
            id=str(order.id),
            store_type=order.store_type,
            customer_id=order_input.customer_id,
            items=order_input.items,
            total=order_input.total,
        )

    async def get_by_id(self, order_id: str) -> Optional[OrderDTO]:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return None

        # Get items
        items: List[OrderItemDTO] = []

        # Get pizzas
        pizza_result = await self.session.execute(
            select(OrderPizza).where(OrderPizza.order_id == order_id)
        )
        for pizza_row in pizza_result:
            pizza = await self.session.get(Pizza, pizza_row.pizza_id)
            if pizza is None:
                continue
            items.append(
                OrderItemDTO(
                    product_id=str(pizza.id),
                    quantity=pizza_row.quantity,
                    price=pizza.price,
                )
            )

        # Get beers
        beer_result = await self.session.execute(
            select(OrderBeer).where(OrderBeer.order_id == order_id)
        )
        for beer_row in beer_result:
            beer = await self.session.get(Beer, beer_row.beer_id)
            if beer is None:
                continue
            items.append(
                OrderItemDTO(
                    product_id=str(beer.id),
                    quantity=beer_row.quantity,
                    price=beer.price,
                )
            )

        return OrderDTO(
            id=str(order.id),
            store_type=order.store_type,
            customer_id=order.customer_id,
            items=items,
            total=Decimal(order.total_amount),
        )

    async def get_all(self) -> List[OrderDTO]:
        result = await self.session.execute(select(Order))
        orders = result.scalars().all()

        order_dtos = []
        for order in orders:
            # Get items for each order
            items: List[OrderItemDTO] = []

            # Get pizzas
            pizza_result = await self.session.execute(
                select(OrderPizza).where(OrderPizza.order_id == order.id)
            )
            for pizza_row in pizza_result:
                pizza = await self.session.get(Pizza, pizza_row.pizza_id)
                if pizza is None:
                    continue
                items.append(
                    OrderItemDTO(
                        product_id=str(pizza.id),
                        quantity=pizza_row.quantity,
                        price=pizza.price,
                    )
                )

            # Get beers
            beer_result = await self.session.execute(
                select(OrderBeer).where(OrderBeer.order_id == order.id)
            )
            for beer_row in beer_result:
                beer = await self.session.get(Beer, beer_row.beer_id)
                if beer is None:
                    continue
                items.append(
                    OrderItemDTO(
                        product_id=str(beer.id),
                        quantity=beer_row.quantity,
                        price=beer.price,
                    )
                )

            order_dtos.append(
                OrderDTO(
                    id=str(order.id),
                    store_type=order.store_type,
                    customer_id=order.customer_id,
                    items=items,
                    total=Decimal(order.total_amount),
                )
            )

        return order_dtos

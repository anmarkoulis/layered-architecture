from decimal import Decimal

from layered_architecture.dao.interfaces import BeerDAO, OrderDAO, PizzaDAO
from layered_architecture.db.uow import SQLAUnitOfWork
from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.services.interfaces.order import OrderService


class DowntownOrderService(OrderService):
    """Service for handling downtown store orders with special pricing."""

    DOWNTOWN_TAX_RATE = Decimal("0.08")  # 8% tax for downtown location

    def __init__(
        self,
        pizza_dao: PizzaDAO,
        beer_dao: BeerDAO,
        order_dao: OrderDAO,
        uow: SQLAUnitOfWork,
    ):
        self.pizza_dao = pizza_dao
        self.beer_dao = beer_dao
        self.order_dao = order_dao
        self.uow = uow

    async def create_order(self, order_input: OrderInputDTO) -> OrderDTO:
        """Create a downtown store order with special pricing."""
        async with self.uow:
            # Calculate subtotal
            subtotal = Decimal("0")
            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_id(item.id)
                    subtotal += pizza.price * item.quantity
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_id(item.id)
                    subtotal += beer.price * item.quantity

            # Add downtown tax
            tax_amount = subtotal * self.DOWNTOWN_TAX_RATE
            final_total = subtotal + tax_amount

            # Create order with downtown pricing
            order_input.total = final_total
            order = await self.order_dao.create(order_input)

            await self.uow.commit()
            return OrderDTO.model_validate(order)

from decimal import Decimal

from layered_architecture.dao.interfaces import BeerDAO, OrderDAO, PizzaDAO
from layered_architecture.db.uow import SQLAUnitOfWork
from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.services.interfaces.order import OrderService


class MallOrderService(OrderService):
    """Service for handling mall store orders with special pricing."""

    MALL_TAX_RATE = Decimal("0.06")  # 6% tax for mall location
    MALL_DISCOUNT_THRESHOLD = Decimal("30.00")  # $30 threshold for discount
    MALL_DISCOUNT_RATE = Decimal("0.90")  # 10% discount

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

    def _calculate_discount(self, subtotal: Decimal) -> Decimal:
        """Calculate discount rate based on order amount."""
        if subtotal >= self.MALL_DISCOUNT_THRESHOLD:
            return self.MALL_DISCOUNT_RATE
        return Decimal("1.0")

    async def create_order(self, order_input: OrderInputDTO) -> OrderDTO:
        """Create a mall store order with special pricing."""
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

            # Apply mall discount if applicable
            discount_rate = self._calculate_discount(subtotal)
            discounted_total = subtotal * discount_rate

            # Add mall tax
            tax_amount = discounted_total * self.MALL_TAX_RATE
            final_total = discounted_total + tax_amount

            # Create order with mall pricing
            order = await self.order_dao.create(
                store_type=order_input.store_type,
                customer_id=order_input.customer_id,
                total=final_total,
                items=order_input.items,
            )

            await self.uow.commit()
            return OrderDTO.model_validate(order)

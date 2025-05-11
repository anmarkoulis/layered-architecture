from decimal import Decimal
from typing import Optional

from layered_architecture.dao.interfaces import BeerDAO, OrderDAO, PizzaDAO
from layered_architecture.db.uow.sqla import SQLAUnitOfWork
from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.services.interfaces.order import OrderService


class DeliveryOrderService(OrderService):
    """Service for handling delivery orders with delivery fee calculations."""

    BASE_DELIVERY_FEE = Decimal("5.00")
    DISTANCE_RATE = Decimal("0.50")  # per km
    MIN_ORDER_AMOUNT = Decimal("20.00")
    FREE_DELIVERY_THRESHOLD = Decimal("50.00")

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

    def _calculate_delivery_fee(
        self, subtotal: Decimal, distance_km: Optional[float] = None
    ) -> Decimal:
        """Calculate delivery fee based on order amount and distance."""
        if subtotal >= self.FREE_DELIVERY_THRESHOLD:
            return Decimal("0")

        if subtotal < self.MIN_ORDER_AMOUNT:
            raise ValueError(
                f"Minimum order amount is {self.MIN_ORDER_AMOUNT}"
            )

        fee = self.BASE_DELIVERY_FEE
        if distance_km is not None:
            fee += Decimal(str(distance_km)) * self.DISTANCE_RATE

        return fee

    async def create_order(
        self, order_input: OrderInputDTO, distance_km: Optional[float] = None
    ) -> OrderDTO:
        """Create a delivery order with delivery fee calculation."""
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

            # Calculate delivery fee
            delivery_fee = self._calculate_delivery_fee(subtotal, distance_km)
            final_total = subtotal + delivery_fee

            # Create order with delivery fee
            order_input.total = final_total
            order = await self.order_dao.create(order_input)

            await self.uow.commit()
            return OrderDTO.model_validate(order)

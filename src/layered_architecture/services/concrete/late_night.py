from datetime import datetime, time
from decimal import Decimal

from layered_architecture.dao.interfaces import BeerDAO, OrderDAO, PizzaDAO
from layered_architecture.db.uow.sqla import SQLAUnitOfWork
from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.services.interfaces.order import OrderService


class LateNightOrderService(OrderService):
    """Service for handling late night orders with special pricing and rules."""

    LATE_NIGHT_START = time(22, 0)  # 10 PM
    LATE_NIGHT_END = time(4, 0)  # 4 AM
    LATE_NIGHT_SURCHARGE = Decimal("1.20")  # 20% surcharge

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

    def _is_late_night(self) -> bool:
        """Check if current time is within late night hours."""
        current_time = datetime.now().time()
        if (
            self.LATE_NIGHT_START <= current_time
            or current_time <= self.LATE_NIGHT_END
        ):
            return True
        return False

    async def create_order(self, order_input: OrderInputDTO) -> OrderDTO:
        """Create a late night order with special pricing."""
        if not self._is_late_night():
            raise ValueError(
                "Late night orders are only accepted between 10 PM and 4 AM"
            )

        async with self.uow:
            # Calculate total with late night surcharge
            total = Decimal("0")
            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_id(item.id)
                    total += (
                        pizza.price * item.quantity * self.LATE_NIGHT_SURCHARGE
                    )
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_id(item.id)
                    total += (
                        beer.price * item.quantity * self.LATE_NIGHT_SURCHARGE
                    )

            # Create order with surcharge
            order = await self.order_dao.create(
                store_type=order_input.store_type,
                customer_id=order_input.customer_id,
                total=total,
                items=order_input.items,
            )

            await self.uow.commit()
            return OrderDTO.model_validate(order)

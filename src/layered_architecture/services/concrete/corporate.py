from decimal import Decimal

from layered_architecture.dao.interfaces import BeerDAO, OrderDAO, PizzaDAO
from layered_architecture.db.uow.sqla import SQLAUnitOfWork
from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.services.interfaces.order import OrderService


class CorporateOrderService(OrderService):
    """Service for handling corporate orders with bulk discounts and special handling."""

    BULK_DISCOUNT_THRESHOLD = 10  # items
    BULK_DISCOUNT_RATE = Decimal("0.85")  # 15% discount
    CORPORATE_TAX_RATE = Decimal("0.10")  # 10% tax for corporate orders

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

    def _calculate_bulk_discount(self, total_items: int) -> Decimal:
        """Calculate bulk discount rate based on total items."""
        if total_items >= self.BULK_DISCOUNT_THRESHOLD:
            return self.BULK_DISCOUNT_RATE
        return Decimal("1.0")

    async def create_order(self, order_input: OrderInputDTO) -> OrderDTO:
        """Create a corporate order with bulk discounts and tax handling."""
        async with self.uow:
            # Calculate subtotal and count total items
            subtotal = Decimal("0")
            total_items = 0

            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_id(item.id)
                    subtotal += pizza.price * item.quantity
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_id(item.id)
                    subtotal += beer.price * item.quantity
                total_items += item.quantity

            # Apply bulk discount if applicable
            discount_rate = self._calculate_bulk_discount(total_items)
            discounted_total = subtotal * discount_rate

            # Add corporate tax
            tax_amount = discounted_total * self.CORPORATE_TAX_RATE
            final_total = discounted_total + tax_amount

            # Create order with corporate pricing
            order_input.total = final_total
            order = await self.order_dao.create(order_input)

            await self.uow.commit()
            return OrderDTO.model_validate(order)

from typing import List, Optional

from layered_architecture.dao.interfaces import (
    BeerDAOInterface,
    OrderDAOInterface,
    PizzaDAOInterface,
)
from layered_architecture.db.uow.base import BaseUnitOfWork
from layered_architecture.dto.order import (
    OrderDTO,
    OrderItemInputDTO,
    OrderUpdateInternalDTO,
)
from layered_architecture.dto.user import UserReadDTO
from layered_architecture.enums import OrderStatus
from layered_architecture.exceptions import NotFoundError
from layered_architecture.services.interfaces.order import (
    OrderServiceInterface,
)


class BaseOrderService(OrderServiceInterface):
    """Base class for order services with common functionality."""

    def __init__(
        self,
        pizza_dao: PizzaDAOInterface,
        beer_dao: BeerDAOInterface,
        order_dao: OrderDAOInterface,
        uow: BaseUnitOfWork,
    ):
        """Initialize the base order service.

        :param pizza_dao: The pizza DAO
        :type pizza_dao: PizzaDAOInterface
        :param beer_dao: The beer DAO
        :type beer_dao: BeerDAOInterface
        :param order_dao: The order DAO
        :type order_dao: OrderDAOInterface
        :param uow: The unit of work
        :type uow: BaseUnitOfWork
        """
        self.pizza_dao = pizza_dao
        self.beer_dao = beer_dao
        self.order_dao = order_dao
        self.uow = uow

    async def cancel_pending_orders(
        self,
        user: UserReadDTO,
        reason: Optional[str] = None,
    ) -> List[OrderDTO]:
        """Cancel all pending orders.

        :param user: The user cancelling the orders
        :type user: UserReadDTO
        :param reason: Optional reason for cancellation
        :type reason: Optional[str]
        :return: List of cancelled orders
        :rtype: List[OrderDTO]
        """
        async with self.uow:
            # Get all pending orders
            pending_orders = await self.order_dao.get_all(
                status=OrderStatus.PENDING
            )
            cancelled_orders = []

            for order in pending_orders:
                # Convert OrderItemDTO to OrderItemInputDTO
                items = []
                for item in order.items:
                    if item.type == "pizza":
                        pizza = await self.pizza_dao.get_by_id(
                            str(item.product_id)
                        )
                        if not pizza:
                            raise NotFoundError(
                                resource_type="pizza",
                                resource_id=str(item.product_id),
                            )
                        items.append(
                            OrderItemInputDTO(
                                type="pizza",
                                product_name=pizza.name,
                                quantity=item.quantity,
                            )
                        )
                    elif item.type == "beer":
                        beer = await self.beer_dao.get_by_id(
                            str(item.product_id)
                        )
                        if not beer:
                            raise NotFoundError(
                                resource_type="beer",
                                resource_id=str(item.product_id),
                            )
                        items.append(
                            OrderItemInputDTO(
                                type="beer",
                                product_name=beer.name,
                                quantity=item.quantity,
                            )
                        )

                notes = f"Cancelled: {reason}" if reason else order.notes

                update_dto = OrderUpdateInternalDTO(
                    service_type=order.service_type,
                    items=items,
                    notes=notes,
                    status=OrderStatus.CANCELLED,
                    customer_id=user.id,
                    subtotal=order.total,
                    total=order.total,
                    customer_email=user.email,
                    delivery_address=order.delivery_address,
                )

                cancelled_order = await self.order_dao.update(
                    str(order.id), update_dto
                )
                cancelled_orders.append(cancelled_order)

            return cancelled_orders

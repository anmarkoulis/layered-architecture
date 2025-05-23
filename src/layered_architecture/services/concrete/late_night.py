from datetime import datetime, time
from decimal import Decimal
from logging import getLogger
from uuid import UUID

from layered_architecture.dao.interfaces import (
    BeerDAOInterface,
    OrderDAOInterface,
    PizzaDAOInterface,
)
from layered_architecture.db.uow.base import BaseUnitOfWork
from layered_architecture.dto.order import (
    OrderCreateInternalDTO,
    OrderDTO,
    OrderInputDTO,
    OrderItemInputDTO,
    OrderUpdateDTO,
    OrderUpdateInternalDTO,
)
from layered_architecture.dto.user import UserReadDTO
from layered_architecture.enums import OrderStatus, ServiceType
from layered_architecture.exceptions import NotFoundError
from layered_architecture.services.interfaces.order import (
    OrderServiceInterface,
)

logger = getLogger(__name__)


class LateNightOrderService(OrderServiceInterface):
    """Service for handling late night orders with 20% surcharge."""

    LATE_NIGHT_SURCHARGE = Decimal(
        "0.20"
    )  # 20% surcharge for late night orders
    LATE_NIGHT_START = time(22, 0)  # 10 PM
    LATE_NIGHT_END = time(4, 0)  # 4 AM

    def __init__(
        self,
        pizza_dao: PizzaDAOInterface,
        beer_dao: BeerDAOInterface,
        order_dao: OrderDAOInterface,
        uow: BaseUnitOfWork,
    ):
        self.pizza_dao = pizza_dao
        self.beer_dao = beer_dao
        self.order_dao = order_dao
        self.uow = uow

    def _is_late_night(self) -> bool:
        """Check if the current time is within late night hours.

        :return: True if current time is between 10 PM and 4 AM
        :rtype: bool
        """
        current_time = datetime.now().time()
        return (
            self.LATE_NIGHT_START <= current_time
            or current_time < self.LATE_NIGHT_END
        )

    async def create_order(
        self,
        order_input: OrderInputDTO,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Create a new late night order.

        :param order_input: The order input data
        :type order_input: OrderInputDTO
        :param user: The user creating the order
        :type user: UserReadDTO
        :return: The created order
        :rtype: OrderDTO
        """
        if order_input.service_type != ServiceType.LATE_NIGHT:
            raise ValueError("Invalid service type for late night service")

        if not self._is_late_night():
            raise ValueError(
                "Late night orders are only available between 10 PM and 4 AM"
            )

        async with self.uow:
            # Calculate subtotal
            subtotal = Decimal("0")
            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_name(item.product_name)
                    if not pizza:
                        raise NotFoundError(
                            resource_type="pizza",
                            resource_id=item.product_name,
                        )
                    subtotal += pizza.price * item.quantity
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_name(item.product_name)
                    if not beer:
                        raise NotFoundError(
                            resource_type="beer",
                            resource_id=item.product_name,
                        )
                    subtotal += beer.price * item.quantity
                else:
                    raise ValueError(
                        f"Invalid item type: {item.type}. Only 'pizza' and 'beer' are supported"
                    )

            # Apply late night surcharge
            surcharge = subtotal * self.LATE_NIGHT_SURCHARGE
            total = subtotal + surcharge

            order_create_dto = OrderCreateInternalDTO(
                service_type=ServiceType.LATE_NIGHT,
                items=order_input.items,
                notes=order_input.notes,
                customer_id=user.id,
                subtotal=subtotal,
                total=total,
                customer_email=user.email,
                delivery_address=order_input.delivery_address,
            )

            created_order = await self.order_dao.create(order_create_dto)
            logger.info(
                f"Created late night order {created_order.id} for user {user.id} with {self.LATE_NIGHT_SURCHARGE*100}% surcharge"
            )
            return created_order

    async def check_status(
        self,
        order_id: UUID,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Check the status of a late night order.

        :param order_id: The ID of the order to check
        :type order_id: UUID
        :param user: The user checking the order
        :type user: UserReadDTO
        :return: The order with its current status
        :rtype: OrderDTO
        """
        async with self.uow:
            order = await self.order_dao.get_by_id(str(order_id))
            if not order:
                raise NotFoundError(
                    resource_type="order",
                    resource_id=str(order_id),
                )
            if order.customer_id != user.id:
                raise ValueError("Unauthorized to check this order")

            return order

    async def update_order(
        self,
        order_id: UUID,
        order_input: OrderUpdateDTO,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Update a late night order.

        :param order_id: The ID of the order to update
        :type order_id: UUID
        :param order_input: The updated order data
        :type order_input: OrderUpdateDTO
        :param user: The user updating the order
        :type user: UserReadDTO
        :return: The updated order
        :rtype: OrderDTO
        """
        if not self._is_late_night():
            raise ValueError(
                "Late night orders can only be updated between 10 PM and 4 AM"
            )

        async with self.uow:
            order = await self.order_dao.get_by_id(str(order_id))
            if not order:
                raise NotFoundError(
                    resource_type="order",
                    resource_id=str(order_id),
                )
            if order.customer_id != user.id:
                raise ValueError("Unauthorized to update this order")
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                raise ValueError(
                    f"Cannot update order in status {order.status}"
                )
            if order_input.service_type != ServiceType.LATE_NIGHT:
                raise ValueError(
                    "Cannot change service type to non-late-night"
                )

            # Calculate new subtotal
            subtotal = Decimal("0")
            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_name(item.product_name)
                    if not pizza:
                        raise NotFoundError(
                            resource_type="pizza",
                            resource_id=item.product_name,
                        )
                    subtotal += pizza.price * item.quantity
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_name(item.product_name)
                    if not beer:
                        raise NotFoundError(
                            resource_type="beer",
                            resource_id=item.product_name,
                        )
                    subtotal += beer.price * item.quantity
                else:
                    raise ValueError(
                        f"Invalid item type: {item.type}. Only 'pizza' and 'beer' are supported"
                    )

            # Add 20% surcharge for late night orders
            total = subtotal * Decimal("1.20")

            update_dto = OrderUpdateInternalDTO(
                service_type=ServiceType.LATE_NIGHT,
                items=order_input.items,
                notes=order_input.notes,
                status=order_input.status,
                customer_id=user.id,
                subtotal=subtotal,
                total=total,
                customer_email=user.email,
                delivery_address=order_input.delivery_address,
            )

            updated_order = await self.order_dao.update(
                str(order_id), update_dto
            )
            logger.info(
                f"Updated late night order {order_id} by user {user.id}"
            )
            return updated_order

    async def cancel_order(
        self,
        order_id: UUID,
        user: UserReadDTO,
        reason: str | None = None,
    ) -> OrderDTO:
        """Cancel a late night order.

        :param order_id: The ID of the order to cancel
        :type order_id: UUID
        :param user: The user cancelling the order
        :type user: UserReadDTO
        :param reason: Optional reason for cancellation
        :type reason: str | None
        :return: The cancelled order
        :rtype: OrderDTO
        """
        async with self.uow:
            order = await self.order_dao.get_by_id(str(order_id))
            if not order:
                raise NotFoundError(
                    resource_type="order",
                    resource_id=str(order_id),
                )
            if order.customer_id != user.id:
                raise ValueError("Unauthorized to cancel this order")
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                raise ValueError(
                    f"Cannot cancel order in status {order.status}"
                )

            notes = f"Cancelled: {reason}" if reason else order.notes

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
                    beer = await self.beer_dao.get_by_id(str(item.product_id))
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

            update_dto = OrderUpdateInternalDTO(
                service_type=ServiceType.LATE_NIGHT,
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
                str(order_id), update_dto
            )
            logger.info(
                f"Cancelled late night order {order_id} by user {user.id}"
            )
            return cancelled_order

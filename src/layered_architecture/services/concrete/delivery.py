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
    OrderUpdateDTO,
    OrderUpdateInternalDTO,
)
from layered_architecture.dto.user import UserReadDTO
from layered_architecture.enums import OrderStatus, ServiceType
from layered_architecture.services.interfaces.order import (
    OrderServiceInterface,
)

logger = getLogger(__name__)


class DeliveryOrderService(OrderServiceInterface):
    """Service for handling delivery orders with delivery fee."""

    DELIVERY_FEE = Decimal("5.00")  # $5 delivery fee

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

    async def create_order(
        self,
        order_input: OrderInputDTO,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Create a new delivery order.

        :param order_input: The order input data
        :type order_input: OrderInputDTO
        :param user: The user creating the order
        :type user: UserReadDTO
        :return: The created order
        :rtype: OrderDTO
        """
        if order_input.service_type != ServiceType.DELIVERY:
            raise ValueError("Invalid service type for delivery service")

        async with self.uow:
            # Calculate subtotal
            subtotal = Decimal("0")
            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_name(item.product_name)
                    if not pizza:
                        raise ValueError(
                            f"Pizza {item.product_name} not found"
                        )
                    subtotal += pizza.price * item.quantity
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_name(item.product_name)
                    if not beer:
                        raise ValueError(f"Beer {item.product_name} not found")
                    subtotal += beer.price * item.quantity
                else:
                    raise ValueError(
                        f"Invalid item type: {item.type}. Only 'pizza' and 'beer' are supported"
                    )

            # Add delivery fee
            total = subtotal + self.DELIVERY_FEE

            order_create_dto = OrderCreateInternalDTO(
                service_type=ServiceType.DELIVERY,
                items=order_input.items,
                notes=order_input.notes,
                customer_id=user.id,
                subtotal=subtotal,
                total=total,
                customer_email=user.email,
            )

            created_order = await self.order_dao.create(order_create_dto)
            logger.info(
                f"Created delivery order {created_order.id} for user {user.id} with ${self.DELIVERY_FEE} delivery fee"
            )
            return created_order

    async def check_status(
        self,
        order_id: UUID,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Check the status of a delivery order.

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
                raise ValueError(f"Order {order_id} not found")
            if order.customer_id != user.id:
                raise ValueError("Unauthorized to check this order")

            return order

    async def update_order(
        self,
        order_id: UUID,
        order_input: OrderUpdateDTO,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Update a delivery order.

        :param order_id: The ID of the order to update
        :type order_id: UUID
        :param order_input: The updated order data
        :type order_input: OrderUpdateDTO
        :param user: The user updating the order
        :type user: UserReadDTO
        :return: The updated order
        :rtype: OrderDTO
        """
        async with self.uow:
            order = await self.order_dao.get_by_id(str(order_id))
            if not order:
                raise ValueError(f"Order {order_id} not found")
            if order.customer_id != user.id:
                raise ValueError("Unauthorized to update this order")
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                raise ValueError(
                    f"Cannot update order in status {order.status}"
                )
            if order_input.service_type != ServiceType.DELIVERY:
                raise ValueError("Cannot change service type to non-delivery")

            # Calculate new subtotal
            subtotal = Decimal("0")
            for item in order_input.items:
                if item.type == "pizza":
                    pizza = await self.pizza_dao.get_by_name(item.product_name)
                    if not pizza:
                        raise ValueError(
                            f"Pizza {item.product_name} not found"
                        )
                    subtotal += pizza.price * item.quantity
                elif item.type == "beer":
                    beer = await self.beer_dao.get_by_name(item.product_name)
                    if not beer:
                        raise ValueError(f"Beer {item.product_name} not found")
                    subtotal += beer.price * item.quantity
                else:
                    raise ValueError(
                        f"Invalid item type: {item.type}. Only 'pizza' and 'beer' are supported"
                    )

            # Add delivery fee
            total = subtotal + self.DELIVERY_FEE

            update_dto = OrderUpdateInternalDTO(
                service_type=ServiceType.DELIVERY,
                items=order_input.items,
                notes=order_input.notes,
                status=order_input.status,
                customer_id=user.id,
                subtotal=subtotal,
                total=total,
                customer_email=user.email,
            )

            updated_order = await self.order_dao.update(
                str(order_id), update_dto
            )
            logger.info(f"Updated delivery order {order_id} by user {user.id}")
            return updated_order

    async def cancel_order(
        self,
        order_id: UUID,
        user: UserReadDTO,
        reason: str | None = None,
    ) -> OrderDTO:
        """Cancel a delivery order.

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
                raise ValueError(f"Order {order_id} not found")
            if order.customer_id != user.id:
                raise ValueError("Unauthorized to cancel this order")
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                raise ValueError(
                    f"Cannot cancel order in status {order.status}"
                )

            notes = f"Cancelled: {reason}" if reason else order.notes

            update_dto = OrderUpdateInternalDTO(
                service_type=ServiceType.DELIVERY,
                items=order.items,
                notes=notes,
                status=OrderStatus.CANCELLED,
                customer_id=user.id,
                subtotal=order.total,
                total=order.total,
                customer_email=user.email,
            )

            cancelled_order = await self.order_dao.update(
                str(order_id), update_dto
            )
            logger.info(
                f"Cancelled delivery order {order_id} by user {user.id}"
            )
            return cancelled_order

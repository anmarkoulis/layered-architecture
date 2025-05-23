from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.dto.user import UserReadDTO


class OrderServiceInterface(ABC):  # pragma: no cover
    """Interface for order services."""

    @abstractmethod
    async def create_order(
        self,
        order_input: OrderInputDTO,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Create a new order.

        :param order_input: The order input data
        :type order_input: OrderInputDTO
        :param user: The user creating the order
        :type user: UserReadDTO
        :return: The created order
        :rtype: OrderDTO
        """
        pass

    @abstractmethod
    async def check_status(
        self,
        order_id: UUID,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Check the status of an order.

        :param order_id: The ID of the order to check
        :type order_id: UUID
        :param user: The user checking the order
        :type user: UserReadDTO
        :return: The order with its current status
        :rtype: OrderDTO
        """
        pass

    @abstractmethod
    async def update_order(
        self,
        order_id: UUID,
        order_input: OrderInputDTO,
        user: UserReadDTO,
    ) -> OrderDTO:
        """Update an existing order.

        :param order_id: The ID of the order to update
        :type order_id: UUID
        :param order_input: The updated order data
        :type order_input: OrderInputDTO
        :param user: The user updating the order
        :type user: UserReadDTO
        :return: The updated order
        :rtype: OrderDTO
        """
        pass

    @abstractmethod
    async def cancel_order(
        self,
        order_id: UUID,
        user: UserReadDTO,
        reason: Optional[str] = None,
    ) -> OrderDTO:
        """Cancel an order.

        :param order_id: The ID of the order to cancel
        :type order_id: UUID
        :param user: The user cancelling the order
        :type user: UserReadDTO
        :param reason: Optional reason for cancellation
        :type reason: Optional[str]
        :return: The cancelled order
        :rtype: OrderDTO
        """
        pass

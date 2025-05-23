from abc import ABC, abstractmethod
from typing import List, Optional

from layered_architecture.dto.order import (
    OrderCreateInternalDTO,
    OrderDTO,
    OrderUpdateInternalDTO,
)


class OrderDAOInterface(ABC):
    """Interface for order data access."""

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[OrderDTO]:
        """Get an order by its ID.

        :param order_id: The ID of the order to retrieve
        :type order_id: str
        :return: The order if found, None otherwise
        :rtype: Optional[OrderDTO]
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[OrderDTO]:
        """Get all orders.

        :return: List of all orders
        :rtype: List[OrderDTO]
        """
        pass

    @abstractmethod
    async def create(self, order_input: OrderCreateInternalDTO) -> OrderDTO:
        """Create a new order.

        :param order_input: The order input data with customer details
        :type order_input: OrderCreateInternalDTO
        :return: The created order
        :rtype: OrderDTO
        """
        pass

    @abstractmethod
    async def update(
        self, order_id: str, update_data: OrderUpdateInternalDTO
    ) -> OrderDTO:
        """Update an existing order.

        :param order_id: The ID of the order to update
        :type order_id: str
        :param update_data: The data to update the order with
        :type update_data: OrderUpdateInternalDTO
        :return: The updated order
        :rtype: OrderDTO
        """
        pass

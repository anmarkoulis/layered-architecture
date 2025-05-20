from abc import ABC, abstractmethod

from layered_architecture.dto.order import OrderDTO, OrderInputDTO


class OrderService(ABC):
    @abstractmethod
    async def create_order(self, order_input: OrderInputDTO) -> OrderDTO:
        """Create a new order.

        Args:
            order_input: The order input data including store_type

        Returns:
            The created order
        """
        pass

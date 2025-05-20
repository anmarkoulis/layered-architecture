from abc import ABC, abstractmethod
from typing import List, Optional

from layered_architecture.dto.order import OrderDTO, OrderInputDTO


class OrderDAO(ABC):
    @abstractmethod
    async def create(self, order_input: OrderInputDTO) -> OrderDTO:
        """Create a new order.

        Args:
            order_input: The order input data including store_type

        Returns:
            The created order
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[OrderDTO]:
        pass

    @abstractmethod
    async def get_all(self) -> List[OrderDTO]:
        pass

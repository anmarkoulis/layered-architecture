from abc import ABC, abstractmethod
from typing import List, Optional

from layered_architecture.dto.order import OrderItemDTO


class BeerDAO(ABC):
    @abstractmethod
    async def get_by_id(self, beer_id: str) -> Optional[OrderItemDTO]:
        pass

    @abstractmethod
    async def get_all(self) -> List[OrderItemDTO]:
        pass

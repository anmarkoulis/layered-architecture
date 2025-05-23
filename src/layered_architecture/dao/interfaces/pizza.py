from abc import ABC, abstractmethod
from typing import List, Optional

from layered_architecture.dto.pizza import PizzaDTO


class PizzaDAOInterface(ABC):  # pragma: no cover
    """Interface for pizza data access."""

    @abstractmethod
    async def get_by_id(self, pizza_id: str) -> Optional[PizzaDTO]:
        """Get a pizza by its ID.

        :param pizza_id: The ID of the pizza to retrieve
        :type pizza_id: str
        :return: The pizza if found, None otherwise
        :rtype: Optional[PizzaDTO]
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[PizzaDTO]:
        """Get a pizza by its name.

        :param name: The name of the pizza to retrieve
        :type name: str
        :return: The pizza if found, None otherwise
        :rtype: Optional[PizzaDTO]
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[PizzaDTO]:
        """Get all pizzas.

        :return: List of all pizzas
        :rtype: List[PizzaDTO]
        """
        pass

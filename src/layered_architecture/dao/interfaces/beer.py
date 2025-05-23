from abc import ABC, abstractmethod
from typing import List, Optional

from layered_architecture.dto.beer import BeerDTO


class BeerDAOInterface(ABC):  # pragma: no cover
    """Interface for beer data access."""

    @abstractmethod
    async def get_by_id(self, beer_id: str) -> Optional[BeerDTO]:
        """Get a beer by its ID.

        :param beer_id: The ID of the beer to retrieve
        :type beer_id: str
        :return: The beer if found, None otherwise
        :rtype: Optional[BeerDTO]
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[BeerDTO]:
        """Get a beer by its name.

        :param name: The name of the beer to retrieve
        :type name: str
        :return: The beer if found, None otherwise
        :rtype: Optional[BeerDTO]
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[BeerDTO]:
        """Get all beers.

        :return: List of all beers
        :rtype: List[BeerDTO]
        """
        pass

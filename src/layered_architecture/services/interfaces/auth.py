from abc import ABC, abstractmethod

from layered_architecture.dto.user import UserReadDTO


class AuthServiceInterface(ABC):  # pragma: no cover
    """Interface for authentication services."""

    @staticmethod
    @abstractmethod
    async def get_current_user() -> UserReadDTO:
        """Get the current authenticated user.

        :return: The current user's data
        :rtype: UserReadDTO
        """
        pass

    @staticmethod
    @abstractmethod
    async def get_system_user() -> UserReadDTO:
        """Get the system user for automated operations.

        :return: The system user's data
        :rtype: UserReadDTO
        """
        pass

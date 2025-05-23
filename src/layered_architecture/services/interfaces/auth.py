from abc import ABC, abstractmethod

from layered_architecture.dto.user import UserReadDTO


class AuthServiceInterface(ABC):
    """Interface for authentication services."""

    @staticmethod
    @abstractmethod
    async def get_current_user() -> UserReadDTO:
        """Get the current authenticated user.

        :return: The current user's data
        :rtype: UserReadDTO
        """
        pass

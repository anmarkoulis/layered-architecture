from layered_architecture.dto.user import UserReadDTO
from layered_architecture.services.interfaces.auth import AuthServiceInterface


class FakeAuthService(AuthServiceInterface):
    """A fake authentication service that always returns the same user."""

    @staticmethod
    async def get_current_user() -> UserReadDTO:
        """Get the current user (always returns the test user).

        :return: The test user's data
        :rtype: UserReadDTO
        """
        return UserReadDTO(
            id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            address="123 Test Street, Test City",
        )

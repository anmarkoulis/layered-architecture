from logging import getLogger

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.db.depends import get_db
from layered_architecture.db.models.order import ServiceType
from layered_architecture.factories.order import OrderServiceFactory
from layered_architecture.services.concrete.fake_auth import FakeAuthService
from layered_architecture.services.interfaces.auth import AuthServiceInterface
from layered_architecture.services.interfaces.order import (
    OrderServiceInterface,
)

logger = getLogger(__name__)


class DependencyService:
    """Service for managing dependencies and service creation."""

    @staticmethod
    async def get_order_service(
        service_type: ServiceType,
        db: AsyncSession = Depends(get_db),
    ) -> OrderServiceInterface:
        """Get an order service for the specified service type.

        :param service_type: The type of service to get
        :type service_type: ServiceType
        :param db: The database session to use
        :type db: AsyncSession
        :return: An order service instance
        :rtype: OrderServiceInterface
        """
        factory = OrderServiceFactory(db)
        return factory.get_service_by_service_type(service_type)

    @staticmethod
    async def get_order_service_by_id(
        order_id: str,
        db: AsyncSession = Depends(get_db),
    ) -> OrderServiceInterface:
        """Get an order service based on the order ID.

        :param order_id: The ID of the order to get the service for
        :type order_id: str
        :param db: The database session to use
        :type db: AsyncSession
        :return: An order service instance
        :rtype: OrderServiceInterface
        :raises ValueError: If the order is not found
        """
        factory = OrderServiceFactory(db)
        return await factory.get_service_by_order_id(order_id)

    @staticmethod
    async def get_auth_service() -> AuthServiceInterface:
        """Get the authentication service.

        :return: An authentication service instance
        :rtype: AuthServiceInterface
        """
        return FakeAuthService()

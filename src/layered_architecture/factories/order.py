from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.concrete.sqla_beer import SQLBeerDAO
from layered_architecture.dao.concrete.sqla_order import SQLOrderDAO
from layered_architecture.dao.concrete.sqla_pizza import SQLPizzaDAO
from layered_architecture.db.models.order import ServiceType
from layered_architecture.db.uow import SQLAUnitOfWork
from layered_architecture.services import (
    DeliveryOrderService,
    DineInOrderService,
    LateNightOrderService,
    OrderServiceInterface,
    TakeawayOrderService,
)

logger = getLogger(__name__)


class OrderServiceFactory:
    """Factory for creating order services based on service type.

    This factory is responsible for creating the appropriate order service
    based on the service type. It handles all the necessary dependencies
    and service instantiation.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the factory with database session.

        :param db: The database session to use
        :type db: AsyncSession
        """
        self.db = db
        self.uow = SQLAUnitOfWork(db)
        self.pizza_dao = SQLPizzaDAO(db)
        self.beer_dao = SQLBeerDAO(db)
        self.order_dao = SQLOrderDAO(db)

    async def get_service_by_order_id(
        self, order_id: str
    ) -> OrderServiceInterface:
        """Get the appropriate service for an order.

        :param order_id: The ID of the order
        :type order_id: str
        :return: The appropriate order service
        :rtype: OrderServiceInterface
        :raises ValueError: If order not found
        """
        order = await self.order_dao.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order not found: {order_id}")

        return self.get_service_by_service_type(order.service_type)

    def get_service_by_service_type(
        self, service_type: ServiceType
    ) -> OrderServiceInterface:
        """Get the appropriate service based on service type.

        :param service_type: The type of service
        :type service_type: ServiceType
        :return: The appropriate order service
        :rtype: OrderServiceInterface
        :raises ValueError: If service type is not supported
        """
        match service_type:
            case ServiceType.DINE_IN:
                return DineInOrderService(
                    self.pizza_dao, self.beer_dao, self.order_dao, self.uow
                )
            case ServiceType.TAKEAWAY:
                return TakeawayOrderService(
                    self.pizza_dao, self.beer_dao, self.order_dao, self.uow
                )
            case ServiceType.DELIVERY:
                return DeliveryOrderService(
                    self.pizza_dao, self.beer_dao, self.order_dao, self.uow
                )
            case ServiceType.LATE_NIGHT:
                return LateNightOrderService(
                    self.pizza_dao, self.beer_dao, self.order_dao, self.uow
                )
            case _:
                raise ValueError(f"Unsupported service type: {service_type}")

from logging import getLogger

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.concrete.sqla_beer import SQLBeerDAO
from layered_architecture.dao.concrete.sqla_order import SQLOrderDAO
from layered_architecture.dao.concrete.sqla_pizza import SQLPizzaDAO
from layered_architecture.db.depends import get_db
from layered_architecture.db.uow import SQLAUnitOfWork
from layered_architecture.enums import StoreType
from layered_architecture.services.concrete.corporate import (
    CorporateOrderService,
)
from layered_architecture.services.concrete.delivery import (
    DeliveryOrderService,
)
from layered_architecture.services.concrete.downtown import (
    DowntownOrderService,
)
from layered_architecture.services.concrete.late_night import (
    LateNightOrderService,
)
from layered_architecture.services.concrete.mall import MallOrderService
from layered_architecture.services.interfaces.order import OrderService

logger = getLogger(__name__)


class DependencyService:
    @staticmethod
    def get_order_service(
        store_type: StoreType,
        db: AsyncSession = Depends(get_db),
    ) -> OrderService:
        """Get an order service for the specified store.

        Args:
            store_type: The type of the store to get the service for
            db: The database session to use

        Returns:
            An order service instance

        Raises:
            ValueError: If the store type is not supported
        """
        uow = SQLAUnitOfWork(db)
        pizza_dao = SQLPizzaDAO(db)
        beer_dao = SQLBeerDAO(db)
        order_dao = SQLOrderDAO(db)
        logger.info(f"store_type: {store_type}")
        logger.info(f"type(store_type): {type(store_type)}")

        if store_type == StoreType.DOWNTOWN:
            return DowntownOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_type == StoreType.MALL:
            return MallOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_type == StoreType.LATE_NIGHT:
            return LateNightOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_type == StoreType.CORPORATE:
            return CorporateOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_type == StoreType.DELIVERY:
            return DeliveryOrderService(pizza_dao, beer_dao, order_dao, uow)
        else:
            raise ValueError(f"Unsupported store type: {store_type}")

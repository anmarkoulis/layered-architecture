from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.concrete.sqla_beer import SQLBeerDAO
from layered_architecture.dao.concrete.sqla_order import SQLOrderDAO
from layered_architecture.dao.concrete.sqla_pizza import SQLPizzaDAO
from layered_architecture.db.depends import get_db
from layered_architecture.db.uow import SQLAUnitOfWork
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


class DependencyService:
    @staticmethod
    def get_order_service(
        store_id: str,
        db: AsyncSession = Depends(get_db),
    ) -> OrderService:
        """Get an order service for the specified store.

        Args:
            store_id: The ID of the store to get the service for
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
        print(f"store_id: {store_id}")
        print(f"type(store_id): {type(store_id)}")

        if store_id == "downtown":
            return DowntownOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_id == "mall":
            return MallOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_id == "late_night":
            return LateNightOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_id == "corporate":
            return CorporateOrderService(pizza_dao, beer_dao, order_dao, uow)
        elif store_id == "delivery":
            return DeliveryOrderService(pizza_dao, beer_dao, order_dao, uow)
        else:
            raise ValueError(f"Unsupported store type: {store_id}")

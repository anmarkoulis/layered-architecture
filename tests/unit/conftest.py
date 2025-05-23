from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from layered_architecture.dao.interfaces import (
    BeerDAOInterface,
    OrderDAOInterface,
    PizzaDAOInterface,
)
from layered_architecture.db.uow.base import BaseUnitOfWork
from layered_architecture.dto.user import UserReadDTO
from layered_architecture.services.concrete.delivery import (
    DeliveryOrderService,
)
from layered_architecture.services.concrete.dine_in import DineInOrderService
from layered_architecture.services.concrete.late_night import (
    LateNightOrderService,
)
from layered_architecture.services.concrete.takeaway import (
    TakeawayOrderService,
)


@pytest.fixture
def mock_pizza_dao() -> AsyncMock:
    return AsyncMock(spec=PizzaDAOInterface)


@pytest.fixture
def mock_beer_dao() -> AsyncMock:
    return AsyncMock(spec=BeerDAOInterface)


@pytest.fixture
def mock_order_dao() -> AsyncMock:
    return AsyncMock(spec=OrderDAOInterface)


@pytest.fixture
def mock_uow() -> AsyncMock:
    return AsyncMock(spec=BaseUnitOfWork)


@pytest.fixture
def delivery_service(
    mock_pizza_dao: AsyncMock,
    mock_beer_dao: AsyncMock,
    mock_order_dao: AsyncMock,
    mock_uow: AsyncMock,
) -> DeliveryOrderService:
    return DeliveryOrderService(
        pizza_dao=mock_pizza_dao,
        beer_dao=mock_beer_dao,
        order_dao=mock_order_dao,
        uow=mock_uow,
    )


@pytest.fixture
def dine_in_service(
    mock_pizza_dao: AsyncMock,
    mock_beer_dao: AsyncMock,
    mock_order_dao: AsyncMock,
    mock_uow: AsyncMock,
) -> DineInOrderService:
    return DineInOrderService(
        pizza_dao=mock_pizza_dao,
        beer_dao=mock_beer_dao,
        order_dao=mock_order_dao,
        uow=mock_uow,
    )


@pytest.fixture
def late_night_service(
    mock_pizza_dao: AsyncMock,
    mock_beer_dao: AsyncMock,
    mock_order_dao: AsyncMock,
    mock_uow: AsyncMock,
) -> LateNightOrderService:
    return LateNightOrderService(
        pizza_dao=mock_pizza_dao,
        beer_dao=mock_beer_dao,
        order_dao=mock_order_dao,
        uow=mock_uow,
    )


@pytest.fixture
def takeaway_service(
    mock_pizza_dao: AsyncMock,
    mock_beer_dao: AsyncMock,
    mock_order_dao: AsyncMock,
    mock_uow: AsyncMock,
) -> TakeawayOrderService:
    return TakeawayOrderService(
        pizza_dao=mock_pizza_dao,
        beer_dao=mock_beer_dao,
        order_dao=mock_order_dao,
        uow=mock_uow,
    )


@pytest.fixture
def user() -> UserReadDTO:
    return UserReadDTO(
        id=uuid4(),
        username="testuser",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        address="123 Test Street, Test City",
    )

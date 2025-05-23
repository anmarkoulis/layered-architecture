from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from layered_architecture.dto.order import (
    OrderDTO,
    OrderInputDTO,
    OrderItemDTO,
    OrderItemInputDTO,
    OrderUpdateDTO,
)
from layered_architecture.dto.user import UserReadDTO
from layered_architecture.enums import OrderStatus, ServiceType
from layered_architecture.exceptions import NotFoundError
from layered_architecture.services.concrete.dine_in import DineInOrderService


class TestDineInService:
    @pytest.mark.asyncio
    async def test_create_order_success(
        self,
        dine_in_service: DineInOrderService,
        mock_pizza_dao: AsyncMock,
        mock_beer_dao: AsyncMock,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_input = OrderInputDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=2,
                ),
                OrderItemInputDTO(
                    type="beer",
                    product_name="Heineken",
                    quantity=1,
                ),
            ],
            notes="Extra cheese please",
        )

        mock_pizza_dao.get_by_name.return_value = Mock(
            price=Decimal("12.99"),
            id=uuid4(),
        )
        mock_beer_dao.get_by_name.return_value = Mock(
            price=Decimal("5.99"),
            id=uuid4(),
        )

        now = datetime.now()
        expected_order = OrderDTO(
            id=uuid4(),
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[
                OrderItemDTO(
                    product_id=str(uuid4()),
                    quantity=2,
                    price=Decimal("12.99"),
                    type="pizza",
                ),
                OrderItemDTO(
                    product_id=str(uuid4()),
                    quantity=1,
                    price=Decimal("5.99"),
                    type="beer",
                ),
            ],
            total=Decimal("31.97"),  # (2 * 12.99) + 5.99
            customer_email=user.email,
            notes="Extra cheese please",
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.create.return_value = expected_order

        # When
        result = await dine_in_service.create_order(order_input, user)

        # Then
        assert result == expected_order
        mock_pizza_dao.get_by_name.assert_called_once_with("Margherita")
        mock_beer_dao.get_by_name.assert_called_once_with("Heineken")
        mock_order_dao.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_order_invalid_service_type(
        self,
        dine_in_service: DineInOrderService,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_input = OrderInputDTO(
            service_type=ServiceType.DELIVERY,  # Invalid for dine-in service
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=1,
                ),
            ],
        )

        # When/Then
        with pytest.raises(
            ValueError, match="Invalid service type for dine-in service"
        ):
            await dine_in_service.create_order(order_input, user)

    @pytest.mark.asyncio
    async def test_create_order_pizza_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_pizza_dao: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_input = OrderInputDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="NonexistentPizza",
                    quantity=1,
                ),
            ],
        )

        mock_pizza_dao.get_by_name.return_value = None

        # When/Then
        with pytest.raises(
            NotFoundError, match="Pizza NonexistentPizza not found"
        ):
            await dine_in_service.create_order(order_input, user)

    @pytest.mark.asyncio
    async def test_create_order_beer_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_pizza_dao: AsyncMock,
        mock_beer_dao: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_input = OrderInputDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=1,
                ),
                OrderItemInputDTO(
                    type="beer",
                    product_name="NonexistentBeer",
                    quantity=1,
                ),
            ],
        )

        mock_pizza_dao.get_by_name.return_value = Mock(
            price=Decimal("12.99"),
            id=uuid4(),
        )
        mock_beer_dao.get_by_name.return_value = None

        # When/Then
        with pytest.raises(
            NotFoundError, match="Beer NonexistentBeer not found"
        ):
            await dine_in_service.create_order(order_input, user)

    @pytest.mark.asyncio
    async def test_check_status_success(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        expected_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = expected_order

        # When
        result = await dine_in_service.check_status(order_id, user)

        # Then
        assert result == expected_order
        mock_order_dao.get_by_id.assert_called_once_with(str(order_id))
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_status_order_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        mock_order_dao.get_by_id.return_value = None

        # When/Then
        with pytest.raises(NotFoundError, match=f"Order {order_id} not found"):
            await dine_in_service.check_status(order_id, user)

    @pytest.mark.asyncio
    async def test_check_status_unauthorized(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        other_user_id = uuid4()
        now = datetime.now()
        expected_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=other_user_id,  # Different from user.id
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email="other@example.com",
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = expected_order

        # When/Then
        with pytest.raises(
            ValueError,
            match=f"Unauthorized to check this order. User {user.id} is not the customer of order {other_user_id}",
        ):
            await dine_in_service.check_status(order_id, user)

    @pytest.mark.asyncio
    async def test_update_order_success(
        self,
        dine_in_service: DineInOrderService,
        mock_pizza_dao: AsyncMock,
        mock_beer_dao: AsyncMock,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        mock_pizza_dao.get_by_name.return_value = Mock(
            price=Decimal("12.99"),
            id=uuid4(),
        )

        expected_updated_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.CONFIRMED,
            items=[
                OrderItemDTO(
                    product_id=str(uuid4()),
                    quantity=2,
                    price=Decimal("12.99"),
                    type="pizza",
                ),
            ],
            total=Decimal("25.98"),  # 2 * 12.99
            customer_email=user.email,
            notes="Updated order",
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.update.return_value = expected_updated_order

        # When
        result = await dine_in_service.update_order(
            order_id, update_input, user
        )

        # Then
        assert result == expected_updated_order
        mock_order_dao.get_by_id.assert_called_once_with(str(order_id))
        mock_pizza_dao.get_by_name.assert_called_once_with("Margherita")
        mock_order_dao.update.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        mock_order_dao.get_by_id.return_value = None

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        # When/Then
        with pytest.raises(NotFoundError, match=f"Order {order_id} not found"):
            await dine_in_service.update_order(order_id, update_input, user)

    @pytest.mark.asyncio
    async def test_update_order_unauthorized(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        other_user_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=other_user_id,  # Different from user.id
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email="other@example.com",
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        # When/Then
        with pytest.raises(
            ValueError, match="Unauthorized to update this order"
        ):
            await dine_in_service.update_order(order_id, update_input, user)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status", [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
    )
    async def test_update_order_invalid_status(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
        status: OrderStatus,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=status,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        # When/Then
        with pytest.raises(
            ValueError, match=f"Cannot update order in status {status}"
        ):
            await dine_in_service.update_order(order_id, update_input, user)

    @pytest.mark.asyncio
    async def test_update_order_invalid_service_type(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DELIVERY,  # Invalid for dine-in service
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="Margherita",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        # When/Then
        with pytest.raises(
            ValueError, match="Cannot change service type to non-dine-in"
        ):
            await dine_in_service.update_order(order_id, update_input, user)

    @pytest.mark.asyncio
    async def test_update_order_pizza_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_pizza_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="pizza",
                    product_name="NonexistentPizza",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        mock_pizza_dao.get_by_name.return_value = None

        # When/Then
        with pytest.raises(
            NotFoundError, match="Pizza NonexistentPizza not found"
        ):
            await dine_in_service.update_order(order_id, update_input, user)

    @pytest.mark.asyncio
    async def test_update_order_beer_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_beer_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        update_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="beer",
                    product_name="NonexistentBeer",
                    quantity=2,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.CONFIRMED,
        )

        mock_beer_dao.get_by_name.return_value = None

        # When/Then
        with pytest.raises(
            NotFoundError, match="Beer NonexistentBeer not found"
        ):
            await dine_in_service.update_order(order_id, update_input, user)

    @pytest.mark.asyncio
    async def test_cancel_order_success(
        self,
        dine_in_service: DineInOrderService,
        mock_pizza_dao: AsyncMock,
        mock_beer_dao: AsyncMock,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[
                OrderItemDTO(
                    product_id=str(uuid4()),
                    quantity=1,
                    price=Decimal("12.99"),
                    type="pizza",
                ),
            ],
            total=Decimal("12.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        # Ensure the mock pizza has a valid name attribute
        pizza_mock = Mock()
        pizza_mock.name = "Margherita"
        pizza_mock.id = uuid4()
        mock_pizza_dao.get_by_id.return_value = pizza_mock

        expected_cancelled_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.CANCELLED,
            items=[
                OrderItemDTO(
                    product_id=str(uuid4()),
                    quantity=1,
                    price=Decimal("12.99"),
                    type="pizza",
                ),
            ],
            total=Decimal("12.99"),
            customer_email=user.email,
            notes="Cancelled: Customer request",
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.update.return_value = expected_cancelled_order

        # When
        result = await dine_in_service.cancel_order(
            order_id, user, reason="Customer request"
        )

        # Then
        assert result == expected_cancelled_order
        mock_order_dao.get_by_id.assert_called_once_with(str(order_id))
        mock_pizza_dao.get_by_id.assert_called_once()
        mock_order_dao.update.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_order_unauthorized(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        other_user_id = uuid4()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=other_user_id,  # Not the same as user.id
            status=OrderStatus.PENDING,
            items=[],
            total=Decimal("17.99"),
            customer_email="other@example.com",
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        # When/Then
        with pytest.raises(
            ValueError, match="Unauthorized to cancel this order"
        ):
            await dine_in_service.cancel_order(order_id, user)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status", [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
    )
    async def test_cancel_order_invalid_status(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        user: UserReadDTO,
        status: OrderStatus,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=status,
            items=[],
            total=Decimal("17.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order

        # When/Then
        with pytest.raises(
            ValueError, match=f"Cannot cancel order in status {status}"
        ):
            await dine_in_service.cancel_order(order_id, user)

    @pytest.mark.asyncio
    async def test_cancel_order_pizza_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_pizza_dao: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        pizza_id = uuid4()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[
                OrderItemDTO(
                    product_id=str(pizza_id),
                    quantity=1,
                    price=Decimal("12.99"),
                    type="pizza",
                ),
            ],
            total=Decimal("12.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order
        mock_pizza_dao.get_by_id.return_value = None

        # When/Then
        with pytest.raises(NotFoundError, match=f"Pizza {pizza_id} not found"):
            await dine_in_service.cancel_order(order_id, user)

    @pytest.mark.asyncio
    async def test_cancel_order_beer_not_found(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_beer_dao: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        now = datetime.now()
        beer_id = uuid4()
        existing_order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[
                OrderItemDTO(
                    product_id=str(beer_id),
                    quantity=1,
                    price=Decimal("5.99"),
                    type="beer",
                ),
            ],
            total=Decimal("5.99"),
            customer_email=user.email,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        mock_order_dao.get_by_id.return_value = existing_order
        mock_beer_dao.get_by_id.return_value = None

        # When/Then
        with pytest.raises(NotFoundError, match=f"Beer {beer_id} not found"):
            await dine_in_service.cancel_order(order_id, user)

    @pytest.mark.asyncio
    async def test_create_order_invalid_item_type(
        self,
        dine_in_service: DineInOrderService,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_input = OrderInputDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="invalid_type",  # Invalid item type
                    product_name="Margherita",
                    quantity=1,
                ),
            ],
        )

        # When/Then
        with pytest.raises(
            ValueError,
            match="Invalid item type: invalid_type. Only 'pizza' and 'beer' are supported",
        ):
            await dine_in_service.create_order(order_input, user)

    @pytest.mark.asyncio
    async def test_update_order_invalid_item_type(
        self,
        dine_in_service: DineInOrderService,
        mock_order_dao: AsyncMock,
        mock_uow: AsyncMock,
        user: UserReadDTO,
    ) -> None:
        # Given
        order_id = uuid4()
        order = OrderDTO(
            id=order_id,
            service_type=ServiceType.DINE_IN,
            customer_id=user.id,
            status=OrderStatus.PENDING,
            items=[
                OrderItemDTO(
                    product_id=str(uuid4()),
                    quantity=1,
                    price=Decimal("12.99"),
                    type="pizza",
                ),
            ],
            total=Decimal("12.99"),
            customer_email=user.email,
            notes="Test order",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_order_dao.get_by_id.return_value = order

        order_input = OrderUpdateDTO(
            service_type=ServiceType.DINE_IN,
            items=[
                OrderItemInputDTO(
                    type="invalid_type",  # Invalid item type
                    product_name="Margherita",
                    quantity=1,
                ),
            ],
            notes="Updated order",
            status=OrderStatus.PREPARING,
        )

        # When/Then
        with pytest.raises(
            ValueError,
            match="Invalid item type: invalid_type. Only 'pizza' and 'beer' are supported",
        ):
            await dine_in_service.update_order(order_id, order_input, user)

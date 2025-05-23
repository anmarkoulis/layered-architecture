from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.concrete import SQLOrderDAO
from layered_architecture.dto.order import (
    OrderCreateInternalDTO,
    OrderDTO,
    OrderItemInputDTO,
    OrderStatus,
    OrderUpdateInternalDTO,
    ServiceType,
)


class TestSQLOrderDAO:
    @pytest.mark.asyncio
    async def test_create(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
            OrderItemInputDTO(
                type="beer",
                product_name="Heineken",
                quantity=2,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("22.97"),  # 12.99 + (2 * 5.99)
            total=Decimal("22.97"),
            customer_email="john.doe@example.com",
            notes="Extra cheese please",
        )

        # When
        created_order = await dao.create(order_input)

        # Then
        assert created_order is not None
        assert isinstance(created_order, OrderDTO)
        assert created_order.service_type == ServiceType.DINE_IN
        assert created_order.customer_id == customer_id
        assert created_order.status == OrderStatus.PENDING
        assert len(created_order.items) == 2
        assert created_order.total == Decimal("22.97")
        assert created_order.customer_email == "john.doe@example.com"
        assert created_order.notes == "Extra cheese please"
        assert created_order.created_at is not None
        assert created_order.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_with_nonexistent_pizza(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="NonexistentPizza",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="test@example.com",
        )

        # When/Then
        with pytest.raises(
            ValueError, match="Pizza NonexistentPizza not found"
        ):
            await dao.create(order_input)

    @pytest.mark.asyncio
    async def test_create_with_nonexistent_beer(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="beer",
                product_name="NonexistentBeer",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("5.99"),
            total=Decimal("5.99"),
            customer_email="test@example.com",
        )

        # When/Then
        with pytest.raises(ValueError, match="Beer NonexistentBeer not found"):
            await dao.create(order_input)

    @pytest.mark.asyncio
    async def test_get_by_id(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="jane.doe@example.com",
        )
        created_order = await dao.create(order_input)

        # When
        def get_customer_email(customer_id: str) -> str:
            return "jane.doe@example.com"

        retrieved_order = await dao.get_by_id(
            created_order.id, get_customer_email
        )

        # Then
        assert retrieved_order is not None
        assert isinstance(retrieved_order, OrderDTO)
        assert retrieved_order.id == created_order.id
        assert retrieved_order.service_type == ServiceType.DINE_IN
        assert retrieved_order.customer_id == customer_id
        assert retrieved_order.status == OrderStatus.PENDING
        assert len(retrieved_order.items) == 1
        assert retrieved_order.total == Decimal("12.99")
        assert retrieved_order.customer_email == "jane.doe@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        nonexistent_id = str(uuid4())

        # When
        def get_customer_email(customer_id: str) -> str:
            return "test@example.com"

        result = await dao.get_by_id(nonexistent_id, get_customer_email)

        # Then
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
        ]

        order1_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="alice@example.com",
        )
        order2_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="bob@example.com",
        )
        await dao.create(order1_input)
        await dao.create(order2_input)

        # When
        orders = await dao.get_all()

        # Then
        assert len(orders) >= 2
        assert all(isinstance(order, OrderDTO) for order in orders)
        # Since customer_email is None in get_all, we can't check for specific emails
        assert all(order.customer_email == "" for order in orders)

    @pytest.mark.asyncio
    async def test_update(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="charlie@example.com",
        )
        created_order = await dao.create(order_input)

        # When
        update_items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Pepperoni",
                quantity=2,
            ),
        ]
        update_data = OrderUpdateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=update_items,
            status=OrderStatus.CONFIRMED,  # Changed from COMPLETED to CONFIRMED
            customer_id=customer_id,
            subtotal=Decimal("29.98"),  # 2 * 14.99
            total=Decimal("29.98"),
            customer_email="charlie@example.com",
            notes="Extra spicy",
        )
        updated_order = await dao.update(str(created_order.id), update_data)

        # Then
        assert updated_order is not None
        assert updated_order.id == created_order.id
        assert updated_order.status == OrderStatus.CONFIRMED
        assert len(updated_order.items) == 1
        assert updated_order.total == Decimal("29.98")
        assert updated_order.notes == "Extra spicy"

    @pytest.mark.asyncio
    async def test_update_nonexistent_order(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        nonexistent_id = str(uuid4())
        update_items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
        ]
        update_data = OrderUpdateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=update_items,
            status=OrderStatus.CONFIRMED,
            customer_id=uuid4(),
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="test@example.com",
        )

        # When/Then
        with pytest.raises(
            ValueError, match=f"Order {nonexistent_id} not found"
        ):
            await dao.update(nonexistent_id, update_data)

    @pytest.mark.asyncio
    async def test_update_with_nonexistent_pizza(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="test@example.com",
        )
        created_order = await dao.create(order_input)

        # When
        update_items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="NonexistentPizza",
                quantity=1,
            ),
        ]
        update_data = OrderUpdateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=update_items,
            status=OrderStatus.CONFIRMED,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="test@example.com",
        )

        # When/Then
        with pytest.raises(
            ValueError, match="Pizza NonexistentPizza not found"
        ):
            await dao.update(str(created_order.id), update_data)

    @pytest.mark.asyncio
    async def test_update_with_nonexistent_beer(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("12.99"),
            total=Decimal("12.99"),
            customer_email="test@example.com",
        )
        created_order = await dao.create(order_input)

        # When
        update_items = [
            OrderItemInputDTO(
                type="beer",
                product_name="NonexistentBeer",
                quantity=1,
            ),
        ]
        update_data = OrderUpdateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=update_items,
            status=OrderStatus.CONFIRMED,
            customer_id=customer_id,
            subtotal=Decimal("5.99"),
            total=Decimal("5.99"),
            customer_email="test@example.com",
        )

        # When/Then
        with pytest.raises(ValueError, match="Beer NonexistentBeer not found"):
            await dao.update(str(created_order.id), update_data)

    @pytest.mark.asyncio
    async def test_get_all_with_missing_products(
        self,
        db: AsyncSession,
        seed_test_data: None,
    ) -> None:
        # Given
        dao = SQLOrderDAO(db)
        customer_id = uuid4()
        items = [
            OrderItemInputDTO(
                type="pizza",
                product_name="Margherita",
                quantity=1,
            ),
            OrderItemInputDTO(
                type="beer",
                product_name="Heineken",
                quantity=1,
            ),
        ]

        order_input = OrderCreateInternalDTO(
            service_type=ServiceType.DINE_IN,
            items=items,
            customer_id=customer_id,
            subtotal=Decimal("18.98"),  # 12.99 + 5.99
            total=Decimal("18.98"),
            customer_email="test@example.com",
        )
        created_order = await dao.create(order_input)

        # First delete the order items
        await db.execute(
            text("DELETE FROM order_pizza WHERE order_id = :order_id"),
            {"order_id": created_order.id},
        )
        await db.execute(
            text("DELETE FROM order_beer WHERE order_id = :order_id"),
            {"order_id": created_order.id},
        )
        await db.commit()

        # Then delete the pizza and beer from the database
        await db.execute(text("DELETE FROM pizza WHERE name = 'Margherita'"))
        await db.execute(text("DELETE FROM beer WHERE name = 'Heineken'"))
        await db.commit()

        # When
        orders = await dao.get_all()

        # Then
        assert len(orders) >= 1
        # The order should exist but without any items since the products were deleted
        order = next(order for order in orders if order.id == created_order.id)
        assert order is not None
        assert len(order.items) == 0  # No items since products were deleted
        assert order.total == Decimal("18.98")  # Total should remain unchanged

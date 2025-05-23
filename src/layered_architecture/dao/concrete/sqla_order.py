from typing import Callable, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.dao.interfaces import OrderDAOInterface
from layered_architecture.db.models import (
    Beer,
    Order,
    OrderBeer,
    OrderPizza,
    Pizza,
)
from layered_architecture.dto import (
    OrderCreateInternalDTO,
    OrderDTO,
    OrderItemDTO,
    OrderUpdateInternalDTO,
)


class SQLOrderDAO(OrderDAOInterface):
    """SQLAlchemy implementation of the OrderDAO interface."""

    def __init__(self, session: AsyncSession):
        """Initialize the DAO with a database session.

        :param session: The SQLAlchemy async session to use
        :type session: AsyncSession
        """
        self.session = session

    async def create(self, order_input: OrderCreateInternalDTO) -> OrderDTO:
        """Create a new order.

        :param order_input: The order input data with customer details
        :type order_input: OrderCreateInternalDTO
        :return: The created order
        :rtype: OrderDTO
        """
        # Create order
        order = Order(
            service_type=order_input.service_type,
            customer_id=order_input.customer_id,
            status="pending",
            subtotal=order_input.subtotal,
            total=order_input.total,
            notes=order_input.notes,
            delivery_address=order_input.delivery_address,
        )

        # Add order first and flush to get the ID
        self.session.add(order)
        await self.session.flush()

        # Now add items to order and collect OrderItemDTOs
        items: List[OrderItemDTO] = []
        for item in order_input.items:
            if item.type == "pizza":
                # Look up pizza by name
                pizza_result = await self.session.execute(
                    select(Pizza).where(Pizza.name == item.product_name)
                )
                pizza = pizza_result.scalar_one_or_none()
                if not pizza:
                    raise ValueError(f"Pizza {item.product_name} not found")

                order_pizza = OrderPizza(
                    order_id=order.id,
                    pizza_id=pizza.id,
                    quantity=item.quantity,
                )
                self.session.add(order_pizza)
                items.append(
                    OrderItemDTO(
                        product_id=pizza.id,
                        quantity=item.quantity,
                        price=pizza.price,
                        type="pizza",
                    )
                )
            elif item.type == "beer":
                # Look up beer by name
                beer_result = await self.session.execute(
                    select(Beer).where(Beer.name == item.product_name)
                )
                beer = beer_result.scalar_one_or_none()
                if not beer:
                    raise ValueError(f"Beer {item.product_name} not found")

                order_beer = OrderBeer(
                    order_id=order.id,
                    beer_id=beer.id,
                    quantity=item.quantity,
                )
                self.session.add(order_beer)
                items.append(
                    OrderItemDTO(
                        product_id=beer.id,
                        quantity=item.quantity,
                        price=beer.price,
                        type="beer",
                    )
                )

        # Flush the order items
        await self.session.flush()

        return OrderDTO(
            id=order.id,
            service_type=order.service_type,
            customer_id=order_input.customer_id,
            status=order.status,
            items=items,  # Use converted items
            total=order_input.total,
            customer_email=order_input.customer_email,
            notes=order_input.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            delivery_address=order.delivery_address,
        )

    async def get_by_id(
        self,
        order_id: str,
        get_customer_email: Callable[[str], str] | None = None,
    ) -> Optional[OrderDTO]:
        """Get an order by its ID.

        :param order_id: The ID of the order to retrieve
        :type order_id: str
        :param get_customer_email: Optional function to get customer email by ID
        :type get_customer_email: Callable[[str], str] | None
        :return: The order if found, None otherwise
        :rtype: Optional[OrderDTO]
        """
        # First get the order
        order_result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = order_result.scalar_one_or_none()
        if not order:
            return None

        # Then get all items in a single query
        items_result = await self.session.execute(
            select(OrderPizza, Pizza, OrderBeer, Beer)
            .outerjoin(Pizza, OrderPizza.pizza_id == Pizza.id)
            .outerjoin(OrderBeer, OrderPizza.order_id == OrderBeer.order_id)
            .outerjoin(Beer, OrderBeer.beer_id == Beer.id)
            .where(OrderPizza.order_id == order_id)
        )

        items: List[OrderItemDTO] = []
        for row in items_result:
            order_pizza, pizza, order_beer, beer = row

            # Add pizza if present
            if pizza is not None:
                items.append(
                    OrderItemDTO(
                        product_id=pizza.id,
                        quantity=order_pizza.quantity,
                        price=pizza.price,
                        type="pizza",
                    )
                )

            # Add beer if present
            if beer is not None:
                items.append(
                    OrderItemDTO(
                        product_id=beer.id,
                        quantity=order_beer.quantity,
                        price=beer.price,
                        type="beer",
                    )
                )

        # Get customer email if function is provided
        customer_email = ""
        if get_customer_email:
            customer_email = get_customer_email(str(order.customer_id))

        return OrderDTO(
            id=order.id,
            service_type=order.service_type,
            customer_id=order.customer_id,
            status=order.status,
            items=items,
            total=order.total,
            customer_email=customer_email,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            delivery_address=order.delivery_address,
        )

    async def get_all(self) -> List[OrderDTO]:
        """Get all orders.

        :return: List of all orders
        :rtype: List[OrderDTO]
        """
        result = await self.session.execute(select(Order))
        orders = result.scalars().all()

        order_dtos = []
        for order in orders:
            # Get items for each order
            items: List[OrderItemDTO] = []

            # Get pizzas
            pizza_result = await self.session.execute(
                select(OrderPizza).where(OrderPizza.order_id == order.id)
            )
            for pizza_row in pizza_result.scalars():
                pizza = await self.session.get(Pizza, pizza_row.pizza_id)
                if pizza is None:
                    continue
                items.append(
                    OrderItemDTO(
                        product_id=str(pizza.id),
                        quantity=pizza_row.quantity,
                        price=pizza.price,
                        type="pizza",
                    )
                )

            # Get beers
            beer_result = await self.session.execute(
                select(OrderBeer).where(OrderBeer.order_id == order.id)
            )
            for beer_row in beer_result.scalars():
                beer = await self.session.get(Beer, beer_row.beer_id)
                if beer is None:
                    continue
                items.append(
                    OrderItemDTO(
                        product_id=str(beer.id),
                        quantity=beer_row.quantity,
                        price=beer.price,
                        type="beer",
                    )
                )

            order_dtos.append(
                OrderDTO(
                    id=str(order.id),
                    service_type=order.service_type,
                    customer_id=order.customer_id,
                    status=order.status,
                    items=items,
                    total=order.total,
                    customer_email="",  # Use empty string instead of None
                    notes=order.notes,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                    delivery_address=order.delivery_address,
                )
            )

        return order_dtos

    async def update(
        self, order_id: str, update_data: OrderUpdateInternalDTO
    ) -> OrderDTO:
        """Update an existing order.

        :param order_id: The ID of the order to update
        :type order_id: str
        :param update_data: The data to update the order with
        :type update_data: OrderUpdateInternalDTO
        :return: The updated order
        :rtype: OrderDTO
        :raises ValueError: If the order is not found
        """
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError(f"Order {order_id} not found")

        # Update order fields
        if update_data.status is not None:
            order.status = update_data.status
        if update_data.notes is not None:
            order.notes = update_data.notes
        if update_data.total is not None:
            order.total = update_data.total
        if update_data.subtotal is not None:
            order.subtotal = update_data.subtotal
        if update_data.delivery_address is not None:
            order.delivery_address = update_data.delivery_address

        # Delete existing items
        await self.session.execute(
            delete(OrderPizza).where(OrderPizza.order_id == order_id)
        )
        await self.session.execute(
            delete(OrderBeer).where(OrderBeer.order_id == order_id)
        )

        # Add new items
        items: List[OrderItemDTO] = []
        for item in update_data.items:
            if item.type == "pizza":
                # Look up pizza by name
                pizza_result = await self.session.execute(
                    select(Pizza).where(Pizza.name == item.product_name)
                )
                pizza = pizza_result.scalar_one_or_none()
                if not pizza:
                    raise ValueError(f"Pizza {item.product_name} not found")

                order_pizza = OrderPizza(
                    order_id=order.id,
                    pizza_id=pizza.id,
                    quantity=item.quantity,
                )
                self.session.add(order_pizza)
                items.append(
                    OrderItemDTO(
                        product_id=pizza.id,
                        quantity=item.quantity,
                        price=pizza.price,
                        type="pizza",
                    )
                )
            elif item.type == "beer":
                # Look up beer by name
                beer_result = await self.session.execute(
                    select(Beer).where(Beer.name == item.product_name)
                )
                beer = beer_result.scalar_one_or_none()
                if not beer:
                    raise ValueError(f"Beer {item.product_name} not found")

                order_beer = OrderBeer(
                    order_id=order.id,
                    beer_id=beer.id,
                    quantity=item.quantity,
                )
                self.session.add(order_beer)
                items.append(
                    OrderItemDTO(
                        product_id=beer.id,
                        quantity=item.quantity,
                        price=beer.price,
                        type="beer",
                    )
                )

        # Flush changes to ensure they are visible in the current session
        await self.session.flush()

        # Get updated order with items
        return await self.get_by_id(order_id)

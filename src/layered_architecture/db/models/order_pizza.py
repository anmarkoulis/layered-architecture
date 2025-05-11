from sqlalchemy import Column, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from layered_architecture.db.models.mixins import UUIDMixin


class OrderPizza(Base, UUIDMixin):
    """Association table for orders and pizzas."""

    order_id = Column(
        UUID(as_uuid=True), ForeignKey("order.id"), nullable=False
    )
    pizza_id = Column(
        UUID(as_uuid=True), ForeignKey("pizza.id"), nullable=False
    )
    quantity = Column(Numeric(10, 0), nullable=False)

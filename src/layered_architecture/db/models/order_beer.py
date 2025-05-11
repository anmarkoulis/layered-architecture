from sqlalchemy import Column, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from layered_architecture.db.models.mixins import UUIDMixin


class OrderBeer(Base, UUIDMixin):
    """Association table for orders and beers."""

    order_id = Column(
        UUID(as_uuid=True), ForeignKey("order.id"), nullable=False
    )
    beer_id = Column(UUID(as_uuid=True), ForeignKey("beer.id"), nullable=False)
    quantity = Column(Numeric(10, 0), nullable=False)

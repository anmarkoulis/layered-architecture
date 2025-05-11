from datetime import datetime

from sqlalchemy import Column, DateTime, String

from .base import Base
from layered_architecture.db.models.mixins import UUIDMixin


class Order(Base, UUIDMixin):
    """Order model."""

    store_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    status = Column(String, nullable=False)
    total_amount = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    delivery_address = Column(String, nullable=True)
    notes = Column(String, nullable=True)

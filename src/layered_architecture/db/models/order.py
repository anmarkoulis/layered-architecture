from decimal import Decimal
from typing import Optional

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from layered_architecture.db.models.mixins import (
    CreatedAtMixin,
    UpdatedAtMixin,
    UUIDMixin,
)
from layered_architecture.enums import StoreType


class Order(Base, CreatedAtMixin, UpdatedAtMixin, UUIDMixin):
    """Order model representing a customer order in the system."""

    store_type: Mapped[StoreType] = mapped_column(nullable=False)
    customer_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    customer_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    customer_email: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    customer_phone: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    delivery_address: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

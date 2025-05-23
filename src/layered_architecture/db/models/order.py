from decimal import Decimal

from sqlalchemy import Enum as SQLEnum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CreatedAtMixin, UpdatedAtMixin, UUIDMixin
from layered_architecture.enums import OrderStatus, ServiceType


class Order(Base, UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    """Order model."""

    service_type: Mapped[ServiceType] = mapped_column(
        SQLEnum(ServiceType), nullable=False
    )
    customer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str] = mapped_column(String, nullable=True)

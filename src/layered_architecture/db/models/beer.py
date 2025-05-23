from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CreatedAtMixin, UpdatedAtMixin, UUIDMixin


class Beer(Base, UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    """Beer model."""

    name: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_tap: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

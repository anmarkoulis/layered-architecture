from decimal import Decimal
from uuid import UUID

from pydantic import Field

from .base import ModelConfigBaseModel


class PizzaDTO(ModelConfigBaseModel):
    """DTO for pizza data."""

    id: UUID = Field(..., description="Pizza ID")
    name: str = Field(..., description="Name of the pizza")
    price: Decimal = Field(..., ge=0, description="Price of the pizza")
    description: str | None = Field(
        None, description="Optional description of the pizza"
    )

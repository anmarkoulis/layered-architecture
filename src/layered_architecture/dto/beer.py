from decimal import Decimal
from uuid import UUID

from pydantic import Field

from .base import ModelConfigBaseModel


class BeerDTO(ModelConfigBaseModel):
    """DTO for beer data."""

    id: UUID = Field(..., description="Beer ID")
    name: str = Field(..., description="Name of the beer")
    price: Decimal = Field(..., ge=0, description="Price of the beer")
    description: str | None = Field(
        None, description="Optional description of the beer"
    )

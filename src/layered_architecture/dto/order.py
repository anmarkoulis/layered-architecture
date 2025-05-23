from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import Field

from .base import ModelConfigBaseModel
from layered_architecture.enums import OrderStatus, ServiceType


class OrderItemInputDTO(ModelConfigBaseModel):
    """Input DTO for order items."""

    type: str = Field(..., description="Type of item (pizza or beer)")
    product_name: str = Field(
        ...,
        description="Name of the product (e.g., 'Margherita' for pizza or 'Heineken' for beer)",
    )
    quantity: int = Field(..., ge=1, description="Quantity of the item")


class OrderInputDTO(ModelConfigBaseModel):
    """DTO for order input from API."""

    service_type: ServiceType
    items: list[OrderItemInputDTO]
    notes: str | None = None


class OrderCreateInternalDTO(ModelConfigBaseModel):
    """Internal DTO for order creation with customer details."""

    service_type: ServiceType
    items: list[OrderItemInputDTO]
    notes: str | None = None
    customer_id: UUID
    subtotal: Decimal
    total: Decimal
    customer_email: str


class OrderUpdateDTO(ModelConfigBaseModel):
    """DTO for order updates."""

    service_type: ServiceType
    items: list[OrderItemInputDTO]
    notes: str | None = None
    status: OrderStatus
    customer_id: UUID
    subtotal: Decimal
    total: Decimal
    customer_email: str


class OrderItemDTO(ModelConfigBaseModel):
    """DTO for order items."""

    type: str = Field(..., description="Type of item (pizza or beer)")
    product_id: UUID = Field(..., description="ID of the product")
    quantity: int = Field(..., ge=1, description="Quantity of the item")
    price: Decimal = Field(..., ge=0, description="Price of the item")


class OrderDTO(ModelConfigBaseModel):
    """DTO for order responses."""

    id: UUID = Field(..., description="Order ID")
    service_type: ServiceType = Field(..., description="Type of service")
    customer_id: UUID = Field(..., description="ID of the customer")
    status: OrderStatus = Field(..., description="Current status of the order")
    items: List[OrderItemDTO] = Field(
        ..., description="List of items in the order"
    )
    total: Decimal = Field(..., description="Total amount of the order")
    customer_email: str = Field(..., description="Email of the customer")
    notes: str | None = Field(None, description="Optional notes for the order")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

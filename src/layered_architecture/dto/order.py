from decimal import Decimal
from typing import Annotated, List

from pydantic import Field

from .base import ModelConfigBaseModel
from layered_architecture.enums import StoreType


class OrderItemDTO(ModelConfigBaseModel):
    product_id: Annotated[str, Field(description="The ID of the product")]
    quantity: Annotated[
        int, Field(description="The quantity of the product", ge=1)
    ]
    price: Annotated[Decimal, Field(description="The price of the product")]
    type: Annotated[
        str, Field(description="The type of the product (pizza or beer)")
    ]


class OrderInputDTO(ModelConfigBaseModel):
    store_type: Annotated[
        StoreType, Field(description="The type of the store")
    ]
    customer_id: Annotated[str, Field(description="The ID of the customer")]
    items: Annotated[
        List[OrderItemDTO], Field(description="The items in the order")
    ]
    total: Annotated[
        Decimal, Field(description="The total amount of the order")
    ]


class OrderDTO(ModelConfigBaseModel):
    id: Annotated[str, Field(description="The ID of the order")]
    store_type: Annotated[
        StoreType, Field(description="The type of the store")
    ]
    customer_id: Annotated[str, Field(description="The ID of the customer")]
    items: Annotated[
        List[OrderItemDTO], Field(description="The items in the order")
    ]
    total: Annotated[
        Decimal, Field(description="The total amount of the order")
    ]

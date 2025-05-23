"""Services package."""

from .concrete import (
    DeliveryOrderService,
    DineInOrderService,
    FakeAuthService,
    LateNightOrderService,
    TakeawayOrderService,
)
from .interfaces import AuthServiceInterface, OrderServiceInterface

__all__ = [
    "DeliveryOrderService",
    "DineInOrderService",
    "LateNightOrderService",
    "TakeawayOrderService",
    "AuthServiceInterface",
    "OrderServiceInterface",
]

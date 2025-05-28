from enum import Enum


class ServiceType(str, Enum):
    """Service type enum."""

    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"
    LATE_NIGHT = "late_night"

    @staticmethod
    def get_default() -> "ServiceType":
        """Get the default service type.

        :return: The default service type (DINE_IN)
        :rtype: ServiceType
        """
        return ServiceType.DINE_IN


class OrderStatus(str, Enum):
    """Order status enum."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

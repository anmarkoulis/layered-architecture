from typing import List, Optional

from .base import ModelConfigBaseModel


class ErrorResponse(ModelConfigBaseModel):
    """Schema for a single error response."""

    code: str
    details: str
    message: Optional[str] = None
    key: Optional[str] = None


class ErrorEnvelope(ModelConfigBaseModel):
    """Schema for the error response envelope."""

    errors: List[ErrorResponse]

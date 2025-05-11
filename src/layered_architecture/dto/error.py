from typing import List, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Schema for a single error response."""

    code: str
    details: str
    message: Optional[str] = None
    key: Optional[str] = None


class ErrorEnvelope(BaseModel):
    """Schema for the error response envelope."""

    errors: List[ErrorResponse]

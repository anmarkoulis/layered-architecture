from .base import ModelConfigBaseModel


class HealthResponse(ModelConfigBaseModel):
    """Health check response model."""

    status: str

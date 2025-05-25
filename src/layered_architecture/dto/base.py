from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class ModelConfigBaseModel(BaseModel):
    """Base DTO class with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Custom serialization to handle Enum values."""
        data = super().model_dump(**kwargs)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data

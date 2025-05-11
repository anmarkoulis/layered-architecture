import re
from typing import Any

from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for all SQLAlchemy models."""

    @declared_attr  # type: ignore[arg-type]
    def __tablename__(  # pylint: disable=no-self-argument
        cls: Any,
    ) -> str:
        # Convert CamelCase to snake_case
        name: str = cls.__name__
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()

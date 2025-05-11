from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID


class UUIDMixin:
    """Mixin to add UUID primary key to models."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

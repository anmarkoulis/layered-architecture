from datetime import datetime

from sqlalchemy import Column, DateTime


class UpdatedAtMixin(object):
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=datetime.utcnow,
        nullable=True,
        default=None,
    )

from sqlalchemy import Column, DateTime, func


class UpdatedAtMixin(object):
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),  # pylint: disable=not-callable
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
    )

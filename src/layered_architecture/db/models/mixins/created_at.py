from sqlalchemy import Column, DateTime, func


class CreatedAtMixin(object):
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
    )

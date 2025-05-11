from sqlalchemy import Column, DateTime


class DeletedAtMixin(object):
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

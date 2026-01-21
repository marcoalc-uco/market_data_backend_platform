"""SQLAlchemy model base classes and mixins.

This module provides the declarative base class and common mixins
for all database models in the application.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):  # type: ignore[misc]
    """Base class for all SQLAlchemy models.

    All models should inherit from this class to use the ORM features.
    Each model must define its own __tablename__ explicitly.

    Note: The type: ignore is needed because mypy doesn't fully understand
    SQLAlchemy's metaprogramming. DeclarativeBase uses complex metaclasses
    that mypy interprets as "Any".
    """


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns.

    Use this mixin for models that need to track creation and update times.

    Example:
        class User(TimestampMixin, Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

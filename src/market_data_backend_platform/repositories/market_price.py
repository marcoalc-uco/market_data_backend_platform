"""Repository for MarketPrice model operations.

This module provides database access methods specific to MarketPrice entities.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from market_data_backend_platform.models.market_price import MarketPrice
from market_data_backend_platform.repositories.base import BaseRepository


class MarketPriceRepository(BaseRepository[MarketPrice]):
    """Repository for MarketPrice CRUD and query operations.

    Extends BaseRepository with MarketPrice-specific query methods.

    Example::

        repo = MarketPriceRepository(session)
        prices = repo.get_by_instrument(instrument_id=1)
        latest = repo.get_latest_price(instrument_id=1)
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        super().__init__(session, MarketPrice)

    def get_by_instrument(
        self,
        instrument_id: int,
        limit: int | None = None,
    ) -> list[MarketPrice]:
        """Get price records for a specific instrument.

        Args:
            instrument_id: ID of the instrument.
            limit: Optional maximum number of records to return.

        Returns:
            List of MarketPrice records ordered by timestamp descending.
        """
        query = (
            self.session.query(MarketPrice)
            .filter(MarketPrice.instrument_id == instrument_id)
            .order_by(MarketPrice.timestamp.desc())
        )
        if limit:
            query = query.limit(limit)
        return list(query.all())

    def get_latest_price(self, instrument_id: int) -> MarketPrice | None:
        """Get the most recent price for an instrument.

        Args:
            instrument_id: ID of the instrument.

        Returns:
            The most recent MarketPrice if exists, None otherwise.
        """
        return (
            self.session.query(MarketPrice)
            .filter(MarketPrice.instrument_id == instrument_id)
            .order_by(MarketPrice.timestamp.desc())
            .first()
        )

    def get_by_date_range(
        self,
        instrument_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[MarketPrice]:
        """Get price records within a date range.

        Args:
            instrument_id: ID of the instrument.
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).

        Returns:
            List of MarketPrice records within the range.
        """
        return list(
            self.session.query(MarketPrice)
            .filter(
                MarketPrice.instrument_id == instrument_id,
                MarketPrice.timestamp >= start_date,
                MarketPrice.timestamp <= end_date,
            )
            .order_by(MarketPrice.timestamp.asc())
            .all()
        )

    def bulk_create(self, prices: list[MarketPrice]) -> list[MarketPrice]:
        """Create multiple price records efficiently.

        Args:
            prices: List of MarketPrice instances to persist.

        Returns:
            The persisted MarketPrice instances.
        """
        self.session.add_all(prices)
        self.session.commit()
        for price in prices:
            self.session.refresh(price)
        return prices

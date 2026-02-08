"""Ingestion service for loading data into the database.

This module provides the IngestionService class for orchestrating
data fetching from external APIs and loading into the database.

Example::

    from sqlalchemy.orm import Session

    service = IngestionService(
        instrument_repo=InstrumentRepository(session),
        price_repo=MarketPriceRepository(session),
        yahoo_client=YahooFinanceClient(),
    )
    count = service.ingest_by_symbol("AAPL", period="1mo")
    print(f"Ingested {count} prices")
"""

from market_data_backend_platform.core import get_logger
from market_data_backend_platform.etl.clients.yahoo import YahooFinanceClient
from market_data_backend_platform.etl.transformers.yahoo_transformer import (
    YahooTransformer,
)
from market_data_backend_platform.models.market_price import MarketPrice
from market_data_backend_platform.repositories.instrument import InstrumentRepository
from market_data_backend_platform.repositories.market_price import MarketPriceRepository

logger = get_logger(__name__)


class IngestionService:
    """Service for ingesting market data into the database.

    Orchestrates fetching from external APIs, transforming data,
    and loading into PostgreSQL.

    This follows the Dependency Inversion Principle (SOLID):
    the service depends on abstractions (repositories) not
    concrete implementations.

    Example::

        service = IngestionService(
            instrument_repo=InstrumentRepository(session),
            price_repo=MarketPriceRepository(session),
            yahoo_client=YahooFinanceClient(),
        )
        count = service.ingest_by_symbol("AAPL", period="1mo")
    """

    def __init__(
        self,
        instrument_repo: InstrumentRepository,
        price_repo: MarketPriceRepository,
        yahoo_client: YahooFinanceClient,
    ) -> None:
        """Initialize the ingestion service.

        Args:
            instrument_repo: Repository for instrument lookups.
            price_repo: Repository for persisting market prices.
            yahoo_client: Client for fetching data from Yahoo Finance.
        """
        self.instrument_repo = instrument_repo
        self.price_repo = price_repo
        self.yahoo_client = yahoo_client
        self.transformer = YahooTransformer()

    def ingest_by_symbol(
        self,
        symbol: str,
        interval: str = "1d",
        period: str = "1mo",
    ) -> int:
        """Ingest historical prices for a symbol.

        Fetches data from Yahoo Finance, transforms it to
        MarketPrice entities, and persists to the database.

        Args:
            symbol: Stock symbol (e.g., "AAPL", "GOOGL").
            interval: Data interval (1d, 1wk, 1mo).
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max).

        Returns:
            Number of prices ingested.
        """
        # Step 1: Lookup instrument in database
        instrument = self.instrument_repo.get_by_symbol(symbol)
        if instrument is None:
            logger.warning("instrument_not_found", symbol=symbol)
            return 0

        # Step 2: Fetch from Yahoo Finance
        quotes = self.yahoo_client.get_historical_prices(
            symbol=symbol,
            interval=interval,
            period=period,
        )
        if quotes is None:
            logger.warning("yahoo_no_data", symbol=symbol)
            return 0

        logger.info(
            "ingestion_fetched",
            symbol=symbol,
            count=len(quotes),
        )

        # Step 3: Transform to MarketPriceCreate schemas
        schemas = self.transformer.transform_batch(quotes, instrument.id)

        # Step 4: Convert schemas to model instances
        prices = [
            MarketPrice(
                instrument_id=schema.instrument_id,
                timestamp=schema.timestamp,
                open=schema.open,
                high=schema.high,
                low=schema.low,
                close=schema.close,
                volume=schema.volume,
            )
            for schema in schemas
        ]

        # Step 5: Persist to database (idempotent - skips existing)
        inserted_prices = self.price_repo.bulk_create_new(prices)

        logger.info(
            "ingestion_complete",
            symbol=symbol,
            fetched=len(prices),
            inserted=len(inserted_prices),
            skipped=len(prices) - len(inserted_prices),
            instrument_id=instrument.id,
        )

        return len(inserted_prices)

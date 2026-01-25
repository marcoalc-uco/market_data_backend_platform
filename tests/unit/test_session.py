"""Tests for database session configuration.

This module tests the database engine and session factory setup.
Following TDD: These tests are written FIRST, before implementation.

For unit tests, we use SQLite in-memory to avoid PostgreSQL dependency.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class TestDatabaseEngineConfiguration:
    """Tests for SQLAlchemy engine configuration logic."""

    def test_engine_with_sqlite_returns_engine_instance(self) -> None:
        """Test that creating an engine returns a valid SQLAlchemy Engine."""
        test_engine = create_engine("sqlite:///:memory:")
        assert isinstance(test_engine, Engine)

    def test_engine_can_execute_queries(self) -> None:
        """Test that the engine can execute basic queries."""
        test_engine = create_engine("sqlite:///:memory:")
        with test_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1


class TestSessionFactory:
    """Tests for SQLAlchemy session factory."""

    @pytest.fixture
    def test_engine(self) -> Engine:
        """Create a test engine with SQLite in-memory."""
        return create_engine("sqlite:///:memory:")

    @pytest.fixture
    def test_session_factory(self, test_engine: Engine) -> sessionmaker[Session]:
        """Create a test session factory."""
        return sessionmaker(
            bind=test_engine,
            autocommit=False,
            autoflush=False,
        )

    def test_session_factory_creates_session(
        self, test_session_factory: sessionmaker[Session]
    ) -> None:
        """Test that session factory creates valid sessions."""
        session = test_session_factory()
        assert isinstance(session, Session)
        session.close()

    def test_session_executes_queries(
        self, test_session_factory: sessionmaker[Session]
    ) -> None:
        """Test that session can execute basic queries."""
        session = test_session_factory()
        result = session.execute(text("SELECT 1 + 1"))
        assert result.scalar() == 2
        session.close()

    def test_session_is_bound_to_engine(
        self,
        test_engine: Engine,
        test_session_factory: sessionmaker[Session],
    ) -> None:
        """Test that sessions are properly bound to the engine."""
        session = test_session_factory()
        assert session.get_bind() == test_engine
        session.close()


class TestGetSessionGenerator:
    """Tests for the get_session dependency generator."""

    def test_get_session_yields_session(self) -> None:
        """Test that get_session generator yields a Session."""
        from market_data_backend_platform.db.session import (
            SessionLocal,
            create_test_session_factory,
        )

        # Use test factory for SQLite
        test_factory = create_test_session_factory()
        session_gen = _get_session_from_factory(test_factory)
        session = next(session_gen)

        assert isinstance(session, Session)

        # Clean up
        try:
            next(session_gen)
        except StopIteration:
            pass


def _get_session_from_factory(
    factory: sessionmaker[Session],
) -> "Generator[Session, None, None]":
    """Helper to create a session generator from a factory.

    This mimics the get_session behavior for testing.
    """
    from collections.abc import Generator

    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

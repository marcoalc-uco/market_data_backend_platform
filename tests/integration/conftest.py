"""Integration test fixtures.

Provides fixtures for Docker-based integration testing.
Uses subprocess to control docker-compose services.
"""

import subprocess
import time
from typing import Generator

import httpx
import psycopg2
import pytest


@pytest.fixture(scope="session")
def docker_compose_up() -> Generator[None, None, None]:
    """Start Docker Compose services for integration tests.

    This fixture:
    1. Starts all services defined in docker-compose.yml
    2. Waits for services to be healthy
    3. Yields control to tests
    4. Tears down services after all tests complete
    """
    # Start services
    subprocess.run(
        ["docker-compose", "up", "-d"],
        check=True,
        capture_output=True,
    )

    # Wait for services to be healthy
    max_retries = 30
    for i in range(max_retries):
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Simple check: if output contains "Up", services are running
            if "Up" in result.stdout:
                time.sleep(5)  # Extra wait for health checks
                break
        except subprocess.CalledProcessError:
            pass

        time.sleep(1)

        if i == max_retries - 1:
            raise RuntimeError("Docker services failed to start")

    yield

    # Teardown: stop services
    subprocess.run(
        ["docker-compose", "down"],
        check=False,  # Don't fail if already down
        capture_output=True,
    )


@pytest.fixture
def api_client(docker_compose_up: None) -> Generator[httpx.Client, None, None]:
    """HTTP client for the containerized API.

    Args:
        docker_compose_up: Ensures Docker services are running

    Yields:
        Configured httpx.Client pointing to the API
    """
    base_url = "http://localhost:8000"

    # Wait for API to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = httpx.get(f"{base_url}/health", timeout=2.0)
            if response.status_code == 200:
                break
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        time.sleep(1)

        if i == max_retries - 1:
            raise RuntimeError("API failed to become ready")

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def db_connection(
    docker_compose_up: None,
) -> Generator[psycopg2.extensions.connection, None, None]:
    """Direct PostgreSQL connection for data verification.

    Args:
        docker_compose_up: Ensures Docker services are running

    Yields:
        psycopg2 connection to the containerized database
    """
    # Wait for PostgreSQL to be ready
    max_retries = 30
    conn = None

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="market_data",
                password="market_data_pass",
                database="market_data",
            )
            break
        except psycopg2.OperationalError:
            time.sleep(1)

            if i == max_retries - 1:
                raise RuntimeError("PostgreSQL failed to become ready")

    if conn is None:
        raise RuntimeError("Failed to establish database connection")

    yield conn

    conn.close()

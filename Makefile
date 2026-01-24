# Makefile for Market Data Backend Platform

.PHONY: dev test db-migrate db-upgrade db-downgrade clean help

# Default target
help:
	@echo Available commands:
	@echo   make dev          - Start development server
	@echo   make test         - Run unit tests
	@echo   make db-migrate   - Generate Alembic migration (requires PostgreSQL)
	@echo   make db-upgrade   - Apply pending migrations
	@echo   make db-downgrade - Revert last migration
	@echo   make clean        - Remove temporary files

# Start development server with hot reload
dev:
	.\.venv\Scripts\uvicorn.exe market_data_backend_platform.main:app --reload --host 0.0.0.0 --port 8000

# Run unit tests (quick feedback during development)
test:
	.\.venv\Scripts\pytest.exe tests/unit/ -q

# Run all tests including integration (when available)
test-all:
	.\.venv\Scripts\pytest.exe tests/ -v

# Generate new Alembic migration (autogenerate from model changes)
# Usage: make db-migrate msg="add user table"
db-migrate:
	.\.venv\Scripts\alembic.exe revision --autogenerate -m "$(msg)"

# Apply all pending migrations
db-upgrade:
	.\.venv\Scripts\alembic.exe upgrade head

# Revert last migration
db-downgrade:
	.\.venv\Scripts\alembic.exe downgrade -1

# Show current migration status
db-status:
	.\.venv\Scripts\alembic.exe current

# Clean temporary files
clean:
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist .coverage del .coverage
	@echo Cleaned temporary files

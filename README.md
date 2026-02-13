# Market Data Backend Platform

FastAPI backend for financial market data ingestion and time-series visualization with Grafana.

---

## Overview

The **Market Data Backend Platform** is an API-first backend system designed for financial time-series data. It provides:

- **Data Ingestion**: ETL pipeline for market data from external APIs (Yahoo Finance, Alpha Vantage)
- **REST API**: FastAPI-based endpoints for querying instruments and prices
- **Visualization**: Grafana dashboards for real-time market data analysis
- **Persistence**: PostgreSQL database with optimized time-series storage
- **Reproducibility**: Docker Compose for local development

---

## Quick Start

### Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/market_data_backend_platform.git
cd market_data_backend_platform
```

### 2. Configure Environment

Copy the Docker environment template:

```bash
cp docker/.env.docker .env
```

Edit `.env` to customize credentials (optional):

```env
# PostgreSQL Configuration
POSTGRES_USER=market_data
POSTGRES_PASSWORD=market_data_pass
POSTGRES_DB=market_data

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# API Configuration
DEBUG=false
LOG_LEVEL=INFO
```

### 3. Start Services

Build and start all services (PostgreSQL, API, Grafana):

```bash
docker-compose up -d
```

This will:

- Build the FastAPI application Docker image
- Start PostgreSQL database
- Run database migrations (Alembic)
- Start the FastAPI server
- Start Grafana with pre-configured datasource and dashboards

### 4. Verify Services

Check that all services are running:

```bash
docker-compose ps
```

Expected output:

```
NAME                     STATUS              PORTS
market_data_postgres     Up (healthy)        0.0.0.0:5432->5432/tcp
market_data_api          Up (healthy)        0.0.0.0:8000->8000/tcp
market_data_grafana      Up                  0.0.0.0:3000->3000/tcp
```

### 5. Access Services

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **PostgreSQL**: localhost:5432 (market_data/market_data_pass)

---

## Usage

### Populate Data

Run the ETL ingestion to populate the database with market data:

```bash
# Enter the API container
docker-compose exec api bash

# Run ingestion (example - adjust based on your ETL implementation)
python -m market_data_backend_platform.etl.services.ingestion
```

### Query API

List all instruments:

```bash
curl http://localhost:8000/api/v1/instruments
```

Get prices for an instrument:

```bash
curl "http://localhost:8000/api/v1/prices/1?start_date=2024-01-01&end_date=2024-12-31"
```

### View Dashboards

1. Navigate to http://localhost:3000
2. Login with `admin/admin`
3. Go to **Dashboards** → **Market Data - Multi-Instrument by Asset Type**
4. Select asset type from dropdown (STOCK, INDEX, CRYPTO)
5. Adjust time range as needed

---

## Development

### Local Development (Without Docker)

#### Prerequisites

- Python 3.14+
- PostgreSQL 16+

#### Setup

1. Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env with your local PostgreSQL credentials
```

4. Run migrations:

```bash
alembic upgrade head
```

5. Start development server:

```bash
uvicorn market_data_backend_platform.main:app --reload
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/unit/test_instruments.py
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type check
make type-check

# Run all quality checks
make quality
```

---

## Docker Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f grafana
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U market_data -d market_data

# Run SQL query
docker-compose exec postgres psql -U market_data -d market_data -c "SELECT * FROM instruments;"
```

### Rebuild After Code Changes

```bash
# Rebuild API service
docker-compose build api

# Restart with new image
docker-compose up -d api
```

---

## Project Structure

```
market_data_backend_platform/
├── src/market_data_backend_platform/  # Application code
│   ├── api/                           # FastAPI routes
│   ├── core/                          # Configuration, logging
│   ├── models/                        # SQLAlchemy models
│   ├── schemas/                       # Pydantic schemas
│   ├── repositories/                  # Data access layer
│   ├── services/                      # Business logic
│   ├── etl/                           # Data ingestion
│   └── db/                            # Database session
├── tests/                             # Unit and integration tests
├── alembic/                           # Database migrations
├── docker/                            # Docker configuration
│   ├── Dockerfile                     # API container image
│   └── grafana/                       # Grafana provisioning
├── docs/                              # Documentation
├── docker-compose.yml                 # Multi-service orchestration
└── pyproject.toml                     # Project configuration
```

---

## Documentation

- **[Architecture](docs/architecture.md)**: System design and component overview
- **[Roadmap](docs/roadmap.md)**: Development phases and progress
- **[Grafana Guide](docs/GRAFANA.md)**: Dashboard usage and customization
- **[PRD](docs/PRD.md)**: Product requirements document
- **[DEV_PLAN](docs/DEV_PLAN.md)**: Development execution plan
- **[QA_PROTOCOL](docs/QA_PROTOCOL.md)**: Quality assurance checklist

---

## Troubleshooting

### Port Already in Use

If ports 5432, 8000, or 3000 are already in use:

1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`:

```yaml
services:
  postgres:
    ports:
      - "5433:5432" # Change host port
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### API Not Starting

```bash
# Check API logs
docker-compose logs api

# Common issues:
# 1. Database not ready - wait for postgres health check
# 2. Migration failed - check alembic logs
# 3. Port conflict - change port in docker-compose.yml
```

### Grafana Dashboard Empty

1. Verify data exists in database:

   ```bash
   docker-compose exec postgres psql -U market_data -d market_data -c "SELECT COUNT(*) FROM market_prices;"
   ```

2. Run ETL ingestion to populate data

3. Check Grafana datasource connection:
   - Go to Settings → Data Sources → PostgreSQL
   - Click "Save & Test"

---

## Technology Stack

- **API Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.x
- **Migrations**: Alembic 1.x
- **Validation**: Pydantic 2.x
- **Testing**: pytest 8.x
- **Visualization**: Grafana 11+
- **Containerization**: Docker & Docker Compose

---

## Contributing

See [AGENT.md](AGENT.md) for coding standards and development guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contact

For questions or issues, please open a GitHub issue.

---

**Version**: 1.0
**Last Updated**: 2026-02-13

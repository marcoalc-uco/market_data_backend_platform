# Arquitectura del Sistema — Market Data Backend Platform

## Visión general

El sistema es una **plataforma backend API-first** orientada a datos financieros y series temporales.

La arquitectura está diseñada para:

- Separar ingestión, persistencia, API y visualización.
- Facilitar la extensibilidad y testabilidad.
- Aplicar principios SOLID y patrones de diseño.
- Permitir análisis mediante herramientas estándar (Grafana).
- Ejecutarse de forma reproducible en entorno local.

---

## Principios de diseño

### SOLID

| Principio                 | Aplicación                                        |
| ------------------------- | ------------------------------------------------- |
| **S**ingle Responsibility | Cada módulo/clase tiene una única razón de cambio |
| **O**pen/Closed           | Extensible sin modificar código existente         |
| **L**iskov Substitution   | Abstracciones intercambiables                     |
| **I**nterface Segregation | Interfaces específicas por cliente                |
| **D**ependency Inversion  | Depender de abstracciones, no implementaciones    |

### DRY (Don't Repeat Yourself)

- Lógica compartida en módulos reutilizables.
- Configuración centralizada.
- Factories y generadores para reducir duplicación.

### PEP Compliance

- **PEP 8**: Estilo de código.
- **PEP 257**: Docstrings.
- **PEP 484/585**: Type hints.
- **PEP 621**: Metadata en `pyproject.toml`.

### Virtual Environment

- **venv**: Entorno virtual.
- **pip**: Gestor de paquetes.
- **requirements.txt**: Dependencias.
- Utiliza siempre .venv

---

## Stack tecnológico

| Capa                | Tecnología                    | Propósito               |
| ------------------- | ----------------------------- | ----------------------- |
| **API**             | FastAPI                       | Framework web asíncrono |
| **Validación**      | Pydantic                      | Schemas tipados         |
| **ORM**             | SQLAlchemy                    | ORM maduro y flexible   |
| **Migraciones**     | Alembic                       | Versionado de esquema   |
| **Base de datos**   | PostgreSQL / TimescaleDB      | Series temporales       |
| **Testing**         | pytest, httpx, testcontainers | TDD                     |
| **Calidad**         | ruff, mypy, pre-commit        | Linting y tipos         |
| **Logging**         | structlog                     | Logs estructurados      |
| **Visualización**   | Grafana                       | Dashboards              |
| **Infraestructura** | Docker Compose                | Orquestación local      |

---

## Estructura del proyecto

```
market_data_backend_platform/
├── src/
│   └── market_data/
│       ├── __init__.py
│       ├── main.py              # Entry point FastAPI
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes/          # Endpoints por dominio
│       │   │   ├── __init__.py
│       │   │   ├── health.py
│       │   │   ├── instruments.py
│       │   │   └── prices.py
│       │   └── dependencies.py  # Inyección de dependencias
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py        # Settings con pydantic-settings
│       │   ├── logging.py       # Configuración de logs
│       │   └── exceptions.py    # Excepciones personalizadas
│       ├── models/              # Entidades SQLModel
│       │   ├── __init__.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── schemas/             # DTOs Pydantic (request/response)
│       │   ├── __init__.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── repositories/        # Capa de acceso a datos
│       │   ├── __init__.py
│       │   ├── base.py          # Repository abstracto
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── services/            # Lógica de negocio
│       │   ├── __init__.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── etl/                 # Ingestión de datos
│       │   ├── __init__.py
│       │   ├── clients/         # Clientes API externos
│       │   └── transformers/    # Normalización
│       └── db/
│           ├── __init__.py
│           └── session.py       # Configuración de sesión
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartidos
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py
├── alembic/
│   ├── versions/
│   └── env.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   └── roadmap.md
├── pyproject.toml
├── Makefile
├── .pre-commit-config.yaml
├── .env.example
└── README.md
```

---

## Componentes principales

### 1. FastAPI Backend

**Rol:** Núcleo del sistema.

Responsabilidades:

- Exponer APIs REST versionables.
- Validar datos de entrada con Pydantic.
- Orquestar procesos de ingestión.
- Aplicar reglas de negocio.
- Servir como punto único de acceso a los datos.

FastAPI se utiliza como **servicio de datos**, no como frontend.

---

### 2. Repository Pattern

**Rol:** Abstracción de acceso a datos.

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar("T")

class Repository(Protocol[T]):
    def get_by_id(self, id: int) -> T | None: ...
    def get_all(self) -> list[T]: ...
    def create(self, entity: T) -> T: ...
    def update(self, entity: T) -> T: ...
    def delete(self, id: int) -> None: ...
```

Beneficios:

- Testabilidad (mocks fáciles).
- Dependency Inversion.
- Cambio de persistencia sin afectar servicios.

---

### 3. Services Layer

**Rol:** Lógica de negocio.

- Orquesta operaciones entre repositorios.
- Aplica validaciones de dominio.
- Independiente de la capa de transporte (API).

---

### 4. Modelos y Persistencia (SQLAlchemy + Alembic)

**Rol:** Definición del dominio y control del esquema.

- SQLAlchemy para modelos con ORM maduro y flexible.
- Pydantic para schemas de validación (separados de modelos).
- Alembic para migraciones versionadas.
- Permite coherencia, mantenibilidad y evolución controlada.

---

### 5. Base de Datos (PostgreSQL / TimescaleDB)

**Rol:** Almacenamiento persistente de series temporales.

Características:

- Almacenamiento histórico de precios.
- Índices temporales optimizados (hypertables).
- Integridad referencial.
- Preparada para consultas analíticas.

La base de datos es la **fuente única de verdad**.

---

### 6. Ingestión de Datos (ETL)

**Rol:** Entrada de datos al sistema.

Flujo:

1. Consumo de APIs externas (clientes especializados).
2. Normalización de formatos (transformers).
3. Validación de datos.
4. Inserción idempotente en BD.

La lógica ETL reside en el backend, desacoplada de la visualización.

---

### 7. API REST

**Rol:** Interfaz de acceso a los datos.

Características:

- Endpoints versionables (`/api/v1/`).
- Contratos claros mediante OpenAPI.
- Paginación y filtros.
- Manejo de errores consistente.

---

### 8. Grafana

**Rol:** Visualización y análisis.

- Lectura directa de la base de datos.
- Dashboards y KPIs.
- Análisis de series temporales.

Grafana **no contiene lógica de negocio** ni ingestión.

---

### 9. Docker & Docker Compose

**Rol:** Infraestructura local reproducible.

- Aislamiento de servicios.
- Configuración declarativa.
- Arranque unificado del sistema.
- Health checks.

---

## Testing Strategy

### Pirámide de tests

```
        ╱╲
       ╱  ╲       E2E (pocos)
      ╱────╲
     ╱      ╲     Integración
    ╱────────╲
   ╱          ╲   Unitarios (muchos)
  ╱────────────╲
```

### Tipos de tests

| Tipo            | Scope             | Herramientas          |
| --------------- | ----------------- | --------------------- |
| **Unitarios**   | Funciones, clases | pytest, mocks         |
| **Integración** | API + DB          | httpx, testcontainers |
| **E2E**         | Sistema completo  | Docker Compose        |

### Cobertura objetivo

- Mínimo 80% de cobertura.
- 100% en lógica crítica de negocio.

---

## Flujo de datos

```
APIs externas
     │
     ▼
ETL / Jobs (FastAPI)
     │
     ▼
Base de Datos (PostgreSQL / TimescaleDB)
     │
     ├──► API REST (FastAPI) ──► Clientes
     │
     └──► Grafana Dashboards
```

---

## Configuración

### Gestión con pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Database
    database_url: str

    # API
    api_prefix: str = "/api/v1"
    debug: bool = False

    # External APIs
    alpha_vantage_api_key: str | None = None
```

### Variables de entorno

Todas las configuraciones sensibles se gestionan mediante `.env` (no versionado) y `.env.example` (versionado como documentación).

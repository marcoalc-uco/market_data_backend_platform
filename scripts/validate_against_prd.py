#!/usr/bin/env python3
"""Validate implementation against PRD.md requirements.

This script verifies that the codebase structure and key components
align with the architectural contract defined in /docs/PRD.md.

Usage:
    python scripts/validate_against_prd.py

Exit Codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import sys
from pathlib import Path
from typing import NamedTuple


class ValidationResult(NamedTuple):
    """Result of a validation check."""

    name: str
    passed: bool
    message: str


def validate_project_structure() -> ValidationResult:
    """Verify canonical project structure exists.

    Returns:
        ValidationResult: Result of structure validation.
    """
    required_dirs = [
        "src/market_data_backend_platform",
        "src/market_data_backend_platform/api",
        "src/market_data_backend_platform/api/routes",
        "src/market_data_backend_platform/core",
        "src/market_data_backend_platform/models",
        "src/market_data_backend_platform/schemas",
        "src/market_data_backend_platform/repositories",
        "src/market_data_backend_platform/services",
        "src/market_data_backend_platform/etl",
        "src/market_data_backend_platform/db",
        "tests",
        "docs",
        "alembic",
    ]

    root = Path(__file__).parent.parent
    missing = [d for d in required_dirs if not (root / d).exists()]

    if missing:
        return ValidationResult(
            name="Project Structure",
            passed=False,
            message=f"Missing directories: {', '.join(missing)}",
        )

    return ValidationResult(
        name="Project Structure",
        passed=True,
        message="All required directories exist",
    )


def validate_core_models() -> ValidationResult:
    """Verify core domain models exist.

    Returns:
        ValidationResult: Result of models validation.
    """
    root = Path(__file__).parent.parent
    required_models = [
        "src/market_data_backend_platform/models/instrument.py",
        "src/market_data_backend_platform/models/market_price.py",
    ]

    missing = [m for m in required_models if not (root / m).exists()]

    if missing:
        return ValidationResult(
            name="Core Models",
            passed=False,
            message=f"Missing models: {', '.join(missing)}",
        )

    return ValidationResult(
        name="Core Models",
        passed=True,
        message="All core models exist",
    )


def validate_api_endpoints() -> ValidationResult:
    """Verify required API endpoints exist.

    Returns:
        ValidationResult: Result of API endpoints validation.
    """
    root = Path(__file__).parent.parent
    required_routes = [
        "src/market_data_backend_platform/api/routes/health.py",
        "src/market_data_backend_platform/api/routes/instruments.py",
        "src/market_data_backend_platform/api/routes/prices.py",
    ]

    missing = [r for r in required_routes if not (root / r).exists()]

    if missing:
        return ValidationResult(
            name="API Endpoints",
            passed=False,
            message=f"Missing routes: {', '.join(missing)}",
        )

    return ValidationResult(
        name="API Endpoints",
        passed=True,
        message="All required endpoints exist",
    )


def validate_documentation() -> ValidationResult:
    """Verify required documentation exists.

    Returns:
        ValidationResult: Result of documentation validation.
    """
    root = Path(__file__).parent.parent
    required_docs = [
        "docs/PRD.md",
        "docs/DEV_PLAN.md",
        "docs/QA_PROTOCOL.md",
        "docs/architecture.md",
        "docs/roadmap.md",
        "AGENT.md",
    ]

    missing = [d for d in required_docs if not (root / d).exists()]

    if missing:
        return ValidationResult(
            name="Documentation",
            passed=False,
            message=f"Missing docs: {', '.join(missing)}",
        )

    return ValidationResult(
        name="Documentation",
        passed=True,
        message="All required documentation exists",
    )


def main() -> int:
    """Run all PRD validations.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("🔍 Validating against PRD.md...\n")

    validations = [
        validate_project_structure(),
        validate_core_models(),
        validate_api_endpoints(),
        validate_documentation(),
    ]

    all_passed = True
    for result in validations:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.name}: {result.message}")
        if not result.passed:
            all_passed = False

    print()
    if all_passed:
        print("✅ All PRD validations PASSED")
        return 0
    else:
        print("❌ Some PRD validations FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

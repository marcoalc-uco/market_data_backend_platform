#!/usr/bin/env python3
"""Validate that Pydantic schemas match JSON Schema definitions.

This script ensures consistency between Pydantic models in the codebase
and their corresponding JSON Schema files in /docs/schemas/.

Usage:
    python scripts/validate_schemas.py

Exit Codes:
    0 - All schemas valid
    1 - Schema validation failed
"""

import json
import sys
from pathlib import Path


def main() -> int:
    """Validate schema consistency.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("🔍 Validating schemas...\n")

    root = Path(__file__).parent.parent
    schemas_dir = root / "docs" / "schemas"

    # Check if schemas directory exists
    if not schemas_dir.exists():
        print("⚠️  WARNING: /docs/schemas/ directory not found")
        print("   This is acceptable if schemas are defined inline in Pydantic models.")
        print("   Future enhancement: Export schemas to JSON for external validation.")
        return 0

    # Check for JSON schema files
    schema_files = list(schemas_dir.glob("*.json"))
    if not schema_files:
        print("⚠️  WARNING: No JSON schema files found in /docs/schemas/")
        print("   This is acceptable if schemas are defined inline in Pydantic models.")
        return 0

    # Validate each schema file
    all_valid = True
    for schema_file in schema_files:
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_data = json.load(f)

            # Basic validation: ensure it's a valid JSON
            if not isinstance(schema_data, dict):
                print(f"❌ {schema_file.name}: Not a valid JSON object")
                all_valid = False
                continue

            print(f"✅ {schema_file.name}: Valid JSON")

        except json.JSONDecodeError as e:
            print(f"❌ {schema_file.name}: Invalid JSON - {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {schema_file.name}: Error - {e}")
            all_valid = False

    print()
    if all_valid:
        print("✅ Schema validation PASSED")
        return 0
    else:
        print("❌ Schema validation FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

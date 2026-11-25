"""Product catalog loader and validator for HiveSpace Coworking."""

import json
from pathlib import Path
from typing import Any

REQUIRED_PRODUCT_FIELDS = {
    "id": str,
    "name": str,
    "type": str,
    "short_description": str,
    "price": (int, float),
    "billing_unit": str,
    "capacity": int,
    "amenities": list,
}

ALLOWED_TYPES = {
    "day_pass",
    "dedicated_desk",
    "meeting_room",
    "private_office",
    "event_space",
    "addon",
}


class CatalogValidationError(ValueError):
    """Raised when the HiveSpace product catalog or query input is invalid."""


def validate_product(item: Any, index: int) -> dict[str, Any]:
    """Validate a single coworking product dictionary."""
    if not isinstance(item, dict):
        raise CatalogValidationError(
            f"Product at index {index} must be a JSON object, got {type(item).__name__}."
        )

    for field, expected_type in REQUIRED_PRODUCT_FIELDS.items():
        if field not in item:
            raise CatalogValidationError(
                f"Product at index {index} is missing required field '{field}'."
            )
        value = item[field]
        # bool is a subclass of int in Python; reject booleans for numeric fields
        if isinstance(value, bool) or not isinstance(value, expected_type):
            raise CatalogValidationError(
                f"Field '{field}' in product '{item.get('id', index)}' has invalid type."
            )

    if not item["id"].strip() or not item["name"].strip() or not item["short_description"].strip():
        raise CatalogValidationError(
            f"Product '{item.get('id', index)}' cannot have empty id, name, or short_description."
        )

    if item["type"] not in ALLOWED_TYPES:
        raise CatalogValidationError(
            f"Product '{item['id']}' has unsupported type '{item['type']}'."
        )

    if item["price"] <= 0:
        raise CatalogValidationError(
            f"Product '{item['id']}' must have a price greater than 0."
        )

    if item["capacity"] < 1:
        raise CatalogValidationError(
            f"Product '{item['id']}' must have capacity of at least 1."
        )

    if not all(isinstance(tag, str) and tag.strip() for tag in item["amenities"]):
        raise CatalogValidationError(
            f"Product '{item['id']}' amenities must be non-empty strings."
        )

    return item


def load_catalog(file_path: str | Path = "data/products.json") -> dict[str, Any]:
    """Load and validate the HiveSpace Coworking catalog from disk."""
    path = Path(file_path)
    if not path.exists():
        raise CatalogValidationError(f"Catalog file not found: {path}")

    raw_text = path.read_text(encoding="utf-8").strip()
    if not raw_text:
        raise CatalogValidationError(f"Catalog file is empty: {path}")

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise CatalogValidationError(f"Invalid JSON in catalog file: {exc.msg}") from exc

    if not isinstance(data, dict) or "products" not in data:
        raise CatalogValidationError("Catalog JSON must be an object containing a 'products' list.")

    products = data["products"]
    if not isinstance(products, list) or len(products) == 0:
        raise CatalogValidationError("Catalog 'products' must be a non-empty list.")

    seen_ids: set[str] = set()
    validated_products: list[dict[str, Any]] = []
    for idx, product in enumerate(products):
        clean_item = validate_product(product, idx)
        if clean_item["id"] in seen_ids:
            raise CatalogValidationError(f"Duplicate product ID found: '{clean_item['id']}'.")
        seen_ids.add(clean_item["id"])
        validated_products.append(clean_item)

    return {
        "space_name": data.get("space_name", "HiveSpace Coworking"),
        "currency": data.get("currency", "PKR"),
        "products": validated_products,
    }


def filter_products(
    products: list[dict[str, Any]],
    query: str,
    product_type: str | None = None,
) -> list[dict[str, Any]]:
    """Baseline keyword filter with safe handling for empty or invalid queries."""
    if not isinstance(query, str) or not query.strip():
        raise CatalogValidationError("Search query cannot be empty. Please enter what you need.")

    if product_type is not None and product_type not in ALLOWED_TYPES:
        raise CatalogValidationError(
            f"Invalid product type '{product_type}'. Choose from: {', '.join(sorted(ALLOWED_TYPES))}."
        )

    term = query.strip().lower()
    results = []
    for item in products:
        if product_type and item["type"] != product_type:
            continue
        searchable = " ".join(
            [item["name"], item["short_description"], " ".join(item["amenities"])]
        ).lower()
        if term in searchable:
            results.append(item)
    return results


def main() -> None:
    try:
        catalog = load_catalog()
    except CatalogValidationError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1) from exc

    products = catalog["products"]
    print(f"Loaded {len(products)} valid products for {catalog['space_name']} ({catalog['currency']}).")
    for item in products:
        print(
            f"- {item['id']} | {item['name']} ({item['type']}) "
            f"- {catalog['currency']} {item['price']:,.0f} {item['billing_unit']} | cap: {item['capacity']}"
        )


if __name__ == "__main__":
    main()
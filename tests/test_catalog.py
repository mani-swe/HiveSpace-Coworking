"""Tests for HiveSpace Coworking catalog loading, validation, and filtering."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.catalog import CatalogValidationError, filter_products, load_catalog


class TestHiveSpaceCatalog(unittest.TestCase):
    def test_load_real_catalog_main_path(self) -> None:
        """Main path: loads and validates the real HiveSpace PKR dataset."""
        catalog = load_catalog("data/products.json")
        self.assertEqual(catalog["space_name"], "HiveSpace Coworking")
        self.assertEqual(catalog["currency"], "PKR")
        self.assertEqual(len(catalog["products"]), 15)

        ids = [item["id"] for item in catalog["products"]]
        self.assertIn("HS-001", ids)
        self.assertIn("HS-015", ids)

    def test_filter_products_main_path(self) -> None:
        """Main path: filters products by query and optional product type."""
        catalog = load_catalog("data/products.json")
        matches = filter_products(catalog["products"], "chai", product_type="addon")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["id"], "HS-015")

    def test_empty_file_failure_path(self) -> None:
        """Failure path: empty catalog file raises a clear CatalogValidationError."""
        with TemporaryDirectory() as tmp_dir:
            empty_file = Path(tmp_dir) / "empty.json"
            empty_file.write_text("", encoding="utf-8")

            with self.assertRaises(CatalogValidationError) as ctx:
                load_catalog(empty_file)

            self.assertIn("empty", str(ctx.exception).lower())

    def test_invalid_price_and_empty_query_failure_path(self) -> None:
        """Failure path: negative price and empty search query raise clear errors."""
        with TemporaryDirectory() as tmp_dir:
            bad_file = Path(tmp_dir) / "bad_products.json"
            payload = {
                "space_name": "HiveSpace Coworking",
                "currency": "PKR",
                "products": [
                    {
                        "id": "HS-999",
                        "name": "Broken Pass",
                        "type": "day_pass",
                        "short_description": "Invalid negative price for test.",
                        "price": -500,
                        "billing_unit": "per_day",
                        "capacity": 1,
                        "amenities": ["fiber_wifi"],
                    }
                ],
            }
            bad_file.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(CatalogValidationError) as ctx:
                load_catalog(bad_file)

            self.assertIn("greater than 0", str(ctx.exception))

        with self.assertRaises(CatalogValidationError) as query_ctx:
            filter_products([], "   ")

        self.assertIn("empty", str(query_ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
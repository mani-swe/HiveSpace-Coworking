"""Tests for HiveSpace Coworking embedding text construction and vector generation."""

import unittest

from src.catalog import CatalogValidationError, load_catalog
from src.embeddings import (
    build_embedding_text,
    build_embeddings_by_id,
    embed_texts,
)


class _FakeSentenceTransformer:
    """Lightweight mock model for fast, deterministic unit tests."""

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def encode(self, texts: list[str], normalize_embeddings: bool = True) -> list[list[float]]:
        vectors: list[list[float]] = []
        for idx, _text in enumerate(texts):
            row = [0.0] * self.dim
            row[idx % self.dim] = 1.0
            vectors.append(row)
        return vectors


class TestHiveSpaceEmbeddings(unittest.TestCase):
    def test_build_embeddings_by_id_main_path(self) -> None:
        """Main path: builds embedding text and 384-dim vectors keyed by product ID."""
        catalog = load_catalog("data/products.json")
        fake_model = _FakeSentenceTransformer(dim=384)

        vectors_by_id = build_embeddings_by_id(catalog["products"], model=fake_model)

        self.assertEqual(len(vectors_by_id), 15)
        self.assertIn("HS-001", vectors_by_id)
        self.assertIn("HS-015", vectors_by_id)

        hs_001 = vectors_by_id["HS-001"]
        self.assertEqual(len(hs_001["embedding"]), 384)
        self.assertIn("Hot Desk Day Pass", hs_001["embedding_text"])
        self.assertNotIn("HS-001", hs_001["embedding_text"])

    def test_build_embedding_text_main_path(self) -> None:
        """Main path: formats product fields into readable semantic text."""
        product = {
            "id": "HS-006",
            "name": "Huddle Room (4 People)",
            "type": "meeting_room",
            "short_description": "Compact glass-walled meeting room for up to 4 people.",
            "price": 2500.0,
            "billing_unit": "per_hour",
            "capacity": 4,
            "amenities": ["4k_display", "whiteboard"],
        }
        text = build_embedding_text(product)
        self.assertIn("Huddle Room (4 People)", text)
        self.assertIn("4 people", text)
        self.assertIn("4k display, whiteboard", text)

    def test_empty_text_failure_path(self) -> None:
        """Failure path: empty string input raises a clear CatalogValidationError."""
        fake_model = _FakeSentenceTransformer(dim=384)

        with self.assertRaises(CatalogValidationError) as ctx:
            embed_texts(["   "], model=fake_model)

        self.assertIn("empty", str(ctx.exception).lower())

    def test_invalid_product_and_empty_list_failure_path(self) -> None:
        """Failure path: missing description and empty product list raise clear errors."""
        fake_model = _FakeSentenceTransformer(dim=384)

        bad_product = {
            "id": "HS-999",
            "name": "Incomplete Room",
            "type": "meeting_room",
            "short_description": "   ",
            "price": 1000.0,
            "billing_unit": "per_hour",
            "capacity": 2,
            "amenities": ["projector"],
        }
        with self.assertRaises(CatalogValidationError) as prod_ctx:
            build_embedding_text(bad_product)

        self.assertIn("short_description", str(prod_ctx.exception))

        with self.assertRaises(CatalogValidationError) as list_ctx:
            build_embeddings_by_id([], model=fake_model)

        self.assertIn("empty", str(list_ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
"""Semantic embedding builder for HiveSpace Coworking using sentence-transformers."""

import json
from pathlib import Path
from typing import Any

from src.catalog import CatalogValidationError, load_catalog

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


def build_embedding_text(product: dict[str, Any]) -> str:
    """Build a semantic text representation from a validated coworking product."""
    if not isinstance(product, dict):
        raise CatalogValidationError(
            f"Product must be a dictionary to build embedding text, got {type(product).__name__}."
        )

    name = product.get("name")
    short_description = product.get("short_description")
    product_type = product.get("type")
    capacity = product.get("capacity")
    billing_unit = product.get("billing_unit")
    amenities = product.get("amenities")

    if not isinstance(name, str) or not name.strip():
        raise CatalogValidationError("Cannot build embedding text: product 'name' is missing or empty.")
    if not isinstance(short_description, str) or not short_description.strip():
        raise CatalogValidationError(
            f"Cannot build embedding text for '{name}': 'short_description' is missing or empty."
        )
    if not isinstance(product_type, str) or not product_type.strip():
        raise CatalogValidationError(
            f"Cannot build embedding text for '{name}': 'type' is missing or empty."
        )
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
        raise CatalogValidationError(
            f"Cannot build embedding text for '{name}': 'capacity' must be an integer >= 1."
        )
    if not isinstance(billing_unit, str) or not billing_unit.strip():
        raise CatalogValidationError(
            f"Cannot build embedding text for '{name}': 'billing_unit' is missing or empty."
        )
    if not isinstance(amenities, list) or not all(isinstance(a, str) and a.strip() for a in amenities):
        raise CatalogValidationError(
            f"Cannot build embedding text for '{name}': 'amenities' must be a non-empty list of strings."
        )

    people_label = "person" if capacity == 1 else "people"
    formatted_type = product_type.replace("_", " ").strip()
    formatted_billing = billing_unit.replace("_", " ").strip()
    formatted_amenities = ", ".join(a.replace("_", " ").strip() for a in amenities)

    return (
        f"Offering: {name.strip()}. "
        f"Category: {formatted_type}. "
        f"Capacity: {capacity} {people_label}. "
        f"Billing: {formatted_billing}. "
        f"Amenities: {formatted_amenities}. "
        f"Details: {short_description.strip()}"
    )


def load_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> Any:
    """Load a SentenceTransformer model with a clear error if unavailable."""
    if not isinstance(model_name, str) or not model_name.strip():
        raise CatalogValidationError("Embedding model name cannot be empty.")

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise CatalogValidationError(
            "Missing dependency 'sentence-transformers'. Install it with: pip install sentence-transformers"
        ) from exc

    try:
        return SentenceTransformer(model_name.strip())
    except Exception as exc:
        raise CatalogValidationError(
            f"Failed to load SentenceTransformer model '{model_name}': {exc}"
        ) from exc


def embed_texts(
    texts: list[str],
    model: Any = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[list[float]]:
    """Compute normalized semantic embeddings for a non-empty list of non-empty strings."""
    if not isinstance(texts, list) or len(texts) == 0:
        raise CatalogValidationError("Texts list cannot be empty when generating embeddings.")

    cleaned_texts: list[str] = []
    for idx, text in enumerate(texts):
        if not isinstance(text, str) or not text.strip():
            raise CatalogValidationError(
                f"Cannot embed empty or non-string text at index {idx}."
            )
        cleaned_texts.append(text.strip())

    active_model = model if model is not None else load_embedding_model(model_name)

    try:
        vectors = active_model.encode(cleaned_texts, normalize_embeddings=True)
    except CatalogValidationError:
        raise
    except Exception as exc:
        raise CatalogValidationError(f"Error while encoding texts into embeddings: {exc}") from exc

    if hasattr(vectors, "tolist"):
        vectors_list = vectors.tolist()
    else:
        vectors_list = list(vectors)

    if len(vectors_list) != len(cleaned_texts):
        raise CatalogValidationError("Embedding count mismatch with input texts.")

    return [[round(float(val), 6) for val in row] for row in vectors_list]


def build_embeddings_by_id(
    products: list[dict[str, Any]],
    model: Any = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> dict[str, dict[str, Any]]:
    """Build embeddings keyed by product ID so catalog data stays separate."""
    if not isinstance(products, list) or len(products) == 0:
        raise CatalogValidationError("Products list cannot be empty when building embeddings.")

    product_ids: list[str] = []
    embedding_texts: list[str] = []

    for product in products:
        pid = product.get("id") if isinstance(product, dict) else None
        if not isinstance(pid, str) or not pid.strip():
            raise CatalogValidationError("Each product must have a non-empty string 'id'.")
        clean_id = pid.strip()
        if clean_id in product_ids:
            raise CatalogValidationError(f"Duplicate product ID '{clean_id}' encountered.")
        product_ids.append(clean_id)
        embedding_texts.append(build_embedding_text(product))

    vectors = embed_texts(embedding_texts, model=model, model_name=model_name)

    vectors_by_id: dict[str, dict[str, Any]] = {}
    for pid, text, vec in zip(product_ids, embedding_texts, vectors):
        vectors_by_id[pid] = {
            "embedding_text": text,
            "embedding": vec,
        }

    return vectors_by_id


def save_embeddings_by_id(
    vectors_by_id: dict[str, dict[str, Any]],
    output_path: str | Path = "data/embeddings.json",
    model_name: str = DEFAULT_MODEL_NAME,
) -> Path:
    """Save product embeddings keyed by product ID to a separate JSON file."""
    if not isinstance(vectors_by_id, dict) or len(vectors_by_id) == 0:
        raise CatalogValidationError("Cannot save empty embeddings dictionary.")

    first_entry = next(iter(vectors_by_id.values()))
    dim = len(first_entry.get("embedding", []))

    path = Path(output_path)
    payload = {
        "space_name": "HiveSpace Coworking",
        "currency": "PKR",
        "model_name": model_name,
        "embedding_dim": dim,
        "count": len(vectors_by_id),
        "vectors_by_id": vectors_by_id,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> None:
    try:
        catalog = load_catalog("data/products.json")
        vectors_by_id = build_embeddings_by_id(
            catalog["products"], model_name=DEFAULT_MODEL_NAME
        )
        saved_path = save_embeddings_by_id(
            vectors_by_id,
            output_path="data/embeddings.json",
            model_name=DEFAULT_MODEL_NAME,
        )
    except CatalogValidationError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1) from exc

    sample_id = next(iter(vectors_by_id))
    sample = vectors_by_id[sample_id]
    print(
        f"Generated and saved {len(vectors_by_id)} embeddings "
        f"(model={DEFAULT_MODEL_NAME}, dim={len(sample['embedding'])}) to {saved_path}."
    )
    print(f"Keyed sample ({sample_id}): {sample['embedding_text']}")
    print(f"Vector preview: {sample['embedding'][:6]}...")


if __name__ == "__main__":
    main()
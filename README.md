# HiveSpace Coworking — Product Data & Semantic Search Foundation

A structured product catalog and validation foundation developed for **HiveSpace Coworking** (a modern coworking space). This milestone (**Task 1: Product Data**) establishes a realistic, PKR-priced coworking product dataset (`data/products.json`), enforces strict schema and input validation (`src/catalog.py`), provides a baseline keyword/category filter, and verifies main and failure paths through automated unit tests (`tests/test_catalog.py`) so downstream semantic search modules can build reliably on clean data.

---

## 🚀 Features

- **Realistic HiveSpace Product Dataset (`data/products.json`):** Contains 15 realistic coworking offerings priced in **PKR** across six operational categories (`day_pass`, `dedicated_desk`, `meeting_room`, `private_office`, `event_space`, and `addon`), complete with search-ready natural-language descriptions, capacities, billing units, and structured amenity tags.
- **Schema & Value Catalog Validator (`src/catalog.py`):** Validates catalog files for existence, non-empty JSON structure, required fields (`id`, `name`, `type`, `short_description`, `price`, `billing_unit`, `capacity`, `amenities`), strict data types (rejecting boolean-as-int edge cases), duplicate IDs, positive pricing, and valid capacities.
- **Safe Error Handling & Query Guardrails (`CatalogValidationError`):** Catches missing files, empty/malformed JSON, negative prices, unsupported product types, and blank search queries with clear, actionable error messages instead of unhandled crashes.
- **Baseline Keyword & Category Filter (`filter_products`):** Provides deterministic filtering by query string and optional `product_type` across product names, descriptions, and amenity tags as a verified baseline ahead of vector-based semantic ranking.
- **Automated Unit Test Suite (`tests/test_catalog.py`):** Covers both happy paths (loading the 15-item HiveSpace catalog and filtering add-ons) and failure paths (empty files, negative prices, and blank queries) using Python's built-in `unittest` framework.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+ (tested on Python 3.14)
- **Standard Library Modules:** `json`, `pathlib`, `typing`, `unittest`, `tempfile`
- **Data Storage Format:** Structured UTF-8 JSON (`data/products.json`)
- **External Dependencies:** None (zero third-party packages required for Task 1)

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

---

## 📥 Installation & Setup Instructions

Follow these instructions and run these commands step-by-step in your VS Code terminal to get the project running locally:

### 1. Clone the Repository

```bash
git clone https://github.com/mani-swe/HiveSpace-Coworking.git
cd HiveSpace-Coworking
```

### 2. Setup a Virtual Environment (Optional)

Because Task 1 uses only the Python Standard Library, no external packages are needed, though creating a virtual environment keeps future semantic search tasks isolated:

- **On Windows:**

  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

- **On macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

---

## 📚 Catalog Schema & Product Categories

Every item in `data/products.json` follows a strict schema tailored for downstream semantic retrieval:

| Field               | Type           | Description                                                      | Example                                  |
| :------------------ | :------------- | :--------------------------------------------------------------- | :--------------------------------------- |
| `id`                | `str`          | Unique product identifier                                        | `"HS-001"`                               |
| `name`              | `str`          | Customer-facing offering title                                   | `"Hot Desk Day Pass"`                    |
| `type`              | `str`          | Allowed coworking category                                       | `"day_pass"`                             |
| `short_description` | `str`          | Natural-language summary for semantic matching                   | `"Flexible open-seating workstation..."` |
| `price`             | `int \| float` | Positive rate in `PKR`                                           | `1500.0`                                 |
| `billing_unit`      | `str`          | Pricing cadence (`per_hour`, `per_day`, `per_month`, `per_pack`) | `"per_day"`                              |
| `capacity`          | `int`          | Seating/user capacity (`>= 1`)                                   | `1`                                      |
| `amenities`         | `list[str]`    | Structured feature tags                                          | `["fiber_wifi", "power_backup"]`         |

### Included Categories (`ALLOWED_TYPES`)

1. **`day_pass`** — Hot Desk Day Pass, Quiet Focus Zone Day Pass
2. **`dedicated_desk`** — Dedicated Desk Monthly, Dual-Monitor Creator Desk
3. **`meeting_room`** — Acoustic Call Booth Pass, Huddle Room (4 People), Strategy Boardroom (10 People)
4. **`private_office`** — Startup Private Office (4 People), Growth Team Suite (8 People), Executive Corner Office (6 People)
5. **`event_space`** — Workshop & Seminar Hall (30 People)
6. **`addon`** — Smart Gear Locker Monthly, High-Speed Print & Scan Pack (250 Pages), Virtual Office & Business Address, Pantry Pass (Monthly)

---

## 🚀 How to Run & Check

Run all commands from the project root directory (`HiveSpace-Coworking/`):

### 1. Load & Validate the Product Catalog (CLI)

```bash
python -m src.catalog
```

**Expected Output:**

- Confirms `Loaded 15 valid products for HiveSpace Coworking (PKR).` and prints a formatted summary of `HS-001` through `HS-015` with categories, PKR prices, billing units, and capacities.
- If `data/products.json` is missing, empty, or invalid, prints `[ERROR] <clear reason>` and exits cleanly with status code `1`.

### 2. Run the Unit Test Suite

```bash
python -m tests.test_catalog
```

_(Or with verbose discovery output:)_

```bash
python -m unittest discover -s tests -v
```

**Expected Output:**

- Executes 4 tests (`test_load_real_catalog_main_path`, `test_filter_products_main_path`, `test_empty_file_failure_path`, `test_invalid_price_and_empty_query_failure_path`) and reports `Ran 4 tests ... OK`.

---

## 🧠 Architecture Decision & Trade-off

- **Decision:** Store the product catalog as structured JSON (`data/products.json`) validated in Python (`src/catalog.py`), and model shared refreshments (`HS-015` — _Pantry Pass (Monthly)_) as a standalone `addon` rather than duplicating chai/coffee perks inside every base pass description.
- **Trade-off:** Unlike a flat CSV, JSON supports nested `amenities` lists and rich multi-sentence `short_description` text without delimiter escaping issues, and separating the Pantry Pass prevents semantic overlap across unrelated desk plans during future embedding search. The trade-off is that non-technical staff cannot edit JSON directly in a spreadsheet as easily as a CSV and must rely on `src/catalog.py` to catch syntax or schema mistakes.

---

## 📋 Task 1 Summary

- **What Was Built:** A 15-item PKR-priced HiveSpace Coworking product dataset (`data/products.json`), strict catalog and query validator (`src/catalog.py`), baseline keyword/type filter, unit tests covering main and failure paths (`tests/test_catalog.py`), and complete run/check documentation.
- **Current Scope Boundaries:** Embedding generation, vector indexing, and semantic similarity ranking are intentionally excluded from Task 1 and will build directly on `load_catalog()` in upcoming tasks.

---

## 📁 Project Structure

```text
HiveSpace-Coworking/
├── README.md                  # Project documentation, run steps & design trade-off
├── data/
│   └── products.json          # 15 realistic HiveSpace Coworking offerings (PKR)
├── src/
│   ├── __init__.py
│   └── catalog.py             # Catalog loader, schema validator & baseline filter
└── tests/
    ├── __init__.py
    └── test_catalog.py        # Main-path & failure-path unit tests
```

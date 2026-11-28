# ꙮ HiveSpace Coworking — Product Data & Semantic Search Foundation

A structured product catalog and semantic embedding pipeline developed for **HiveSpace Coworking** (a modern coworking space). Across **Task 1 (Product Data)** and **Task 2 (Embeddings)**, this repository establishes a realistic, PKR-priced coworking product dataset (`data/products.json`), enforces strict schema and input validation (`src/catalog.py`), generates normalized `384`-dimensional `sentence-transformers` vectors stored in a separate file keyed by product ID (`data/embeddings.json`), and verifies main and failure paths through automated unit tests (`tests/test_catalog.py` and `tests/test_embeddings.py`).

---

## 🚀 Features

- **Realistic HiveSpace Product Dataset (`data/products.json`):** Contains 15 realistic coworking offerings priced in **PKR** across six operational categories (`day_pass`, `dedicated_desk`, `meeting_room`, `private_office`, `event_space`, and `addon`), complete with search-ready natural-language descriptions, capacities, billing units, and structured amenity tags.
- **Schema & Value Catalog Validator (`src/catalog.py`):** Validates catalog files for existence, non-empty JSON structure, required fields (`id`, `name`, `type`, `short_description`, `price`, `billing_unit`, `capacity`, `amenities`), strict data types (rejecting boolean-as-int edge cases), duplicate IDs, positive pricing, and valid capacities.
- **Semantic Embedding Builder (`src/embeddings.py`):** Constructs clean semantic text representations from validated coworking items and generates L2-normalized `384`-dimensional vectors using `sentence-transformers` (`all-MiniLM-L6-v2`), saving them separately in `data/embeddings.json` keyed by product ID (`HS-001` through `HS-015`).
- **Safe Error Handling & Query Guardrails (`CatalogValidationError`):** Catches missing files, empty/malformed JSON, negative prices, unsupported product types, blank embedding inputs, and empty search queries with clear, actionable error messages instead of unhandled crashes.
- **Baseline Keyword & Category Filter (`filter_products`):** Provides deterministic filtering by query string and optional `product_type` across product names, descriptions, and amenity tags as a verified baseline ahead of hybrid semantic ranking.
- **Automated Unit Test Suites (`tests/test_catalog.py`, `tests/test_embeddings.py`):** Covers both happy paths (loading the 15-item HiveSpace catalog, filtering add-ons, building embedding text and 384-dim ID-keyed vectors) and failure paths (empty files, negative prices, blank embedding strings, and invalid product records) using Python's built-in `unittest` framework.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+ (tested on Python 3.14)
- **Embedding Model & Library:** `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dimensional normalized embeddings)
- **Standard Library Modules:** `json`, `pathlib`, `typing`, `unittest`, `tempfile`
- **Data Storage Format:** Structured UTF-8 JSON (`data/products.json` & `data/embeddings.json`)

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

### 2. Setup a Virtual Environment

- **On Windows (PowerShell):**

  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

- **On macOS/Linux:**

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install sentence-transformers
```

---

## 📚 Catalog Schema & Product Categories

Every item in `data/products.json` follows a strict schema tailored for downstream semantic retrieval:

| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `id` | `str` | Unique product identifier | `"HS-001"` |
| `name` | `str` | Customer-facing offering title | `"Hot Desk Day Pass"` |
| `type` | `str` | Allowed coworking category | `"day_pass"` |
| `short_description` | `str` | Natural-language summary for semantic matching | `"Flexible open-seating workstation..."` |
| `price` | `int \| float` | Positive rate in `PKR` | `1500.0` |
| `billing_unit` | `str` | Pricing cadence (`per_hour`, `per_day`, `per_month`, `per_pack`) | `"per_day"` |
| `capacity` | `int` | Seating/user capacity (`>= 1`) | `1` |
| `amenities` | `list[str]` | Structured feature tags | `["fiber_wifi", "power_backup"]` |

### Included Categories (`ALLOWED_TYPES`)

1. **`day_pass`** — Hot Desk Day Pass, Quiet Focus Zone Day Pass
2. **`dedicated_desk`** — Dedicated Desk Monthly, Dual-Monitor Creator Desk
3. **`meeting_room`** — Acoustic Call Booth Pass, Huddle Room (4 People), Strategy Boardroom (10 People)
4. **`private_office`** — Startup Private Office (4 People), Growth Team Suite (8 People), Executive Corner Office (6 People)
5. **`event_space`** — Workshop & Seminar Hall (30 People)
6. **`addon`** — Smart Gear Locker Monthly, High-Speed Print & Scan Pack (250 Pages), Virtual Office & Business Address, Pantry Pass (Monthly)

---

## 🧩 Embedding Input Construction

Before generating vector embeddings from `data/products.json` (`HS-001` through `HS-015`), each coworking product is converted into a single structured text string representing what a member searches for semantically:

### Included in Embedding Text (Semantic Meaning)
- **`name`** — Product title (e.g., *Quiet Focus Zone Day Pass*, *Strategy Boardroom (10 People)*, *Pantry Pass (Monthly)*).
- **`short_description`** — Natural-language description of how the space or add-on is used (quiet focus, team meetings, client calls, monthly desk, or pantry perks).
- **`amenities`** — Feature tags formatted cleanly (e.g., `fiber_wifi`, `quiet_zone`, `projector`, `soundproof`, `unlimited_chai`).
- **`type` & Contextual Cadence/Capacity** — Category context (`day_pass`, `dedicated_desk`, `meeting_room`, `private_office`, `event_space`, `addon`) along with human-readable capacity and billing cadence (e.g., `4 people`, `per_hour` or `per_month`) so queries like *"meeting room for 4"* or *"monthly pass"* align naturally with product intent.

### Excluded from Embedding Text (Metadata & Non-Semantic Identifiers)
- **`id`** (`HS-001`, etc.) — Internal identifier with no semantic meaning for natural-language queries.
- **Raw `price` (`PKR` numeric value)** — Kept as metadata/filter attribute rather than embedded directly as raw numbers, avoiding noisy vector matches on numeric digits while preserving exact PKR pricing (`1,500` to `160,000` PKR) for filtering and display.

---

## 🚀 How to Run & Check

Run all commands from the project root directory (`HiveSpace-Coworking/`) with your virtual environment active:

### 1. Load & Validate the Product Catalog (Task 1)

```bash
python -m src.catalog
```

**Expected Output:**

- Confirms `Loaded 15 valid products for HiveSpace Coworking (PKR).` and prints a formatted summary of `HS-001` through `HS-015` with categories, PKR prices, billing units, and capacities.
- If `data/products.json` is missing, empty, or invalid, prints `[ERROR] <clear reason>` and exits cleanly with status code `1`.

### 2. Generate & Verify Product Embeddings (Task 2)

```bash
python -m src.embeddings
```

**Expected Output:**

- Loads `data/products.json`, encodes all 15 coworking offerings using `all-MiniLM-L6-v2`, writes normalized `384`-dimensional vectors to `data/embeddings.json` under `vectors_by_id`, and prints a sample `embedding_text` and vector preview.
- If input data is missing or empty, prints `[ERROR] <clear reason>` and exits cleanly with status code `1`.

### 3. Run the Unit Test Suites

Run individual test modules or discover all tests across the repository:

```bash
python -m tests.test_catalog
python -m tests.test_embeddings
```

*(Or run the full test suite at once:)*

```bash
python -m unittest discover -s tests -v
```

**Expected Output:**

- Executes all 8 unit tests (4 catalog tests + 4 embedding tests) covering main paths and failure paths, reporting `Ran 8 tests ... OK`.

---

## 🧠 Architecture Decisions & Trade-offs

### Task 1 — Structured JSON Catalog & Separate Add-on Modeling
- **Decision:** Store the product catalog as structured JSON (`data/products.json`) validated in Python (`src/catalog.py`), and model shared refreshments (`HS-015` — *Pantry Pass (Monthly)*) as a standalone `addon` rather than duplicating chai/coffee perks inside every base pass description.
- **Trade-off:** Unlike a flat CSV, JSON supports nested `amenities` lists and rich multi-sentence `short_description` text without delimiter escaping issues, and separating the Pantry Pass prevents semantic overlap across unrelated desk plans during embedding search. The trade-off is that non-technical staff cannot edit JSON directly in a spreadsheet as easily as a CSV and must rely on `src/catalog.py` to catch syntax or schema mistakes.

### Task 2 — Separate Vectors File Keyed by Product ID (`data/embeddings.json`)
- **Decision:** Store generated `sentence-transformers` embeddings in a separate JSON file (`data/embeddings.json`) keyed by product ID (`vectors_by_id["HS-001"]`, etc.) rather than embedding vectors inline inside `data/products.json`.
- **Trade-off:** Keeping `data/products.json` clean and human-readable lets you re-run or swap embedding models and rebuild `data/embeddings.json` without touching product pricing or catalog records. The trade-off is maintaining two linked files and joining them by product `id` during search.

---

## 📋 Project Progress Summary

- **Task 1 (Product Data) — Completed:** Built a 15-item PKR-priced HiveSpace Coworking product dataset (`data/products.json`), strict catalog/query validator (`src/catalog.py`), baseline keyword/type filter, and unit tests (`tests/test_catalog.py`).
- **Task 2 (Embeddings) — Completed:** Built semantic text construction and `all-MiniLM-L6-v2` vector generation (`src/embeddings.py`), persisted `384`-dimensional embeddings keyed by product ID (`data/embeddings.json`), and verified main and failure paths (`tests/test_embeddings.py`).
- **Upcoming Scope:** Hybrid semantic + metadata search (`Task 3`), relevance evaluation (`Task 4`), API & caching (`Task 5`), and final client handover (`Task 6`).

---

## 📁 Project Structure

```text
HiveSpace-Coworking/
├── README.md                  # Project documentation, run steps & design trade-offs
├── .gitignore                 # Excludes __pycache__, .venv, and local IDE artifacts
├── data/
│   ├── products.json          # 15 realistic HiveSpace Coworking offerings (PKR)
│   └── embeddings.json        # 384-dim normalized vectors keyed by product ID
├── src/
│   ├── __init__.py
│   ├── catalog.py             # Catalog loader, schema validator & baseline filter
│   └── embeddings.py          # Embedding text builder & sentence-transformers encoder
└── tests/
    ├── __init__.py
    ├── test_catalog.py        # Main-path & failure-path catalog unit tests
    └── test_embeddings.py     # Main-path & failure-path embedding unit tests
```
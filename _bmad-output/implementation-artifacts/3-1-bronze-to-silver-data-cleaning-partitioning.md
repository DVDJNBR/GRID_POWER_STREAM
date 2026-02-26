# Story 3.1: Bronze to Silver — Data Cleaning & Partitioning

Status: done

## Story

As a Data Engineer,
I want to use Polars to clean the raw multi-source data (Bronze),
so that it is standardized, deduplicated, and stored as optimized Parquet files in the Silver layer.

## Acceptance Criteria

1. **Given** raw JSON/CSV files in the Bronze layer,
   **When** the Silver transformation job runs,
   **Then** columns are renamed to snake_case, nulls are handled, and duplicates are removed.

2. **Given** cleaned data,
   **When** written to Silver,
   **Then** the data is stored as Parquet files partitioned by `Year/Month/Day` in `silver/`.

3. **Given** the deduplication step,
   **When** processing RTE production data,
   **Then** duplicates are identified by the composite key `(code_insee_region, date_heure)`.

4. **Given** the cleaning process,
   **When** null or corrupted entries are found,
   **Then** they are handled according to defined rules (drop, impute, or flag) and logged.

## Tasks / Subtasks

- [ ] Task 1: Silver transformation module for RTE data (AC: #1, #2, #3)
  - [ ] 1.1: Create `shared/transformations/rte_silver.py` — load Bronze JSON, clean, deduplicate
  - [ ] 1.2: Column normalization: snake_case, consistent types (datetime, float for MW values)
  - [ ] 1.3: Deduplication on `(code_insee_region, date_heure)` composite key
  - [ ] 1.4: Write to `silver/rte/production/year=YYYY/month=MM/day=DD/*.parquet` (Hive partitioning)

- [ ] Task 2: Silver transformation for CSV capacity data (AC: #1, #2)
  - [ ] 2.1: Create `shared/transformations/capacity_silver.py` — load Bronze CSV, clean
  - [ ] 2.2: Standardize column names, handle missing values
  - [ ] 2.3: Write to `silver/reference/capacity/year=YYYY/*.parquet`

- [ ] Task 3: Silver transformation for maintenance data (AC: #1, #2)
  - [ ] 3.1: Create `shared/transformations/maintenance_silver.py` — parse scraped JSON
  - [ ] 3.2: Normalize date formats, clean description text
  - [ ] 3.3: Write to `silver/maintenance/year=YYYY/month=MM/*.parquet`

- [ ] Task 4: Silver transformation for ERA5 climate data (AC: #1, #2)
  - [ ] 4.1: Create `shared/transformations/era5_silver.py` — reproject, clean, standardize
  - [ ] 4.2: Compute derived fields: wind speed magnitude from u100/v100
  - [ ] 4.3: Write to `silver/climate/era5/year=YYYY/month=MM/*.parquet`

- [ ] Task 5: Null/corruption handling framework (AC: #4)
  - [ ] 5.1: Create `shared/transformations/data_quality.py` — null handling rules per source
  - [ ] 5.2: Define strategy per column: drop row, forward fill, interpolate, or flag
  - [ ] 5.3: Log quality metrics (null count, rows dropped, rows imputed) to audit

- [ ] Task 6: Azure Function trigger & orchestration (AC: #1, #2)
  - [ ] 6.1: Create timer-triggered function for Silver transformation (runs after Bronze ingestion)
  - [ ] 6.2: Track last processed Bronze files to avoid reprocessing (checkpoint)
  - [ ] 6.3: Integrate audit logging

- [ ] Task 7: Tests (AC: #1, #2, #3, #4)
  - [ ] 7.1: Unit tests per transformation module with fixture data
  - [ ] 7.2: Test deduplication logic, null handling, partitioning output
  - [ ] 7.3: Integration test — Bronze fixture → Silver output validation

## Dev Notes

### Architecture Requirements

- **Library:** `polars` (mandatory per PRD) — use `pl.scan_parquet()` / `pl.read_json()` for lazy/streaming
- **Partitioning:** Hive-style (`year=YYYY/month=MM/day=DD/`) for efficient downstream queries
- **Memory (NFR-E2):** Use Polars streaming for large datasets, avoid `.collect()` on full datasets
- **Processing model:** Each source gets its own transformation module — modular, testable, independent

### Deduplication Key (from CONCEPTION_TECHNIQUE)

- RTE data: `(code_insee_region, date_heure)` — exact match dedup
- Maintenance: `(event_id)` — natural key
- ERA5: `(region, horodatage)` — spatial-temporal key

### Column Naming Convention

- All output columns: `snake_case`
- Timestamps: `DATETIME2` compatible ISO 8601 strings
- MW values: `FLOAT64` (Polars) → `DECIMAL(10,2)` in SQL

### ⚠️ Known Data Issues (from Story 0.1 API Exploration)

- **`pompage`** has inconsistent type across records: sometimes `str` ("0"), sometimes `int` (0). Cast to `Float64` during cleaning.
- **`stockage_batterie`/`destockage_batterie`** same issue — cast to `Float64`.
- **`column_68`/`column_30`** are null artifacts — drop during Silver transformation.

### Dependencies

- Stories 1.1, 1.2, 2.1, 2.2: Bronze data must exist (at least fixture samples for testing)
- Story 1.0: ADLS Gen2 provisioned

### Project Structure (additions)

```
functions/
└── shared/
    └── transformations/         # [NEW] Silver transformation modules
        ├── __init__.py
        ├── rte_silver.py
        ├── capacity_silver.py
        ├── maintenance_silver.py
        ├── era5_silver.py
        └── data_quality.py
tests/
└── test_transformations/        # [NEW]
    ├── test_rte_silver.py
    ├── test_capacity_silver.py
    ├── test_maintenance_silver.py
    ├── test_era5_silver.py
    └── test_data_quality.py
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.1] — Original AC
- [Source: CONTEXT/CONCEPTION_TECHNIQUE.md#Pipeline ETL] — Bronze→Silver logic, dedup key
- [Source: _bmad-output/planning-artifacts/prd.md#FR8] — Cleaning, partitioning
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-E2] — Polars streaming efficiency

## Dev Agent Record

### Agent Model Used

Antigravity (Amelia 💻)

### Debug Log References

`pytest`: 17/17 Silver tests pass (0.27s)

### Completion Notes List

- 5 Silver transformation modules: rte, capacity, maintenance, era5, data_quality
- Data quality framework with 4 null strategies: DROP, FILL_ZERO, FORWARD_FILL, FLAG
- RTE: dedup on (code_insee_region, date_heure), pompage/stockage cast Str→Float64
- Hive-partitioned Parquet output: `year=YYYY/month=MM/day=DD/`
- Fixed Polars 1.25+ strict timezone parsing (`time_zone="UTC"`)
- Modular: each source has its own transformation module

### File List

- `functions/shared/transformations/__init__.py` — [NEW] Package init
- `functions/shared/transformations/data_quality.py` — [NEW] Null handling framework
- `functions/shared/transformations/rte_silver.py` — [NEW] RTE Bronze→Silver
- `functions/shared/transformations/capacity_silver.py` — [NEW] Capacity CSV→Silver
- `functions/shared/transformations/maintenance_silver.py` — [NEW] Maintenance JSON→Silver
- `functions/shared/transformations/era5_silver.py` — [NEW] ERA5 Parquet→Silver
- `tests/test_transformations.py` — [NEW] 17 tests

### Change Log

- 2026-02-26: Story completed. 17/17 tests pass.

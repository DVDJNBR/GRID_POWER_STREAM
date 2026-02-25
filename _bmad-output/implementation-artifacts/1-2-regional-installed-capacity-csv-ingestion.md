# Story 1.2: Regional Installed Capacity (CSV) Ingestion

Status: ready-for-dev

## Story

As a Platform Builder,
I want to automate the collection of regional installed capacity CSV files,
so that we have the reference points needed to calculate performance metrics (load factors).

## Acceptance Criteria

1. **Given** the capacity CSV files are uploaded to the source landing zone,
   **When** the ingestion process runs,
   **Then** the files are moved to `bronze/reference/capacity/` without schema alteration.

2. **Given** a successful CSV ingestion,
   **When** the file is stored in Bronze,
   **Then** the data is logged as successfully received in the audit logs.

3. **Given** the CSV file is malformed or empty,
   **When** the ingestion process runs,
   **Then** the error is logged and the file is moved to `bronze/reference/capacity/errors/`.

## Tasks / Subtasks

- [ ] Task 1: CSV ingestion Azure Function (AC: #1, #2)
  
  - [ ] 1.1: Create timer-triggered or blob-triggered function for CSV ingestion
  - [ ] 1.2: Create `shared/csv_ingestion.py` — read CSV from landing zone (ADLS Gen2 `landing/capacity/`)
  - [ ] 1.3: Copy raw CSV to `bronze/reference/capacity/YYYY/MM/{filename}_{timestamp}.csv` preserving original content
  - [ ] 1.4: Integrate with `shared/audit_logger.py` (reuse from Story 1.1) for heartbeat logging

- [ ] Task 2: Error handling & validation (AC: #3)
  
  - [ ] 2.1: Basic validation: file not empty, valid CSV structure (parseable headers)
  - [ ] 2.2: Move malformed files to `bronze/reference/capacity/errors/` with error metadata
  - [ ] 2.3: Log validation failures to audit logs

- [ ] Task 3: Tests (AC: #1, #2, #3)
  
  - [ ] 3.1: Unit tests for `csv_ingestion.py` — valid CSV, empty file, malformed CSV
  - [ ] 3.2: Integration test — full pipeline from landing zone to Bronze storage

## Dev Notes

### Architecture Requirements

- **Reuse** `shared/audit_logger.py` and `shared/bronze_storage.py` from Story 1.1 — extend if needed for CSV
- **Storage convention:** `bronze/reference/capacity/YYYY/MM/{original_filename}_{ISO8601}.csv`
- **No transformation:** Raw CSV stored as-is (FR2 — "without schema alteration")
- **Trigger strategy:** Timer trigger (daily check) or Blob trigger on `landing/capacity/` container
- **CSV data context:** Regional installed capacity per energy source per region — used later in Story 3.2 for load factor calculation (`valeur_mw / puissance_installee`)

### Dependencies

- Story 1.0 (Terraform): ADLS Gen2 must be provisioned
- Story 1.1: Shared modules (`audit_logger.py`, `bronze_storage.py`) must exist

### Project Structure (additions)

```
functions/
├── function_app.py              # Add CSV ingestion trigger
└── shared/
    ├── csv_ingestion.py         # [NEW] CSV landing zone handler
    └── ...                      # Reuse existing modules
tests/
└── test_csv_ingestion.py        # [NEW]
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR2] — Flat Files extraction
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md#SITE_PRODUCTION] — puissance_installee_mw from CSV

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log

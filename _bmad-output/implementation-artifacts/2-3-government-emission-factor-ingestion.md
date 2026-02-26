# Story 2.3: Government Emission Factor Ingestion (Open Data)

Status: done

## Story

As a Platform Builder,
I want to ingest government emission factor data from public Open Data sources,
so that we can calculate carbon intensity metrics in the Gold layer.

## Acceptance Criteria

1. **Given** the government emission factor Open Data source is identified,
   **When** the ingestion function runs,
   **Then** the emission factor data is downloaded and stored in `bronze/reference/emissions/`.

2. **Given** the downloaded data,
   **When** stored in Bronze,
   **Then** the original format is preserved (CSV/JSON) with a timestamp.

3. **Given** the emission factors change infrequently (yearly),
   **When** the ingestion schedule runs,
   **Then** it only downloads if new data is available (conditional fetch or checksum comparison).

## Tasks / Subtasks

- [ ] Task 1: Source identification & ingestion (AC: #1, #2)
  - [ ] 1.1: Identify government emission factor source (ADEME Base Carbone, data.gouv.fr, or equivalent)
  - [ ] 1.2: Create `shared/emissions_client.py` — download emission factors (REST API or direct file download)
  - [ ] 1.3: Store raw file in `bronze/reference/emissions/YYYY/emission_factors_{timestamp}.csv`
  - [ ] 1.4: Reuse `shared/audit_logger.py` for heartbeat logging

- [ ] Task 2: Conditional fetch & deduplication (AC: #3)
  - [ ] 2.1: Implement conditional fetch (HTTP ETag/Last-Modified or file checksum)
  - [ ] 2.2: Skip download if data hasn't changed since last ingestion
  - [ ] 2.3: Log skip/download decision to audit

- [ ] Task 3: Tests (AC: #1, #2, #3)
  - [ ] 3.1: Unit tests for `emissions_client.py` — download, conditional fetch, error handling
  - [ ] 3.2: Integration test with sample fixture data

## Dev Notes

### Architecture Requirements

- **Source candidates:**
  - ADEME Base Carbone: `https://data.ademe.fr/` — French emission factors per energy source
  - data.gouv.fr: Government open data portal
  - EEA (European Environment Agency): EU-level factors
- **Frequency:** Monthly or on-demand (emission factors update yearly at most)
- **Storage:** `bronze/reference/emissions/` — raw file preservation
- **Downstream:** Used in Story 3.2 (Gold) for `prix_mwh` or carbon intensity calculation in FACT_ENERGY_FLOW

### Dependencies

- Story 1.0: ADLS Gen2 provisioned
- Story 1.1: Shared modules (audit_logger.py)

### References

- [Source: _bmad-output/planning-artifacts/prd.md#FR4] — Government emission factor data
- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2] — Grid Context Enrichment

> [!IMPORTANT]
> 🎯 **Après cette story → exécuter Story M1 (Milestone E7 — Documentation Data Lake)**

## Dev Agent Record

### Agent Model Used

Antigravity (Amelia 💻)

### Debug Log References

`pytest`: 8/8 emissions tests pass (0.16s)

### Completion Notes List

- Source: ADEME Base Carbone via data.ademe.fr API
- Conditional fetch via SHA-256 checksum (AC #3) — skips if data unchanged
- Dual-mode: URL download or local file ingestion
- Fixture: 12 sources (nucléaire 6 kg/MWh → charbon 1060 kg/MWh)
- Raw CSV preserved as-is in Bronze (AC #2)

### File List

- `functions/shared/emissions_client.py` — [NEW] Emission factor client
- `tests/test_emissions_client.py` — [NEW] 8 tests
- `tests/fixtures/emission_factors_sample.csv` — [NEW] ADEME fixture (12 sources)

### Change Log

- 2026-02-26: Story completed. 8/8 tests pass.

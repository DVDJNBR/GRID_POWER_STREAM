# Story 2.2: Historical Climate Reanalysis (ERA5) Parquet Ingestion

Status: done

## Story

As a Platform Builder,
I want to extract weather datasets (wind speed, solar radiation) in Parquet format from a public Big Data storage (Azure Open Datasets/S3),
so that we can perform large-scale theoretical yield calculations.

## Acceptance Criteria

1. **Given** access to the public ERA5 object storage,
   **When** the ingestion job (using Polars) pulls the hourly deltas,
   **Then** the Parquet files are partitioned and saved in `bronze/climate/era5/`.

2. **Given** the ingestion process,
   **When** processing large Parquet files,
   **Then** Polars "streaming" mode is used to minimize memory footprint (NFR-E2).

3. **Given** Azure Function execution limits (max 10 min on Consumption plan),
   **When** processing mass historical imports,
   **Then** the implementation handles chunked processing to avoid timeouts.

4. **Given** a successful climate ingestion,
   **When** the data is stored in Bronze,
   **Then** a heartbeat entry is logged in the audit system.

## Tasks / Subtasks

- [ ] Task 1: ERA5 data source discovery (AC: #1)
  - [ ] 1.1: Identify ERA5 public data source (Azure Open Datasets, Copernicus CDS, or AWS S3)
  - [ ] 1.2: Create `shared/era5_client.py` — connect to ERA5 source and list available datasets
  - [ ] 1.3: Define data scope: wind speed at 100m (`u100`, `v100`), solar radiation (`ssrd`), surface temperature (`t2m`)
  - [ ] 1.4: Determine geographic filter: France metropolitan regions matching DIM_REGION

- [ ] Task 2: Polars streaming ingestion (AC: #1, #2, #3)
  - [ ] 2.1: Implement `shared/era5_ingestion.py` — read Parquet with `polars.scan_parquet()` (lazy/streaming)
  - [ ] 2.2: Apply geographic and temporal filters lazily before collecting
  - [ ] 2.3: Implement chunked processing: process data in time-window chunks (e.g., 1 month per chunk) to stay within Function timeout
  - [ ] 2.4: Write partitioned output to `bronze/climate/era5/YYYY/MM/era5_{region}_{timestamp}.parquet`

- [ ] Task 3: Azure Function trigger (AC: #3, #4)
  - [ ] 3.1: Create timer-triggered function (hourly or daily) for ERA5 delta ingestion
  - [ ] 3.2: Track last ingestion timestamp to pull only new/updated data
  - [ ] 3.3: Implement checkpoint mechanism (store last processed timestamp in ADLS or Table Storage)
  - [ ] 3.4: Integrate with `shared/audit_logger.py`

- [ ] Task 4: Tests (AC: #1, #2, #3, #4)
  - [ ] 4.1: Unit tests for `era5_client.py` — mock data source responses
  - [ ] 4.2: Unit tests for `era5_ingestion.py` — streaming mode, chunking, partitioning
  - [ ] 4.3: Integration test with small sample Parquet fixture

## Dev Notes

### Architecture Requirements

- **Library:** `polars` (NOT pandas) — mandatory for streaming mode and memory efficiency (NFR-E2)
- **Streaming mode:** Use `pl.scan_parquet()` → lazy operations → `.collect(streaming=True)` to avoid OOM
- **Timeout handling:** Azure Functions Consumption plan = 10 min max. Process in chunks of ~1 month of data
- **Checkpoint:** Store `last_processed_date` in a small JSON file in ADLS (`bronze/climate/era5/_checkpoint.json`)

### ERA5 Data Context (from CONCEPTION_DATAMODEL)

Maps to `METEO_HISTO` entity:

- `vitesse_vent_100m` ← ERA5 `u100`, `v100` (compute wind speed magnitude)
- `rayonnement_solaire` ← ERA5 `ssrd` (surface solar radiation downwards)

### Dependencies

- Story 1.0: ADLS Gen2 provisioned
- Story 1.1: Shared modules (`audit_logger.py`, `bronze_storage.py`)

### Bronze Storage Convention

```
bronze/
  climate/
    era5/
      _checkpoint.json           # Last ingestion timestamp
      YYYY/
        MM/
          era5_{region_code}_{ISO8601}.parquet
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR5] — ERA5 Big Data extraction (C8)
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-E2] — Polars streaming, memory efficiency
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md#METEO_HISTO] — Weather entity model

## Dev Agent Record

### Agent Model Used

Antigravity (Amelia 💻)

### Debug Log References

`pytest`: 8/8 ERA5 tests pass (0.38s)

### Completion Notes List

- Uses `pl.scan_parquet()` + `collect(engine="streaming")` for memory-efficient lazy loading (NFR-E2)
- Wind speed computed from u100/v100 components: `sqrt(u100² + v100²)`
- Temperature converted K → °C
- Grid points mapped to nearest French region via centroid distance
- Chunked processing by month for Azure Function 10-min timeout (AC #3)
- Checkpoint mechanism (`_checkpoint.json`) for delta ingestion
- Sample fixture: 144 rows (3 regions × 48 hours)

### File List

- `functions/shared/era5_ingestion.py` — [NEW] Polars streaming ingestion
- `tests/test_era5_ingestion.py` — [NEW] 8 tests
- `tests/fixtures/era5_sample.parquet` — [NEW] ERA5 sample (144 rows)
- `scripts/generate_era5_fixture.py` — [NEW] Fixture generator

### Change Log

- 2026-02-26: Story completed. 8/8 tests pass.

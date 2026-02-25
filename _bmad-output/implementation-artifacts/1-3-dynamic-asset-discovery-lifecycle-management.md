# Story 1.3: Dynamic Asset Discovery & Lifecycle Management (C11, C14)

Status: ready-for-dev

## Story

As a Data Architect,
I want the system to manage the full lifecycle of grid assets by discovering new entities and marking stale ones as inactive in the SQL database,
so that we maintain a high-quality, up-to-date registry without losing historical referential integrity.

## Acceptance Criteria

1. **Given** the extraction of current RTE data (Bronze),
   **When** a region or node is found in the flux that doesn't exist in SQL,
   **Then** it is inserted with `status='active'` and `first_seen_at` timestamp.

2. **Given** an existing SQL node,
   **When** it is NOT found in the RTE flux for a configurable period (e.g., 24h),
   **Then** its status is updated to `status='stale'` or `inactive` (Soft Delete).

3. **Given** a stale/inactive asset,
   **When** historical queries are run on the Gold layer,
   **Then** the system avoids hard-deleting records to preserve historical production links.

4. **Given** a discovery or decommissioning event,
   **When** the lifecycle operation completes,
   **Then** the event is logged for operational review.

## Tasks / Subtasks

- [ ] Task 1: Asset registry SQL schema (AC: #1, #3)
  
  - [ ] 1.1: Extend DIM_REGION with `status` (active/stale/inactive), `first_seen_at`, `last_seen_at` columns
  - [ ] 1.2: Create migration SQL script (`infra/sql/migrations/001_asset_lifecycle.sql`)
  - [ ] 1.3: Ensure soft-delete design — no `DELETE` statements, only status updates

- [ ] Task 2: Asset discovery module (AC: #1, #4)
  
  - [ ] 2.1: Create `shared/asset_discovery.py` — compare Bronze RTE regions against SQL DIM_REGION
  - [ ] 2.2: INSERT new regions with `status='active'`, `first_seen_at=NOW()`
  - [ ] 2.3: UPDATE `last_seen_at` for all matching regions
  - [ ] 2.4: Log discovery events via `shared/audit_logger.py`

- [ ] Task 3: Staleness detection module (AC: #2, #4)
  
  - [ ] 3.1: Create `shared/asset_lifecycle.py` — detect regions not seen for configurable threshold (default 24h)
  - [ ] 3.2: UPDATE stale regions: `status='stale'` (after threshold) → `status='inactive'` (after extended threshold)
  - [ ] 3.3: Log decommissioning events to audit logs
  - [ ] 3.4: Make staleness threshold configurable via environment variable

- [ ] Task 4: Integration into ingestion pipeline (AC: #1, #2)
  
  - [ ] 4.1: Call asset discovery after each RTE API ingestion (post Story 1.1 pipeline)
  - [ ] 4.2: Schedule staleness check (daily or after each ingestion cycle)

- [ ] Task 5: Tests (AC: #1, #2, #3, #4)
  
  - [ ] 5.1: Unit tests for `asset_discovery.py` — new region, existing region update
  - [ ] 5.2: Unit tests for `asset_lifecycle.py` — stale detection, inactive transition
  - [ ] 5.3: Integration test — full discovery + lifecycle cycle with mock SQL

## Dev Notes

### Architecture Requirements

- **SQL connection:** Use `pyodbc` or `pymssql` with Managed Identity (DefaultAzureCredential + token-based SQL auth)
- **Soft delete pattern (C14):** NEVER use `DELETE` — status field transitions: `active` → `stale` → `inactive`
- **Configurable threshold:** `STALENESS_THRESHOLD_HOURS` env var (default 24)
- **Extended threshold:** `INACTIVE_THRESHOLD_HOURS` env var (default 168 = 7 days)

### Data Model Impact

```sql
ALTER TABLE DIM_REGION ADD
  status VARCHAR(10) DEFAULT 'active',     -- active | stale | inactive
  first_seen_at DATETIME2 DEFAULT GETDATE(),
  last_seen_at DATETIME2 DEFAULT GETDATE();
```

### Dependencies

- Story 1.0: SQL database provisioned with DIM_REGION table
- Story 1.1: Bronze RTE data available + shared modules

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3] — Original AC
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md#DIM_REGION] — Region dimension table
- [Source: _bmad-output/planning-artifacts/prd.md#FR17] — Audit logs (C20)

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log

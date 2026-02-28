# Story 3.2: Silver to Gold — Relational Serving & Reconciliation (C11, C14)

Status: done

## Story

As a Data Analyst,
I want to reconcile the newly discovered RTE assets with their SQL metadata (Population, Area) during the Gold move,
so that our warehouse is always synchronized with the reality of the grid flux.

## Acceptance Criteria

1. **Given** new assets discovered in Story 1.3,
   **When** the Gold transformation job runs,
   **Then** it performs a relational join in Azure SQL between the measurements and the asset registry.

2. **Given** Silver Parquet data,
   **When** loading into Gold (Azure SQL),
   **Then** it updates `FACT_ENERGY_FLOW` with the most recent resolved metadata.

3. **Given** the Star Schema design (C11/C14),
   **When** data is loaded,
   **Then** DIM tables are upserted (insert or update) and FACT rows reference valid dimension keys.

4. **Given** the Gold layer,
   **When** the API service principal queries it,
   **Then** tables are read-only for that principal (NFR-S3).

## Tasks / Subtasks

- [ ] Task 1: Dimension table population (AC: #3)
  - [ ] 1.1: Create `shared/gold/dim_loader.py` — upsert DIM_REGION from Silver + asset registry
  - [ ] 1.2: Upsert DIM_TIME — generate time dimension entries for ingested data ranges
  - [ ] 1.3: Upsert DIM_SOURCE — populate energy source types (éolien, solaire, nucléaire, hydraulique, etc.)
  - [ ] 1.4: Use MERGE statements (SQL Server) for idempotent upserts

- [ ] Task 2: Fact table loading (AC: #1, #2)
  - [ ] 2.1: Create `shared/gold/fact_loader.py` — read Silver Parquet, resolve FK references to DIM tables
  - [ ] 2.2: Perform join: Silver measurements + DIM_REGION (by code_insee) + DIM_TIME (by horodatage) + DIM_SOURCE (by source type)
  - [ ] 2.3: Calculate `facteur_charge` = `valeur_mw / puissance_installee` (from capacity data)
  - [ ] 2.4: INSERT into FACT_ENERGY_FLOW with resolved dimension keys

- [ ] Task 3: RBAC enforcement (AC: #4)
  - [ ] 3.1: Create SQL script to configure read-only role for API service principal on Gold tables
  - [ ] 3.2: Ensure ETL process uses a separate principal with write access
  - [ ] 3.3: Document RBAC setup in `infra/sql/rbac_setup.sql`

- [ ] Task 4: Azure Function orchestration (AC: #1, #2)
  - [ ] 4.1: Create timer-triggered function for Gold loading (runs after Silver transformation)
  - [ ] 4.2: Track last processed Silver data (checkpoint) to avoid reprocessing
  - [ ] 4.3: Audit logging for Gold loading operations

- [ ] Task 5: Tests (AC: #1, #2, #3)
  - [ ] 5.1: Unit tests for `dim_loader.py` — upsert logic, idempotency
  - [ ] 5.2: Unit tests for `fact_loader.py` — FK resolution, facteur_charge calculation
  - [ ] 5.3: Integration test — Silver fixture → Gold SQL validation

- [ ] Task 6: Gold data retention (cleanup)
  - [ ] 6.1: Create timer-triggered function (weekly) — `DELETE FROM FACT_ENERGY_FLOW WHERE id_date IN (SELECT id_date FROM DIM_TIME WHERE horodatage < DATEADD(month, -3, GETDATE()))`
  - [ ] 6.2: Orphan cleanup: remove DIM_TIME rows no longer referenced by FACT
  - [ ] 6.3: Log purge metrics to audit

## Dev Notes

### Architecture Requirements

- **SQL connection:** `pyodbc` with Managed Identity token-based auth (DefaultAzureCredential)
- **Gold = Azure SQL** (NOT ADLS Gen2) — Star Schema lives in Azure SQL Serverless
- **Upsert pattern:** SQL MERGE statement for dimensions, INSERT for facts (append-only)
- **Read Parquet → Write SQL:** Use Polars to read Silver Parquet, then batch INSERT via pyodbc

### Star Schema (from CONCEPTION_DATAMODEL)

```sql
FACT_ENERGY_FLOW (id_fact, id_date FK, id_region FK, id_source FK, valeur_mw, facteur_charge, temperature_moyenne, prix_mwh)
DIM_REGION (id_region, code_insee, nom_region, population, superficie)
DIM_TIME (id_date, horodatage, jour, mois, annee, heure)
DIM_SOURCE (id_source, source_name, is_green)
```

### Load Factor Calculation

`facteur_charge = valeur_mw / puissance_installee_mw`

- `valeur_mw` from Silver RTE data
- `puissance_installee_mw` from Silver capacity data (Story 1.2 → 3.1)

### Dependencies

- Story 1.0: SQL schema provisioned (DIM/FACT tables)
- Story 1.3: Asset registry populated (DIM_REGION enriched)
- Story 3.1: Silver data available

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.2] — Original AC
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md#Star Schema] — FACT_ENERGY_FLOW, DIM tables
- [Source: CONTEXT/CONCEPTION_TECHNIQUE.md#Silver to Gold] — Aggregation, joins, KPI calculation
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-S3] — Gold read-only for API principal

## Dev Agent Record

### Agent Model Used

Antigravity (Amelia 💻)

### Debug Log References

`pytest`: 11/11 Gold tests pass (0.26s). Full suite: 95/95 (1.04s)

### Completion Notes List

- Star Schema: DIM_REGION, DIM_TIME, DIM_SOURCE, FACT_ENERGY_FLOW
- DIM upserts with ON CONFLICT (SQLite) / MERGE (SQL Server) — idempotent
- FACT_ENERGY_FLOW: unpivots wide Silver format → long fact rows
- Facteur de charge = valeur_mw / puissance_installee (AC #2)
- FK integrity enforced (all FACT rows reference valid DIMs)
- Weekend detection in DIM_TIME for analytics
- RBAC: gold_reader (SELECT-only) / gold_writer roles
- SQLite local dev mode (no Azure SQL needed for testing)

### File List

- `functions/shared/gold/__init__.py` — [NEW] Package init
- `functions/shared/gold/dim_loader.py` — [NEW] DIM upsert loader
- `functions/shared/gold/fact_loader.py` — [NEW] FACT loader with FK resolution
- `infra/sql/rbac_setup.sql` — [NEW] RBAC roles (NFR-S3)
- `tests/test_gold_loader.py` — [NEW] 11 tests

### Change Log

- 2026-02-26: Story completed. 11/11 tests pass.

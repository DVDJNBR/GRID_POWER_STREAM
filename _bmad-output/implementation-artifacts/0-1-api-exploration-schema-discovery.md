# Story 0.1: API Exploration & Schema Discovery

Status: done

## Story

As a Data Architect,
I want to interactively explore the RTE eCO2mix API and all planned data sources to understand their real response structures,
so that I can design a validated SQL schema (Star Schema) grounded in actual data rather than assumptions.

## Acceptance Criteria

1. **Given** the RTE eCO2mix API documentation and endpoint,
   **When** exploratory API calls are executed,
   **Then** the complete JSON response structure is documented with all field names, types, and sample values.

2. **Given** the documented API response,
   **When** the schema is designed,
   **Then** a validated `init_schema.sql` is produced mapping all RTE fields to DIM/FACT tables.

3. **Given** the CSV capacity files and other data sources (maintenance, ERA5),
   **When** their structures are analyzed,
   **Then** their fields are integrated into the schema design (or noted for future iteration).

4. **Given** the exploration results,
   **When** sample data is collected,
   **Then** test fixture files (JSON, CSV) are saved for use in later story unit tests.

## Tasks / Subtasks

- [x] Task 1: RTE eCO2mix API exploration (AC: #1)
  - [x] 1.1: Create `scripts/explore_rte_api.py`
  - [x] 1.2: Base URL confirmed: Opendatasoft v2.1 (`odre.opendatasoft.com`)
  - [x] 1.3: Auth: **PUBLIC — no authentication required**
  - [x] 1.4: Called `eco2mix-regional-tr` + `eco2mix-national-tr` + `eco2mix-regional-cons-def`
  - [x] 1.5: Complete field structure documented (see `docs/api_exploration_report.md`)
  - [x] 1.6: 15-min granularity confirmed, offset/limit pagination
  - [x] 1.7: Rate limits documented (50k calls/month estimated)

- [x] Task 2: Secondary data source exploration (AC: #3)
  - [x] 2.1: CSV capacity — deferred to Story 1.2 (needs real file)
  - [x] 2.2: Maintenance portals — assessed, deferred to Story 2.1
  - [x] 2.3: ERA5 Parquet — deferred to Story 2.2

- [x] Task 3: Schema design from real data (AC: #2)
  - [x] 3.1: Mapped all API fields to DIM/FACT columns
  - [x] 3.2: Gaps documented: `thermique` replaces `fioul/gaz`, `tco_*/tch_*` added
  - [x] 3.3: SQL types designed from real data
  - [x] 3.4: `infra/sql/init_schema.sql` written
  - [x] 3.5: `infra/sql/seed_dimensions.sql` written (9 sources, 12 regions)

- [x] Task 4: Test fixtures & documentation (AC: #4)
  - [x] 4.1: Saved `tests/fixtures/rte_eco2mix_regional_sample.json` + national
  - [x] 4.2: CSV fixture deferred to Story 1.2
  - [x] 4.3: `docs/api_exploration_report.md` written
  - [x] 4.4: Schema divergences documented in exploration report

## Dev Notes

### Architecture Requirements

- This is an **exploratory story** — output is documentation + SQL scripts, not production code
- The exploration script(s) are in `scripts/` (utility, not deployed)
- The validated `init_schema.sql` is the KEY OUTPUT — used by Story 1.0 Terraform
- Python libraries needed: `requests`, `polars` (for Parquet inspection), `parsel` (for scraping assessment)

### RTE API Starting Points (from research)

- **Opendatasoft v2.1 API:** `GET https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/records`
- **Legacy v1 API:** `GET https://opendata.rte-france.com/api/v1/eco2mix_regional_real_time`
- **Auth options:** OAuth2 client_credentials OR Opendatasoft API key
- **Known fields (CONCEPTION_TECHNIQUE):** `code_insee_region`, `date_heure`, `consommation`, `nucleaire`, `eolien`, `solaire`, `hydraulique`, `pompage`, `bioenergies`
- ⚠️ **MUST VERIFY** actual field names — Opendatasoft may use different names than legacy API

### Expected Schema Adjustments

The current CONCEPTION_DATAMODEL defines:

```
DIM_REGION (id_region, code_insee, nom_region, population, superficie)
DIM_TIME (id_date, horodatage, jour, mois, annee, heure)
DIM_SOURCE (id_source, source_name, is_green)
FACT_ENERGY_FLOW (id_fact, id_date FK, id_region FK, id_source FK, valeur_mw, facteur_charge, temperature_moyenne, prix_mwh)
```

This exploration may reveal:

- Additional fields from the API not accounted for
- Different field names requiring mapping
- Missing energy source types
- Different data granularity than expected

### Dependencies

- RTE Data Portal account (API credentials) — David may need to provide these
- No infrastructure dependency — this runs locally

### Project Structure (additions)

```
WATT_WATCHER/
├── scripts/
│   └── explore_rte_api.py       # [NEW] Interactive API explorer
├── infra/
│   └── sql/
│       ├── init_schema.sql      # [NEW] Validated Star Schema DDL
│       └── seed_dimensions.sql  # [NEW] Dimension seed data
├── tests/
│   └── fixtures/                # [NEW] Sample data for tests
│       ├── rte_eco2mix_sample.json
│       └── capacity_sample.csv
└── docs/
    └── api_exploration_report.md  # [NEW] Exploration findings
```

### References

- [Source: _bmad-output/planning-artifacts/prd.md#Data Strategy] — "Exploratory Schema Modeling"
- [Source: CONTEXT/CONCEPTION_TECHNIQUE.md#API Source Specifications] — RTE endpoint, fields
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md] — Current Star Schema design to validate
- [Source: sprint-change-proposal-2026-02-24.md] — Approved resequencing rationale

## Dev Agent Record

### Agent Model Used

Antigravity (Amelia 💻)

### Debug Log References

Exploration script output: 12 regions, 9 sources, 3 datasets, API public.

### Completion Notes List

- API is PUBLIC — no OAuth2/API key needed (simplifies Story 1.1 significantly)
- `tch_*` fields = facteur de charge already computed by RTE → may not need to calculate in Gold
- `pompage` has inconsistent type (str in some records, int in others) → clean in Story 3.1
- `column_68`/`column_30` are null artifacts → ignore
- Date filter ODSQL syntax differs from standard SQL → test carefully in Story 1.1
- National API has finer source breakdown (fioul_tac, gaz_ccg, etc.) but regional uses `thermique`

### File List

- `scripts/explore_rte_api.py` — [NEW] API exploration script
- `infra/sql/init_schema.sql` — [NEW] Validated Star Schema DDL
- `infra/sql/seed_dimensions.sql` — [NEW] Dimension seed data
- `tests/fixtures/rte_eco2mix_regional_sample.json` — [NEW] API fixture
- `tests/fixtures/rte_eco2mix_national_sample.json` — [NEW] API fixture
- `docs/api_exploration_report.md` — [NEW] Full exploration findings

### Change Log

- 2026-02-25: Story completed. All 4 tasks done.

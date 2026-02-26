# Story 4.1: Production API Endpoints (FastAPI/Functions)

Status: review

## Story

As a Developer,
I want to access regional production and carbon intensity data via RESTful endpoints,
so that I can build downstream applications or integrate the data into other systems.

## Acceptance Criteria

1. **Given** an authenticated request to `/production/regional`,
   **When** valid query parameters (region_code, timeframe) are provided,
   **Then** the system returns a JSON response containing the aggregated metrics from the Gold SQL layer.

2. **Given** a valid API request,
   **When** the query is executed,
   **Then** the response time is less than 500ms (NFR-P2).

3. **Given** the API,
   **When** deployed as an Azure Function HTTP trigger,
   **Then** it follows RESTful conventions with proper status codes (200, 400, 401, 404, 500).

4. **Given** the CSV export requirement (FR15),
   **When** a request is made to `/export/csv` with query parameters,
   **Then** the response is a downloadable CSV file with proper headers.

## Tasks / Subtasks

- [x] Task 1: API framework setup (AC: #1, #3)

  - [x] 1.1: Create HTTP-triggered Azure Function(s) in `function_app.py` using v2 model
  - [x] 1.2: Create `shared/api/routes.py` — route definitions for `/v1/production/regional` and `/v1/export/csv`
  - [x] 1.3: Create `shared/api/models.py` — request/response Pydantic models (or dataclasses)
  - [x] 1.4: Implement API versioning with `/v1/` prefix

- [x] Task 2: Production query endpoint (AC: #1, #2)

  - [x] 2.1: Create `shared/api/production_service.py` — query Gold SQL FACT_ENERGY_FLOW + DIM joins
  - [x] 2.2: Support query parameters: `region_code` (optional), `start_date`, `end_date`, `source_type` (optional)
  - [x] 2.3: Return aggregated JSON: `{region, timestamp, sources: {eolien, solaire, ...}, facteur_charge}`
  - [x] 2.4: Optimize SQL queries with indexes for <500ms response (NFR-P2)

- [x] Task 3: CSV export endpoint (AC: #4)

  - [x] 3.1: Create `shared/api/export_service.py` — generate CSV from same Gold queries
  - [x] 3.2: Set response headers: `Content-Type: text/csv`, `Content-Disposition: attachment; filename=...`
  - [x] 3.3: Format optimized for Excel compatibility (UTF-8 BOM, semicolon separator for FR locale)

- [x] Task 4: Error handling & responses (AC: #3)

  - [x] 4.1: Create `shared/api/error_handlers.py` — standardized error responses
  - [x] 4.2: Implement: 400 (invalid params), 401 (unauthorized), 404 (no data), 500 (server error)
  - [x] 4.3: Include request_id in all responses for traceability

- [x] Task 5: Tests (AC: #1, #2, #3, #4)

  - [x] 5.1: Unit tests for `production_service.py` — mock SQL, validate response shape
  - [x] 5.2: Unit tests for `export_service.py` — CSV format validation
  - [x] 5.3: Integration tests — HTTP trigger → response validation
  - [x] 5.4: Performance test — verify <500ms on sample dataset

## Dev Notes

### Architecture Requirements

- **Framework:** Azure Functions HTTP triggers (v2 model) — NOT FastAPI standalone; keep serverless on Consumption plan
- **Alternative:** If routing becomes complex, consider `azure-functions-openapi-extension` for OpenAPI support directly in Functions
- **SQL connection:** `pyodbc` with Managed Identity (reuse pattern from Story 3.2)
- **Response format:** JSON (primary), CSV (export endpoint)
- **Versioning:** URL path prefix `/v1/`

### Gold Layer Query Pattern

```sql
SELECT r.code_insee, r.nom_region, t.horodatage, s.source_name, f.valeur_mw, f.facteur_charge
FROM FACT_ENERGY_FLOW f
JOIN DIM_REGION r ON f.id_region = r.id_region
JOIN DIM_TIME t ON f.id_date = t.id_date
JOIN DIM_SOURCE s ON f.id_source = s.id_source
WHERE r.code_insee = @region_code
  AND t.horodatage BETWEEN @start_date AND @end_date
ORDER BY t.horodatage DESC
```

### Performance (NFR-P2)

- Add SQL indexes: `IX_FACT_region_date` on `(id_region, id_date)`
- Use parameterized queries to leverage query plan caching
- Limit default result set (pagination: `?limit=100&offset=0`)

### Dependencies

- Story 1.0: SQL provisioned
- Story 3.2: Gold layer populated
- Story 4.2: JWT auth (can be added as middleware after)

### Project Structure (additions)

```
functions/
└── shared/
    └── api/                     # [NEW] API modules
        ├── __init__.py
        ├── routes.py
        ├── models.py
        ├── production_service.py
        ├── export_service.py
        └── error_handlers.py
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 4.1] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR12,FR15] — API + CSV export
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-P2] — <500ms response
- [Source: _bmad-output/planning-artifacts/prd.md#Endpoint Specification] — Routes, versioning

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fix préalable 3.3: `functions/__init__.py` manquant → Pyright `reportMissingImports` résolu
- Fix préalable 3.3: `yaml` possibly unbound dans `gate_runner.py` → `yaml = None  # type: ignore` dans le except
- Export 404: détection no-data via `row_count` (3ème valeur du tuple) plutôt que `len(bytes) <= 3`

### Completion Notes List

- `functions/shared/api/` créé avec 5 modules + `__init__.py`
- HTTP triggers v2 ajoutés dans `function_app.py` : GET /v1/production/regional, GET /v1/export/csv
- `production_service.py` : requête paramétrisée, pivot sources par région/timestamp, pagination
- `export_service.py` : UTF-8 BOM, séparateur `;`, headers FR, retourne `(bytes, filename, row_count)`
- `error_handlers.py` : 400/401/404/500, `request_id` systématique
- `models.py` : dataclasses + validation `parse_production_request` (limit 1–1000, offset ≥ 0)
- `routes.py` : constantes `/v1/production/regional`, `/v1/export/csv`
- 50 tests dans `tests/test_api_endpoints.py` couvrant : error handlers, models, routes, production_service, export_service, HTTP integration, performance (<500ms NFR-P2)
- Suite complète : 160 tests passés, 0 régression

### File List

- `functions/__init__.py` [NEW]
- `functions/shared/api/__init__.py` [NEW]
- `functions/shared/api/models.py` [NEW]
- `functions/shared/api/routes.py` [NEW]
- `functions/shared/api/error_handlers.py` [NEW]
- `functions/shared/api/production_service.py` [NEW]
- `functions/shared/api/export_service.py` [NEW]
- `functions/function_app.py` [MODIFIED]
- `functions/shared/quality/gate_runner.py` [MODIFIED — fix yaml unbound]
- `tests/test_api_endpoints.py` [NEW]

### Change Log

- 2026-02-26: Story 4.1 implémentée — API endpoints production/regional + export/csv, 50 tests, 160 passed total
- 2026-02-26: Fix Pyright 3.3 — `functions/__init__.py` créé, `yaml` unbound corrigé

# Story 4.3: Automated Swagger/OpenAPI Documentation

Status: done

## Story

As a Developer,
I want to access a self-documenting API interface (Swagger UI),
so that I can easily test the endpoints and understand the data schema.

## Acceptance Criteria

1. **Given** the API service is running,
   **When** navigating to the `/docs` or `/swagger` URL,
   **Then** a functional Swagger UI is displayed with all available endpoints, schemas, and authentication requirements.

2. **Given** the Swagger UI,
   **When** inspecting an endpoint,
   **Then** request parameters, response schemas, and example responses are documented.

3. **Given** the authentication model,
   **When** viewing the Swagger UI,
   **Then** the Bearer token authentication requirement is clearly documented.

## Tasks / Subtasks

- [x] Task 1: OpenAPI spec generation (AC: #1, #2)

  - [x] 1.1: Create `shared/api/openapi_spec.py` — programmatically generate OpenAPI 3.0 spec
  - [x] 1.2: Document all endpoints: `/v1/production/regional`, `/v1/export/csv`, `/health`
  - [x] 1.3: Define request parameter schemas (query params with types, descriptions, examples)
  - [x] 1.4: Define response schemas (JSON structure, field descriptions, example values)

- [x] Task 2: Swagger UI integration (AC: #1)

  - [x] 2.1: Create HTTP-triggered function serving Swagger UI at `/docs`
  - [x] 2.2: Use `swagger-ui-dist@5` CDN — no bundled assets
  - [x] 2.3: Serve OpenAPI spec JSON at `/api/openapi.json`

- [x] Task 3: Security documentation (AC: #3)

  - [x] 3.1: Add `securitySchemes` to OpenAPI spec: BearerAuth JWT via Azure AD
  - [x] 3.2: Mark protected endpoints with `security: [{BearerAuth: []}]`
  - [x] 3.3: Include token acquisition instructions in API description

- [x] Task 4: Tests (AC: #1, #2, #3)

  - [x] 4.1: Validate generated OpenAPI spec against OpenAPI 3.0 schema (structural)
  - [x] 4.2: Test Swagger UI HTML — CDN, mount point, title, spec URL
  - [x] 4.3: Verify all defined endpoints exist in spec with correct params/schemas

## Dev Notes

### Architecture Requirements

- **OpenAPI version:** 3.0.3
- **Approach:** Since Azure Functions v2 doesn't have built-in OpenAPI support, generate spec programmatically or use `azure-functions-openapi-extension`
- **Alternative:** If too complex, serve a handcrafted `openapi.yaml` as static file + Swagger UI HTML
- **Swagger UI:** Use CDN `https://unpkg.com/swagger-ui-dist@latest/` to avoid bundling

### Dependencies

- Story 4.1: API endpoints to document
- Story 4.2: Auth scheme to document

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 4.3] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR14] — Swagger/OpenAPI documentation

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_aucun blocage_

### Completion Notes List

- `shared/api/openapi_spec.py` : `build_spec()` génère OpenAPI 3.0.3 complet ; `build_swagger_ui_html()` retourne le HTML CDN
- `routes.py` : `ROUTE_DOCS`, `ROUTE_OPENAPI_JSON` ajoutés ; `PUBLIC_ROUTES` étendu aux 3 routes publiques
- `function_app.py` : 3 nouveaux HTTP triggers — GET `/health` (200 + version), GET `/openapi.json` (JSON spec), GET `/docs` (Swagger UI HTML)
- Spec couvre : info, servers, tags, 3 paths avec params/schemas/examples, components (BearerAuth + 3 schemas)
- Endpoints protégés (`/v1/*`) marqués `security: [{BearerAuth: []}]` ; `/health` marqué `security: []`
- 40 tests dans `tests/test_openapi.py` : structure spec, couverture endpoints, paramètres, schémas, sécurité, Swagger UI HTML, classification routes
- 228 tests passés total, 0 régression

### File List

- `functions/shared/api/openapi_spec.py` [NEW]
- `functions/shared/api/routes.py` [MODIFIED — ROUTE_DOCS, ROUTE_OPENAPI_JSON, PUBLIC_ROUTES étendu]
- `functions/function_app.py` [MODIFIED — 3 HTTP triggers: health, openapi.json, docs]
- `tests/test_openapi.py` [NEW]

### Change Log

- 2026-02-26: Story 4.3 implémentée — OpenAPI 3.0.3 spec, Swagger UI, /health, 40 tests, 228 total

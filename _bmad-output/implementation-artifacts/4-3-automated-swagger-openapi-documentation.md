# Story 4.3: Automated Swagger/OpenAPI Documentation

Status: ready-for-dev

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

- [ ] Task 1: OpenAPI spec generation (AC: #1, #2)
  
  - [ ] 1.1: Create `shared/api/openapi_spec.py` — programmatically generate OpenAPI 3.0 spec
  - [ ] 1.2: Document all endpoints: `/v1/production/regional`, `/v1/export/csv`, `/health`
  - [ ] 1.3: Define request parameter schemas (query params with types, descriptions, examples)
  - [ ] 1.4: Define response schemas (JSON structure, field descriptions, example values)

- [ ] Task 2: Swagger UI integration (AC: #1)
  
  - [ ] 2.1: Create HTTP-triggered function serving Swagger UI at `/docs` or `/api/docs`
  - [ ] 2.2: Use `swagger-ui-dist` CDN or embed static HTML with Swagger UI
  - [ ] 2.3: Serve OpenAPI spec JSON at `/api/openapi.json`

- [ ] Task 3: Security documentation (AC: #3)
  
  - [ ] 3.1: Add `securitySchemes` to OpenAPI spec: Bearer JWT via Azure AD
  - [ ] 3.2: Mark protected endpoints with security requirement
  - [ ] 3.3: Include token acquisition instructions in API description

- [ ] Task 4: Tests (AC: #1, #2, #3)
  
  - [ ] 4.1: Validate generated OpenAPI spec against OpenAPI 3.0 schema
  - [ ] 4.2: Test Swagger UI endpoint returns HTML with correct spec URL
  - [ ] 4.3: Verify all defined endpoints exist in spec

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

### Debug Log References

### Completion Notes List

### File List

### Change Log

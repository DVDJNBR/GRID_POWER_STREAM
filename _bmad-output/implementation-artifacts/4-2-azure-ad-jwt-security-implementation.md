# Story 4.2: Azure AD / JWT Security Implementation (C21)

Status: review

## Story

As a Security Officer,
I want to ensure that all non-public API endpoints require valid Azure AD credentials,
so that our energy data is protected against unauthorized access.

## Acceptance Criteria

1. **Given** an API request without a valid Bearer token,
   **When** accessing a protected endpoint,
   **Then** the API returns a 401 Unauthorized response.

2. **Given** a valid Bearer token,
   **When** the token is verified against the configured Azure AD tenant,
   **Then** the request is authorized and proceeds to the endpoint handler.

3. **Given** an expired or tampered token,
   **When** the token validation fails,
   **Then** the API returns 401 with a descriptive error message.

4. **Given** the security model (NFR-S1),
   **When** any non-public endpoint is accessed,
   **Then** 100% of requests require valid Azure AD JWT authentication.

## Tasks / Subtasks

- [x] Task 1: JWT validation middleware (AC: #1, #2, #3)

  - [x] 1.1: Create `shared/api/auth.py` — JWT Bearer token validation
  - [x] 1.2: Validate token against Azure AD tenant (issuer, audience, signing keys via JWKS endpoint)
  - [x] 1.3: Extract user claims (sub, oid, roles) for authorization context
  - [x] 1.4: Handle edge cases: expired token, invalid signature, missing token, malformed header

- [x] Task 2: Auth decorator/middleware (AC: #4)

  - [x] 2.1: Create `@require_auth` decorator for Azure Function HTTP triggers
  - [x] 2.2: Apply to all protected endpoints (`/v1/production/*`, `/v1/export/*`)
  - [x] 2.3: Allow optional public endpoints (e.g., `/health`, `/docs`) without auth

- [x] Task 3: Azure AD configuration (AC: #2)

  - [x] 3.1: Document App Registration setup in Azure AD (client_id, tenant_id)
  - [x] 3.2: Store Azure AD config in environment variables (AZURE_AD_TENANT_ID, AZURE_AD_CLIENT_ID)
  - [x] 3.3: Configure JWKS endpoint URL for token signature verification

- [x] Task 4: Tests (AC: #1, #2, #3, #4)

  - [x] 4.1: Unit tests for `auth.py` — valid token, expired token, invalid signature, missing token
  - [x] 4.2: Test `@require_auth` decorator — protected vs. public endpoints
  - [x] 4.3: Integration test — full auth flow with mock Azure AD responses

## Dev Notes

### Architecture Requirements

- **Library:** `PyJWT` (with `cryptography` for RS256) or `msal` for Microsoft-specific validation
- **Token validation:** Verify against Azure AD JWKS endpoint: `https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys`
- **Claims to validate:** `iss` (issuer), `aud` (audience = client_id), `exp` (expiration), `nbf` (not before)
- **No secrets:** Token validation uses public keys from JWKS — no client_secret needed for verification

### Security Model (from PRD)

- NFR-S1: 100% of non-public endpoints require valid JWT
- Protocol: JWT Bearer authentication (`Authorization: Bearer <token>`)
- Provider: Azure AD
- Preference: Tokens over static API keys for governance and auditability

### Dependencies

- Story 4.1: API endpoints to protect
- Azure AD: App Registration must be created (manual step, documented)

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 4.2] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-S1] — 100% JWT auth
- [Source: _bmad-output/planning-artifacts/prd.md#Authentication & Security Model] — Azure AD, JWT

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Test `test_full_flow_valid_token` : validator créé AVANT le patch env → tenant/client = "test-tenant"/"test-client" vs token signé avec vrais IDs → AuthError. Fix : `JWTValidator(tenant_id=tenant_id, client_id=client_id, jwks_override=jwks)` directement.

### Completion Notes List

- `shared/api/auth.py` : `JWTValidator` (RS256, JWKS cache, validates iss/aud/exp/nbf/sig), `AuthError`, `extract_bearer_token`, `@require_auth` decorator, `_make_401` (func.HttpResponse ou _Response selon environnement)
- `@require_auth` appliqué sur `get_production_regional` et `get_export_csv` dans `function_app.py`
- `routes.py` : `ROUTE_HEALTH` + `PUBLIC_ROUTES` set pour endpoints publics
- Env vars requis : `AZURE_AD_TENANT_ID`, `AZURE_AD_CLIENT_ID`
- JWKS URI : `https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys` (pas de client_secret, clés publiques uniquement)
- 28 tests dans `tests/test_auth.py` : JWTValidator (8), extract_bearer_token (6), @require_auth (9), intégration (3), routes (2)
- 188 tests passés total, 0 régression

### File List

- `functions/shared/api/auth.py` [NEW]
- `functions/shared/api/routes.py` [MODIFIED — ROUTE_HEALTH, PUBLIC_ROUTES]
- `functions/function_app.py` [MODIFIED — @require_auth sur 2 endpoints]
- `tests/test_auth.py` [NEW]

### Change Log

- 2026-02-26: Story 4.2 implémentée — Azure AD JWT auth, @require_auth decorator, 28 tests, 188 total

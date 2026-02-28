# Story M3: Milestone E4 — Documentation API REST & Application

Status: ready-for-dev

## Story

As a Student preparing for soutenance,
I want to document all E4 (API REST) deliverables including Swagger, security, dashboard, and alerting,
so that I have evidence of competencies C8, C9, C10, C11, C12 for my evaluation.

## Acceptance Criteria

1. **Given** all API and App stories are complete (4.1 → 5.2),
   **When** this milestone is executed,
   **Then** all evidence is captured in `docs/milestones/E4/`.

## Tasks / Subtasks

- [ ] Task 1: API evidence
  - [ ] 1.1: Capture Swagger UI page with all endpoints documented
  - [ ] 1.2: Capture sample API request/response (curl or Postman)
  - [ ] 1.3: Capture CSV export download
  - [ ] 1.4: Capture JWT authentication flow (token request → protected endpoint)
  - [ ] 1.5: Capture API performance metrics (response times < 500ms)

- [ ] Task 2: Dashboard evidence
  - [ ] 2.1: Capture dashboard homepage (charts, KPIs, region selector)
  - [ ] 2.2: Capture region-specific view with production breakdown
  - [ ] 2.3: Capture responsive design (mobile + desktop views)
  - [ ] 2.4: Capture alert banner when over-production is detected

- [ ] Task 3: Security evidence
  - [ ] 3.1: Capture Azure AD App Registration configuration
  - [ ] 3.2: Capture RBAC role assignments (SQL read-only for API)
  - [ ] 3.3: Capture 401 response for unauthenticated request

- [ ] Task 4: Summary report
  - [ ] 4.1: Create `docs/milestones/E4/rapport_api_application.md` — endpoints, security, UX
  - [ ] 4.2: Map evidence to competencies (C8→C12)

## Dependencies

- Stories 4.1, 4.2, 4.3, 5.1, 5.2 must be complete

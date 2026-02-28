# QA Story Review Report 🧪

**Date:** 2026-02-24
**Reviewer:** Quinn (QA Engineer)
**Scope:** 16 stories — Acceptance Criteria quality, testability, edge cases, consistency

---

## Summary

| Metric                 | Value |
| ---------------------- | ----- |
| Stories reviewed       | 16    |
| Issues found           | 12    |
| Critical (blocks dev)  | 2     |
| Important (should fix) | 6     |
| Minor (nice to have)   | 4     |

---

## 🔴 Critical Issues

### C1. Story 1.1 — AC missing for empty API response

**Story:** 1.1 (RTE API Ingestion)
**Problem:** No AC covers the case where the API returns a valid 200 response but with an **empty dataset** (e.g., no data for the requested time range). This will happen frequently during initial development and off-peak testing.
**Recommendation:** Add AC #5:

```
Given a valid API response with zero records,
When the function processes the response,
Then no file is written to Bronze, and the heartbeat logs "0 records" without triggering an error.
```

### C2. Story 3.2 — AC #3 "upsert" not testable as written

**Story:** 3.2 (Silver to Gold)
**Problem:** AC #3 says "DIM tables are upserted" but doesn't specify the deterministic key for upsert. Without this, the dev agent may implement INSERT+duplicate conflict instead of proper MERGE.
**Recommendation:** Add explicit upsert keys:

- DIM_REGION: upsert on `code_insee`
- DIM_TIME: upsert on `horodatage`
- DIM_SOURCE: upsert on `source_name`

---

## 🟡 Important Issues

### I1. Story 0.1 — No failure criteria for exploration

**Story:** 0.1 (API Exploration)
**Problem:** All ACs describe success cases. What if the API is down, requires paid access, or returns unexpected format?
**Recommendation:** Add AC:

```
Given the RTE API is inaccessible or returns unexpected format,
When the exploration cannot proceed,
Then the blocker is documented and escalated before proceeding to Story 1.0.
```

### I2. Story 1.0 — Terraform `destroy` safety not addressed

**Story:** 1.0 (Terraform IaC)
**Problem:** No AC prevents accidental `terraform destroy` on production data. With a student budget, data loss = project restart.
**Recommendation:** Add `prevent_destroy = true` lifecycle rule on ADLS Gen2 and SQL in dev notes.

### I3. Story 1.2 — CSV encoding not specified

**Story:** 1.2 (CSV Ingestion)
**Problem:** French CSV files commonly use `ISO-8859-1` or `Windows-1252` encoding, not UTF-8. Accent characters (région, éolien) will corrupt silently.
**Recommendation:** Add to dev notes: "Detect encoding with `chardet` or assume `UTF-8` with `ISO-8859-1` fallback. Log detected encoding in audit."

### I4. Story 2.1 — No AC for "portal structure changed"

**Story:** 2.1 (Web Scraping)
**Problem:** Web scraping is fragile — the portal HTML structure can change at any time. No AC handles this.
**Recommendation:** Add AC:

```
Given the portal HTML structure has changed,
When parsing fails,
Then an error is logged with a diff of expected vs. actual selectors.
```

### I5. Story 4.1 — AC #2 "<500ms" not verifiable without benchmark data

**Story:** 4.1 (API Endpoints)
**Problem:** The 500ms performance target (NFR-P2) can't be verified without knowing dataset size. 500ms on 10 rows ≠ 500ms on 100,000 rows.
**Recommendation:** Specify: "Response < 500ms for queries returning ≤ 1000 rows with proper indexing on Azure SQL Serverless."

### I6. Stories 3.1–3.3 — No idempotency guarantee documented

**Story:** 3.1, 3.2, 3.3 (Medallion pipeline)
**Problem:** If a Silver or Gold transformation runs twice on the same data, will it produce duplicates? No AC specifies idempotency.
**Recommendation:** Add AC to Story 3.1:

```
Given the same Bronze data is processed twice,
When Silver transformation runs,
Then the output is identical (idempotent — no duplicate rows).
```

---

## 🟢 Minor Issues

### M1. Story 1.3 — Staleness threshold should have a test case for boundary values

**Recommendation:** Add test case for exactly 24h boundary (23h59 = active, 24h01 = stale).

### M2. Story 4.2 — Missing test for expired token refresh

**Recommendation:** Add test: token acquired, wait for expiry, verify re-auth flow.

### M3. Story 5.1 — No AC for "API unavailable" dashboard state

**Recommendation:** Add: dashboard shows "Service unavailable" state instead of blank/broken.

### M4. All stories — Test task descriptions could specify framework explicitly

**Recommendation:** Each story's test task should state: "pytest" (backend) or "vitest/jest" (frontend) explicitly.

---

## Dependency Chain Validation

```
0.1 → 1.0 → 1.1 → 1.2 → 1.3
                → 2.1
                → 2.2
                → 2.3
       1.0 ────→ 3.1 → 3.2 → 3.3
                        3.2 → 4.1 → 4.2 → 4.3
                                   → 5.1 → 5.2
```

**Dependency issues found:** None ✅ — All stories correctly reference their dependencies.

---

## Consistency Check

| Item                                          | Status |
| --------------------------------------------- | ------ |
| All stories have BDD format (Given/When/Then) | ✅     |
| All stories have Tasks with AC references     | ✅     |
| All stories have Dev Notes section            | ✅     |
| All stories have References section           | ✅     |
| All stories have Test tasks                   | ✅     |
| All stories have Dev Agent Record template    | ✅     |
| Naming convention consistent                  | ✅     |
| Status all `ready-for-dev`                    | ✅     |

---

## Verdict: 🟡 Solid but needs 8 fixes before dev

The stories are well-structured and consistent. The critical issues (C1, C2) should be fixed before launching dev. The important issues (I1–I6) would prevent common implementation errors.

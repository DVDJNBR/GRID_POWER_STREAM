# Story 2.1: Web Scraping of Grid Maintenance Portals

Status: ready-for-dev

## Story

As a Platform Builder,
I want to programmatically scrape the ENTSO-E or RTE transparency status pages,
so that we can capture scheduled downtime and maintenance events in the Bronze layer.

## Acceptance Criteria

1. **Given** the URL of the maintenance transparency portal,
   **When** the scraping Azure Function is triggered,
   **Then** the extracted HTML/JSON data (Event ID, Dates, Description) is saved in `bronze/maintenance/`.

2. **Given** a scraping run,
   **When** the data is successfully extracted,
   **Then** each maintenance event includes: event_id, start_date, end_date, description, affected_area, source_url.

3. **Given** common HTTP errors (404, 429, 503),
   **When** the scraper encounters an error,
   **Then** the error is handled gracefully with retry logic and logged.

4. **Given** the scraping competency requirement (C8),
   **When** the scraper runs,
   **Then** it demonstrates programmatic web scraping as a data source distinct from API calls.

## Tasks / Subtasks

- [ ] Task 1: Scraper module (AC: #1, #2, #4)
  - [ ] 1.1: Create `shared/maintenance_scraper.py` — target RTE or ENTSO-E transparency portal
  - [ ] 1.2: Implement HTML parsing using `parsel` (XPath + CSS selectors; fallback: `selectolax`) to extract maintenance event data
  - [ ] 1.3: Structure extracted data as JSON: `{event_id, start_date, end_date, description, affected_area, source_url, scraped_at}`
  - [ ] 1.4: Handle pagination if the portal uses multi-page listings

- [ ] Task 2: Bronze storage & trigger (AC: #1)
  - [ ] 2.1: Create timer-triggered function (hourly or configurable) for maintenance scraping
  - [ ] 2.2: Store scraped JSON in `bronze/maintenance/YYYY/MM/DD/maintenance_{timestamp}.json`
  - [ ] 2.3: Reuse `shared/audit_logger.py` for heartbeat logging

- [ ] Task 3: Error handling (AC: #3)
  - [ ] 3.1: Implement retry logic (reuse pattern from `shared/rte_client.py`)
  - [ ] 3.2: Handle anti-scraping measures: rate limiting, user-agent rotation, politeness delays
  - [ ] 3.3: Log errors with context (URL, HTTP status, response snippet)

- [ ] Task 4: Tests (AC: #1, #2, #3)
  - [ ] 4.1: Unit tests for `maintenance_scraper.py` — mock HTML responses, parse validation
  - [ ] 4.2: Unit tests for error handling — 404, 429, malformed HTML
  - [ ] 4.3: Integration test with saved HTML fixture files

## Dev Notes

### Architecture Requirements

- **Library:** `parsel` + `requests` (NOT Selenium/Playwright — keep serverless-compatible). Backup: `selectolax` si perf critique
- **Politeness:** Minimum 2-second delay between requests, respect `robots.txt`
- **User-Agent:** Custom descriptive string (`GRID_POWER_STREAM/1.0 DataIngestion`)
- **Target portals (investigate at implementation):**
  - RTE: `https://www.services-rte.com/fr/visualisez-les-donnees-publiees-par-rte/indisponibilites-des-moyens-de-production.html`
  - ENTSO-E: `https://transparency.entsoe.eu/outage-domain/r2/unavailabilityOfProductionAndGenerationUnits/show`
- **Fallback:** If portal is too complex to scrape, create a **simulated scraper** using a local HTML fixture that demonstrates the C8 competency

### Dependencies

- Story 1.0: ADLS Gen2 provisioned
- Story 1.1: Shared modules (`audit_logger.py`, `bronze_storage.py`, retry patterns)

### Bronze Storage Convention

```
bronze/
  maintenance/
    YYYY/
      MM/
        DD/
          maintenance_{ISO8601_timestamp}.json
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.1] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR3] — Web scraping requirement (C8)
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md#MAINTENANCE] — Maintenance entity model

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log

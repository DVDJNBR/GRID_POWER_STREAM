# Story 5.2: Over-Production & Negative Price Alerts

Status: ready-for-dev

## Story

As a Grid Manager (Marc),
I want to receive visual alerts when production exceeds demand or when prices are at risk of turning negative,
so that I can preemptively adjust the grid maintenance or export strategies.

## Acceptance Criteria

1. **Given** the 15-minute data ingestion cycle,
   **When** the production-to-demand ratio exceeds the safety threshold (Alerting Logic),
   **Then** a high-priority "Risk Alert" is displayed on the dashboard.

2. **Given** an alert condition,
   **When** the alert is triggered,
   **Then** the event is logged in the audit trail for later review.

3. **Given** the alerting system,
   **When** configuring thresholds,
   **Then** the safety threshold is configurable (default: production > 110% of demand).

4. **Given** the negative price detection,
   **When** production peaks coincide with low demand,
   **Then** a "Negative Price Risk" warning is generated with estimated severity.

## Tasks / Subtasks

- [ ] Task 1: Alert detection engine (AC: #1, #3, #4)
  - [ ] 1.1: Create `shared/alerting/alert_engine.py` — evaluate alert rules against latest Gold data
  - [ ] 1.2: Implement over-production rule: `production_total / consommation > threshold` (default 1.10)
  - [ ] 1.3: Implement negative price risk rule: production peak + low demand + historical price correlation
  - [ ] 1.4: Make thresholds configurable via environment variables (`OVERPRODUCTION_THRESHOLD`, `NEGATIVE_PRICE_THRESHOLD`)

- [ ] Task 2: Alert storage & API (AC: #1, #2)
  - [ ] 2.1: Create `alerts` table in SQL or JSON store in ADLS: `{alert_id, type, severity, region, timestamp, details, acknowledged}`
  - [ ] 2.2: Create API endpoint: `GET /v1/alerts?region_code={}&status=active` (extends Story 4.1)
  - [ ] 2.3: Integrate alert evaluation into the Silver→Gold pipeline trigger (post-transformation)
  - [ ] 2.4: Log all alerts to audit system

- [ ] Task 3: Dashboard alert integration (AC: #1)
  - [ ] 3.1: Create `AlertBanner.jsx` component — dismissible, color-coded (red=critical, orange=warning)
  - [ ] 3.2: Create `AlertHistory.jsx` — list view of recent alerts with timestamps
  - [ ] 3.3: Add real-time alert polling (every 60 seconds) or WebSocket for instant display
  - [ ] 3.4: Add visual indicator: pulsing icon in header when active alerts exist

- [ ] Task 4: Tests (AC: #1, #2, #3, #4)
  - [ ] 4.1: Unit tests for `alert_engine.py` — over-production trigger, threshold config, edge cases
  - [ ] 4.2: Unit tests for negative price detection logic
  - [ ] 4.3: Component tests for `AlertBanner.jsx` — render states (active, dismissed, empty)
  - [ ] 4.4: Integration test — Gold data trigger → alert creation → API response → dashboard display

## Dev Notes

### Architecture Requirements

- **Alert evaluation:** Runs as part of the Gold transformation pipeline (not a separate trigger)
- **Storage:** Prefer SQL table `ALERTS` for queryability, or JSON file in `bronze/audit/alerts/` for simplicity
- **Severity levels:** CRITICAL (immediate action), WARNING (monitor), INFO (informational)
- **Dashboard integration:** Polling-based (REST API) — WebSocket adds unnecessary complexity for 15-min data

### Alert Logic

```python
# Over-production detection
ratio = total_production_mw / total_consumption_mw
if ratio > OVERPRODUCTION_THRESHOLD:
    create_alert(type="OVERPRODUCTION", severity="CRITICAL", details=f"Ratio: {ratio:.2f}")

# Negative price risk (simplified)
if ratio > NEGATIVE_PRICE_THRESHOLD and is_low_demand_period(hour):
    create_alert(type="NEGATIVE_PRICE_RISK", severity="WARNING", details=f"Peak production during low demand")
```

### Dependencies

- Story 3.2: Gold data available for evaluation
- Story 4.1: API endpoints to extend
- Story 5.1: Dashboard to display alerts

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 5.2] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR17,FR18] — Over-production alerts, negative price detection
- [Source: _bmad-output/planning-artifacts/prd.md#Risk Mitigations] — Curtailment alerting logic

> [!IMPORTANT]
> 🎯 **Après cette story → exécuter Story M3 (Milestone E4 — Documentation API & Application)**

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log

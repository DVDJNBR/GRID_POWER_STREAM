# Story 3.3: Data Quality Gates & Integrity Checks

Status: ready-for-dev

## Story

As a Data Governor,
I want to implement automated quality checks between the Silver and Gold layers,
so that we ensure the integrity of the metrics served to the API.

## Acceptance Criteria

1. **Given** the completion of a Gold ingestion job,
   **When** the quality gate script runs,
   **Then** it verifies that row counts match expectations and mandatory fields are non-null.

2. **Given** a quality check failure,
   **When** the validation detects an anomaly,
   **Then** an alert is triggered in the audit logs with severity and details.

3. **Given** the quality gate framework,
   **When** new checks are needed,
   **Then** they can be added declaratively (config-driven) without code changes.

## Tasks / Subtasks

- [ ] Task 1: Quality gate framework (AC: #1, #3)
  - [ ] 1.1: Create `shared/quality/gate_runner.py` — config-driven quality check executor
  - [ ] 1.2: Create `shared/quality/checks.py` — individual check implementations (row count, null check, range check, freshness)
  - [ ] 1.3: Create `config/quality_gates.yaml` — declarative check definitions per layer/table

- [ ] Task 2: Silver layer checks (AC: #1)
  - [ ] 2.1: Row count comparison: Bronze source count vs Silver output count (within tolerance %)
  - [ ] 2.2: Null check: mandatory fields (`code_insee_region`, `date_heure`, `valeur_mw`) must be non-null
  - [ ] 2.3: Range check: MW values within reasonable bounds (0–100,000 MW for France)
  - [ ] 2.4: Freshness check: latest `date_heure` within expected window

- [ ] Task 3: Gold layer checks (AC: #1)
  - [ ] 3.1: Referential integrity: all FACT FK values exist in corresponding DIM tables
  - [ ] 3.2: Completeness: all active DIM_REGION entries have recent FACT rows
  - [ ] 3.3: Calculation validation: `facteur_charge` between 0 and 1 (or flagged)

- [ ] Task 4: Alerting & reporting (AC: #2)
  - [ ] 4.1: Integrate with `shared/audit_logger.py` — log check results (pass/fail/warn)
  - [ ] 4.2: Generate quality report JSON in `bronze/audit/quality/YYYY/MM/DD/`
  - [ ] 4.3: Define severity levels: CRITICAL (halt pipeline), WARNING (log + continue), INFO

- [ ] Task 5: Tests (AC: #1, #2, #3)
  - [ ] 5.1: Unit tests for each check type with pass/fail fixtures
  - [ ] 5.2: Test config-driven gate runner with sample YAML
  - [ ] 5.3: Integration test — run gates against fixture data

## Dev Notes

### Architecture Requirements

- **Config-driven:** Quality checks defined in YAML, not hardcoded — extensible
- **Severity model:** CRITICAL = halt pipeline + alert, WARNING = log + continue, INFO = log only
- **Run timing:** Quality gates run after each Silver and Gold transformation
- **Tolerance:** Row count checks allow configurable tolerance (default ±5%)

### Quality Gate YAML Format

```yaml
gates:
  - name: "silver_rte_null_check"
    layer: silver
    table: rte/production
    check: null_check
    columns: ["code_insee_region", "date_heure"]
    severity: CRITICAL

  - name: "gold_fact_referential_integrity"
    layer: gold
    table: FACT_ENERGY_FLOW
    check: fk_exists
    fk_columns:
      { id_region: DIM_REGION, id_date: DIM_TIME, id_source: DIM_SOURCE }
    severity: CRITICAL
```

### Dependencies

- Story 3.1: Silver data to validate
- Story 3.2: Gold data to validate
- Story 1.1: Audit logger module

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.3] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR11] — Data integrity validation
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-R2] — Monitoring & audit

> [!IMPORTANT]
> 🎯 **Après cette story → exécuter Story M2 (Milestone E5 — Documentation Data Warehouse)**

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log

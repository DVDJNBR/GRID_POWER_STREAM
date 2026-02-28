# Story M2: Milestone E5 — Documentation Data Warehouse

Status: ready-for-dev

## Story

As a Student preparing for soutenance,
I want to document all E5 (Data Warehouse) deliverables with evidence of ETL, Star Schema, and quality gates,
so that I have evidence of competencies C13, C14, C15 for my evaluation.

## Acceptance Criteria

1. **Given** all DW stories are complete (3.1 → 3.3),
   **When** this milestone is executed,
   **Then** all evidence is captured in `docs/milestones/E5/`.

## Tasks / Subtasks

- [ ] Task 1: Star Schema evidence
  - [ ] 1.1: Capture Azure SQL schema (table list, column details)
  - [ ] 1.2: Capture DIM tables populated with real data (SELECT TOP 10)
  - [ ] 1.3: Capture FACT table with sample rows showing FK joins
  - [ ] 1.4: Generate ER diagram from SQL metadata

- [ ] Task 2: ETL pipeline evidence
  - [ ] 2.1: Capture Silver Parquet files (partitioned structure in ADLS)
  - [ ] 2.2: Capture transformation logs (rows processed, nulls handled)
  - [ ] 2.3: Document Bronze → Silver → Gold data flow with row counts
  - [ ] 2.4: Capture Gold cleanup job execution (retention policy in action)

- [ ] Task 3: Quality gates evidence
  - [ ] 3.1: Capture quality gate report (pass/fail checks)
  - [ ] 3.2: Document data quality metrics (null %, duplicate %, freshness)

- [ ] Task 4: Summary report
  - [ ] 4.1: Create `docs/milestones/E5/rapport_data_warehouse.md` — schema design, ETL logic, quality
  - [ ] 4.2: Map evidence to competencies (C13→C15)

## Dependencies

- Stories 3.1, 3.2, 3.3 must be complete

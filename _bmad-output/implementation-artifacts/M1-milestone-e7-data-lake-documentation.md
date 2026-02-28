# Story M1: Milestone E7 — Documentation Data Lake

Status: ready-for-dev

## Story

As a Student preparing for soutenance,
I want to document all E7 (Data Lake) deliverables with screenshots and architecture diagrams,
so that I have evidence of competencies C18, C19, C20, C21 for my evaluation.

## Acceptance Criteria

1. **Given** all Data Lake stories are complete (0.1 → 2.3),
   **When** this milestone is executed,
   **Then** all evidence is captured and organized in `docs/milestones/E7/`.

## Tasks / Subtasks

- [ ] Task 1: Azure Portal screenshots
  - [ ] 1.1: Capture Resource Group overview (all resources visible)
  - [ ] 1.2: Capture ADLS Gen2 containers (bronze/, silver/, gold/) with sample files
  - [ ] 1.3: Capture Storage Lifecycle Policies (retention rules active)
  - [ ] 1.4: Capture Key Vault secrets list (names only, not values)
  - [ ] 1.5: Capture Azure Function App overview + function list

- [ ] Task 2: Terraform evidence
  - [ ] 2.1: Capture `terraform plan` output (infrastructure summary)
  - [ ] 2.2: Save `terraform state list` output
  - [ ] 2.3: Architecture diagram (Resource Group → services → data flow)

- [ ] Task 3: Data pipeline evidence
  - [ ] 3.1: Capture Bronze folder structure with real ingested data
  - [ ] 3.2: Capture audit logs showing successful ingestion runs
  - [ ] 3.3: Capture Function execution logs (Application Insights)
  - [ ] 3.4: Document the 5 data sources and extraction methods (C8)

- [ ] Task 4: Summary report
  - [ ] 4.1: Create `docs/milestones/E7/rapport_data_lake.md` — architecture, decisions, retention policies
  - [ ] 4.2: Map each screenshot to its competency (C18→C21)

## Dependencies

- Stories 0.1, 1.0, 1.1, 1.2, 1.3, 2.1, 2.2, 2.3 must be complete

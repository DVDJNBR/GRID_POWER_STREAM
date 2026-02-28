# Sprint Change Proposal — Epic Resequencing for Exploratory Schema Design

**Date:** 2026-02-24
**Requested by:** David
**Scope:** Moderate — Backlog reorganization

---

## 1. Issue Summary

**Problem:** The current epic/story sequencing assumes a pre-defined Star Schema (DIM/FACT tables) is provisioned via Terraform (Story 1.0) BEFORE any data exploration. However, the PRD explicitly states:

> _"Exploratory Schema Modeling: Final Gold layer SQL schema will be derived from a **discovery phase** of the RTE API response formats to ensure 100% field mapping accuracy."_

The correct workflow should be:

1. **Explore** the RTE API → understand real data structure
2. **Design** the SQL schema based on actual API responses
3. **Provision** infrastructure (Terraform) WITH the validated schema

**Discovery:** Identified during story review before any implementation work, so no rollback is needed.

---

## 2. Impact Analysis

### Epic Impact

| Epic         | Impact            | Details                                                          |
| ------------ | ----------------- | ---------------------------------------------------------------- |
| **Epic 1**   | 🔴 **Resequence** | Stories must be reordered: exploration before infra provisioning |
| **Epic 2**   | 🟢 No impact      | Independent data sources, no dependency on schema                |
| **Epic 3**   | 🟢 No impact      | Depends on Bronze/Silver data, schema already exists by then     |
| **Epic 4–5** | 🟢 No impact      | Downstream consumers, unchanged                                  |

### Story Impact

| Story               | Change        | Rationale                                                                                                                                       |
| ------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **[NEW] Story 0.1** | **Add**       | API Exploration & Schema Discovery — interactive exploration of RTE eCO2mix API responses, design SQL schema from real data                     |
| **Story 1.0**       | **Modify**    | Remove SQL schema creation from Terraform (Task 4) → instead reference the schema produced by Story 0.1, run schema SQL from exploration output |
| **Story 1.1**       | **No change** | Content is correct, but execution now depends on Story 0.1 (API already explored) and Story 1.0 (infra provisioned)                             |
| **Stories 1.2–5.2** | **No change** | Content unchanged                                                                                                                               |

### Artifact Conflicts

- **PRD:** No conflict — PRD already supports exploratory approach
- **Architecture (CONCEPTION_TECHNIQUE):** Schema section may need updating after exploration results, but this is expected
- **CONCEPTION_DATAMODEL:** Current MCD/MLD/MPD is a starting point — will be validated/adjusted after exploration

---

## 3. Recommended Approach: Direct Adjustment

**Selected path:** Direct Adjustment — add new story + modify story 1.0 + resequence

**Why this works:**

- No code has been written yet — zero rollback risk
- Story content is mostly correct, only ordering and one new story needed
- PRD/architecture remain valid
- Effort: **Low** — write one new story, edit one existing story
- Risk: **Low** — clarifies dependencies, reduces future rework

---

## 4. Proposed Changes

### Change 1: Add Story 0.1 — API Exploration & Schema Discovery

**New story at the start of Epic 1.** Interactive exploration of all data sources (primarily RTE API), producing:

- Documented API response structure
- Validated SQL schema (`init_schema.sql`) based on real data
- Sample data fixtures for testing

### Change 2: Modify Story 1.0 — Infrastructure as Code

**Remove:** Task 4 (SQL schema initialization with hardcoded DIM/FACT tables)
**Replace:** Task 4 becomes "Apply schema from Story 0.1 output" — Terraform runs the SQL script produced during exploration

### Change 3: Resequence Epic 1

**Current order:** 1.0 → 1.1 → 1.2 → 1.3
**New order:** **0.1** → 1.0 → 1.1 → 1.2 → 1.3

---

## 5. Implementation Handoff

**Scope classification:** Moderate — backlog reorganization

**Actions required:**

1. **SM (Bob):** Create Story 0.1, modify Story 1.0, update epics.md ordering
2. **Dev (Amelia):** Implement stories in new sequence starting with 0.1

**Success criteria:**

- Story 0.1 exists with clear tasks for API exploration
- Story 1.0 no longer contains hardcoded schema — references exploration output
- Epic 1 stories are in correct dependency order

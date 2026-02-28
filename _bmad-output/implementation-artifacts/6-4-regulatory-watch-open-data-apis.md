# Story 6.4: Regulatory Watch — Open Data & Public APIs in Europe

Status: backlog

## Story

As a Platform Builder,
I want to conduct a regulatory watch on the legal framework governing the use of public data and APIs in Europe,
so that GRID_POWER_STREAM is built on legally sound foundations and can expand to new sources and markets confidently.

## Scope (as defined by Winston, Architect — 2026-02-27)

This is NOT a narrow compliance check on EU 543/2013 alone (already covered lightly in story 6-1).
The scope is a **broad legal landscape review** covering:

1. **EU Open Data Directive 2019/1024** — framework for reuse of public sector data across the EU.
   Governs why RTE, ENTSO-E and other TSOs are legally required to publish their data,
   and what reuse rights downstream consumers (like us) have.

2. **REMIT** (Regulation on Energy Market Integrity and Transparency) — EU energy market regulation.
   Relevant if the project expands to market prices, spot data, or trading-adjacent metrics.

3. **Web scraping legal landscape in Europe** — no unified law yet, but case law evolving.
   Key question: is scraping ENTSO-E transparency portal legally sound under EU law?

4. **Open data licence comparison** — Licence Ouverte Etalab (FR) vs ODbL vs CC-BY vs Open Government Licence (UK).
   Attribution requirements and share-alike conditions vary — impacts commercial deployment.

5. **Geographic expansion** — if adding non-French TSO sources (BNetzA/DE, REE/ES, Elia/BE, National Grid/UK),
   each has its own API terms and licence. A comparative table would be a reusable asset.

## Expected Deliverable

A **legal source dashboard** document covering:
- Table: source → licence → attribution required → commercial use allowed → scraping allowed
- Summary of EU 543/2013 + REMIT relevance to the project
- Red flags / risks to mitigate before commercial deployment
- Recommendations for footer attributions and terms of service compliance

## Immediate action (pre-deployment, not blocked on this story)

> Add footer "Source : RTE Open Data (Licence Ouverte v2 / Etalab)" to dashboard before any public deployment.
> This is a 1-line HTML change — does NOT require this story to be completed first.

## Dependencies

- None blocking — pure research story
- Useful context for any future geographic expansion epic

## Priority

🟡 **Later** — after prototype is stable and deployed. Not blocking jury demo.

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (Architect — Winston)

### Debug Log References

### Completion Notes List

### File List

- `_bmad-output/implementation-artifacts/6-4-regulatory-watch-open-data-apis.md` (this file)

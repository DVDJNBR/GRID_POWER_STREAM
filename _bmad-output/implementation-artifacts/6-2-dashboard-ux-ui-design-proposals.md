# Story 6.2: Dashboard UX/UI Design Proposals

Status: ready-for-dev

## Story

As a UX/UI Designer,
I want to review the data & feature brief from story 6-1 and propose wireframes, layout options, and interaction patterns for the GRID_POWER_STREAM dashboard,
so that the development team has a clear visual direction before committing to any frontend tooling.

## Acceptance Criteria

1. **Given** the MoSCoW feature list from story 6-1,
   **When** the UX analysis is complete,
   **Then** at least 2 layout variants are proposed for the main dashboard view (e.g. map-centric vs. chart-centric), with ASCII wireframes or structured mockup descriptions.

2. **Given** the two personas (Technical Auditor / Wind Farm Manager),
   **When** layouts are proposed,
   **Then** each variant is evaluated against both personas — noting which persona it serves best and why.

3. **Given** the geo-dimension decision from story 6-1 (Task 5),
   **When** the geographic component is designed,
   **Then** the UX agent provides a concrete recommendation (choroplèthe map vs. region selector) with UX rationale (cognitive load, data density, mobile vs. desktop).

4. **Given** the time-series nature of production data,
   **When** chart types are recommended,
   **Then** the agent justifies each chart type choice (area, bar, gauge, etc.) against the data shape and user goal — not just aesthetics.

5. **Given** the existing React frontend (story 5-1) already has dark/light theme, glassmorphism, KPI cards and a region selector,
   **When** proposals are made,
   **Then** the agent explicitly notes what to keep, what to redesign, and what to add — avoiding a full rewrite if unnecessary.

6. **Given** potential tool change (Taipy / other — story 6-3 benchmark),
   **When** design proposals are written,
   **Then** each proposal is flagged as "tool-agnostic" or "React-specific" so the dev benchmark agent can factor this in.

## Tasks / Subtasks

- [ ] Task 1 — Analyse du brief 6-1 (AC: #1, #2)
  - [ ] 1.1 Lire le livrable de story 6-1 (liste MoSCoW + décision géo + rétention)
  - [ ] 1.2 Identifier les contraintes UX issues des données (sparse data, refresh 15 min, 12 régions)
  - [ ] 1.3 Analyser l'existant React (App.jsx, KPICard, ProductionChart, RegionSelector, CarbonGauge)

- [ ] Task 2 — Proposition de layouts (AC: #1, #2)
  - [ ] 2.1 Variant A : Chart-centric — sidebar région, KPIs en haut, charts en grille
  - [ ] 2.2 Variant B : Map-centric — carte choroplèthe France en hero, charts secondaires
  - [ ] 2.3 Wireframe ASCII ou description structurée pour chaque variant
  - [ ] 2.4 Scoring persona : Auditeur technique vs. Gestionnaire parc éolien

- [ ] Task 3 — Recommandation géo (AC: #3)
  - [ ] 3.1 Trancher choroplèthe vs. sélecteur avec justification UX
  - [ ] 3.2 Si carte : préciser le niveau d'interactivité requis (hover, click, zoom ?)
  - [ ] 3.3 Si sélecteur : proposer une amélioration vs. dropdown actuel (autocomplete, flags régionaux ?)

- [ ] Task 4 — Recommandations chart types (AC: #4)
  - [ ] 4.1 Production par source → area chart empilé ou grouped bar ?
  - [ ] 4.2 Intensité carbone → gauge, sparkline ou badge coloré ?
  - [ ] 4.3 Facteur de charge → bullet chart ou progress bar ?
  - [ ] 4.4 Mix énergétique → donut chart ou stacked percentage bar ?
  - [ ] 4.5 Time-series historique → brush/zoom recommandé ?

- [ ] Task 5 — Delta avec l'existant (AC: #5)
  - [ ] 5.1 Lister ce qui est à conserver (composants React story 5-1)
  - [ ] 5.2 Lister ce qui est à retravailler (layout, interactions manquantes)
  - [ ] 5.3 Lister les nouveaux composants nécessaires

- [ ] Task 6 — Tagging tool-agnostic vs. React-specific (AC: #6)
  - [ ] 6.1 Pour chaque composant proposé, noter si la recommandation tient quel que soit l'outil
  - [ ] 6.2 Identifier les éléments qui seraient difficiles à implémenter hors React (animations, SSO MSAL, etc.)

## Dev Notes

### Inputs requis (dépendances)

- **Story 6-1 livrable** — liste MoSCoW finalisée + décision géo + rétention recommandée
- **Code existant story 5-1** :
  - `frontend/src/App.jsx` — layout actuel
  - `frontend/src/components/KPICard.jsx`
  - `frontend/src/components/ProductionChart.jsx` (Recharts AreaChart)
  - `frontend/src/components/RegionSelector.jsx`
  - `frontend/src/components/CarbonGauge.jsx`
  - `frontend/src/index.css` — variables CSS, thème dark/light, glassmorphism

### Contraintes à respecter

- **Pas de redesign complet** si l'existant est réutilisable — éviter la dette de migration
- **Mobile-friendly** recommandé mais pas bloquant pour le prototype jury
- **Performance** : les charts doivent rester réactifs avec refresh 15 min et ~400 data points max
- **Accessibilité** : aria-live déjà en place (story 5-1) — maintenir le niveau

### Personas de référence

- **Marc (Wind Farm Manager)** : veut voir la production régionale, les alertes et le mix énergétique — priorité opérationnelle
- **Technical Auditor (Jury)** : veut voir la data pipeline end-to-end, la qualité des données, la couverture des sources — priorité technique

### Livrable attendu

Document de design dans ce fichier story (section Completion Notes) contenant :
- 2 wireframes ASCII ou descriptions structurées de layouts
- Tableau de recommandations chart types avec justification
- Recommandation géo argumentée
- Liste delta keep/redesign/add vs. story 5-1
- Tag tool-agnostic / React-specific par composant

### Project Structure Notes

- Story de **discovery design** — pas de code produit
- Output alimente directement story 6-3 (benchmark) et la future story d'implémentation dashboard v2

### References

- Composants existants : `frontend/src/components/` [Source: story 5-1]
- PRD personas : [Source: `_bmad-output/planning-artifacts/prd.md` §User Journeys]
- Feature list MoSCoW : [Source: story 6-1 livrable]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (SM story preparation)

### Debug Log References

### Completion Notes List

### File List

- `_bmad-output/implementation-artifacts/6-2-dashboard-ux-ui-design-proposals.md` (this file)

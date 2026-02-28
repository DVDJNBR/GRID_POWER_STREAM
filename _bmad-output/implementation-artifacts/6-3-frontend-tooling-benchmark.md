# Story 6.3: Frontend Tooling Benchmark

Status: ready-for-dev

## Story

As a Senior Developer,
I want to benchmark the viable frontend/dashboard tooling options against the confirmed feature requirements (story 6-1) and UX proposals (story 6-2),
so that the team makes an informed, justified tool choice before building the dashboard v2 — avoiding a costly mid-project migration.

## Acceptance Criteria

1. **Given** the MoSCoW feature list from story 6-1 and UX proposals from story 6-2,
   **When** the benchmark is complete,
   **Then** each candidate tool is scored against a set of defined criteria (geo, time-series, Python-native, customisation, maintenance, licensing).

2. **Given** the existing React + Recharts + Vite stack (story 5-1),
   **When** React is evaluated,
   **Then** it is treated as a candidate like the others — not assumed to win by default — with an honest assessment of what additional libraries would be needed.

3. **Given** the geo-visualisation requirement (choroplèthe or interactive map),
   **When** each tool is evaluated,
   **Then** its geo capability is tested/documented specifically: native support, required plugin, or "not possible".

4. **Given** the Python-native stack (Azure Functions + Polars + SQLite/Azure SQL),
   **When** Python-native tools are evaluated (Taipy, Streamlit, Panel, Plotly Dash),
   **Then** the integration path with the existing API layer is documented (does it bypass the REST API or consume it ?).

5. **Given** the prototype-first approach (jury deadline before production deploy),
   **When** tools are scored,
   **Then** a "prototype speed" criterion is included — how fast can a working demo be built from scratch ?

6. **Given** the final recommendation,
   **When** the benchmark document is delivered,
   **Then** a single tool is recommended with a clear rationale, AND a migration path is noted if the current React frontend is NOT chosen (what to reuse, what to rewrite).

## Tasks / Subtasks

- [ ] Task 1 — Définir la grille de critères (AC: #1)
  - [ ] 1.1 Critères fonctionnels : geo/carte, time-series, KPIs, alertes, theming dark/light
  - [ ] 1.2 Critères techniques : intégration API REST, Python-native, SSO/MSAL, Docker-compatible
  - [ ] 1.3 Critères projet : vitesse prototype, maintenabilité, licence/coût, taille communauté
  - [ ] 1.4 Pondération des critères selon priorités story 6-1

- [ ] Task 2 — Benchmark React + libs (AC: #2)
  - [ ] 2.1 Stack actuelle : React 18 + Recharts + Vite + MSAL.js — état des lieux
  - [ ] 2.2 Libs manquantes pour les nouvelles features : Leaflet/react-leaflet ou Deck.gl pour geo, D3 pour charts avancés
  - [ ] 2.3 Effort estimé pour atteindre le scope 6-1 avec React
  - [ ] 2.4 Avantage : 47 tests existants, composants déjà créés, MSAL intégré

- [ ] Task 3 — Benchmark Taipy (AC: #3, #4)
  - [ ] 3.1 Capacités geo : support carte choroplèthe natif ou via plugin ?
  - [ ] 3.2 Intégration avec l'API REST existante vs. accès direct SQLite/Polars
  - [ ] 3.3 Theming et customisation CSS — limitations connues
  - [ ] 3.4 Déploiement Azure Static Web App compatible ?
  - [ ] 3.5 Vitesse de prototype pour un dashboard de ce niveau

- [ ] Task 4 — Benchmark Streamlit (AC: #4, #5)
  - [ ] 4.1 Capacités geo : st.map, pydeck, folium integration
  - [ ] 4.2 Limitations connues : refresh, state management, SSO complexe
  - [ ] 4.3 Adéquation avec le profil jury (Data Engineering — Streamlit bien reconnu)

- [ ] Task 5 — Benchmark Plotly Dash (AC: #4)
  - [ ] 5.1 Capacités geo : Mapbox/choroplèthe natif via plotly.express
  - [ ] 5.2 Intégration REST API vs. Pandas/Polars direct
  - [ ] 5.3 Licensing : Dash Open Source vs. Dash Enterprise (coût ?)

- [ ] Task 6 — Autres candidats à évaluer rapidement (AC: #1)
  - [ ] 6.1 Panel (HoloViz) — Python-native, riche en geo
  - [ ] 6.2 Grafana (open source) — dashboarding natif, mais moins "custom"
  - [ ] 6.3 Observable Framework — JS moderne, geo excellent, mais rupture stack Python

- [ ] Task 7 — Scoring matriciel + recommandation (AC: #6)
  - [ ] 7.1 Tableau de scoring avec note /5 par critère par outil
  - [ ] 7.2 Recommandation argumentée : quel outil pour le prototype jury ?
  - [ ] 7.3 Recommandation long terme : même outil ou migration post-jury ?
  - [ ] 7.4 Si React non retenu : documenter ce qui est réutilisable (services API, auth, tests unitaires)
  - [ ] 7.5 Si React retenu : documenter les libs supplémentaires à ajouter et impact sur bundle size

## Dev Notes

### Contexte technique actuel

**Stack frontend existante (story 5-1) :**
- React 18 + Vite 6 + Recharts 2.x
- MSAL.js v2 (Azure AD SSO) — déjà intégré et testé
- 47 tests Vitest passants
- CSS custom properties (dark/light theme, glassmorphism)
- Proxy Vite → backend Python port 8765
- `frontend/.env.local` avec `VITE_SKIP_AUTH=true` pour dev local

**Backend API :**
- Azure Functions (Python) + `production_service.py`
- SQLite local (prototype) → Azure SQL (prod)
- Endpoint : `GET /api/v1/production/regional`
- Auth : Azure AD JWT Bearer token

**Données disponibles pour le benchmark :**
- 12 régions françaises (code INSEE)
- 8 sources énergétiques
- Time-series 15 min
- ~400 fact rows par jour réaliste après ingestion complète

### Critères discriminants clés

1. **Geo** : choroplèthe France par région INSEE — c'est le critère le plus différenciant entre les outils
2. **SSO MSAL** : Azure AD auth déjà en place — un outil Python-native devrait consommer l'API REST (token) ou rendre MSAL inutile (acceptable si déployé derrière Azure AD App Proxy)
3. **Déploiement Azure** : Azure Static Web App (React) vs. Azure Container Apps (Python server-side)
4. **Budget** : NFR-E1 — Consumption-based, pas de licence payante

### Note sur Taipy spécifiquement

Taipy est séduisant car Python-natif et proche du pipeline. Points à vérifier impérativement :
- Version actuelle stable (2.x vs 3.x — breaking changes ?)
- Support GeoJSON choroplèthe — pas documenté clairement dans les releases récentes
- CSS customisation : Taipy impose son design system, overrides limités
- Ne consomme pas l'API REST par défaut — accès direct DB/Polars, ce qui court-circuite la couche sécurité

### Livrable attendu

Scoring matriciel + recommandation dans la section Completion Notes de cette story, contenant :
- Grille de critères pondérés
- Note /5 par outil par critère
- Score total
- Recommandation avec justification (2-3 paragraphes)
- Migration path si React non retenu

### Project Structure Notes

- Story de **benchmark/research** — pas de code produit
- Output alimente la prochaine story d'implémentation dashboard v2 (6-5 à créer après 6-1/6-2/6-3)

### References

- Stack actuelle : `frontend/` [Source: story 5-1]
- API layer : `functions/shared/api/production_service.py`
- Budget : NFR-E1 [Source: `_bmad-output/planning-artifacts/epics.md`]
- Taipy docs : https://docs.taipy.io (à consulter — version actuelle 2026)
- Recharts actuel : `frontend/src/components/ProductionChart.jsx`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (SM story preparation)

### Debug Log References

### Completion Notes List

### File List

- `_bmad-output/implementation-artifacts/6-3-frontend-tooling-benchmark.md` (this file)

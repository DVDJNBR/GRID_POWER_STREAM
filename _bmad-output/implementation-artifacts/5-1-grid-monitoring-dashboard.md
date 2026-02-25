# Story 5.1: Grid Monitoring Dashboard (Azure Static Web App)

Status: ready-for-dev

## Story

As a Grid Manager (Marc),
I want a modern web dashboard to visualize regional production peaks and demand trends,
so that I can make informed decisions about grid balancing.

## Acceptance Criteria

1. **Given** the dashboard is deployed as an Azure Static Web App,
   **When** the page is loaded,
   **Then** it fetches real-time data from the API and displays interactive charts (Production per source, Carbon Intensity).

2. **Given** the dashboard,
   **When** the user selects a region,
   **Then** the charts update to show region-specific production breakdown by energy source.

3. **Given** the design requirements,
   **When** the dashboard is rendered,
   **Then** the interface is responsive and follows modern UX design patterns (dark mode, glassmorphism, smooth animations).

4. **Given** the API authentication,
   **When** the dashboard makes API calls,
   **Then** it uses Azure AD MSAL.js for seamless SSO authentication.

## Tasks / Subtasks

- [ ] Task 1: Frontend project setup (AC: #1, #3)
  
  - [ ] 1.1: Initialize Vite + React (or vanilla JS) project in `frontend/` directory
  - [ ] 1.2: Configure build for Azure Static Web Apps deployment (`staticwebapp.config.json`)
  - [ ] 1.3: Set up design system: dark theme, color palette, CSS variables, Google Fonts (Inter/Outfit)
  - [ ] 1.4: Install charting library: `recharts`, `chart.js`, or `d3.js`

- [ ] Task 2: Dashboard layout & components (AC: #1, #2, #3)
  
  - [ ] 2.1: Create main dashboard layout: header + sidebar (region selector) + main charts area
  - [ ] 2.2: Create production breakdown chart (stacked area: éolien, solaire, nucléaire, hydraulique, etc.)
  - [ ] 2.3: Create carbon intensity gauge/chart
  - [ ] 2.4: Create region selector dropdown with auto-refresh on selection
  - [ ] 2.5: Add real-time data refresh indicator (last updated timestamp, auto-refresh every 15 min)

- [ ] Task 3: API integration (AC: #1, #4)
  
  - [ ] 3.1: Create API client module — fetch from `/v1/production/regional` with auth headers
  - [ ] 3.2: Integrate MSAL.js for Azure AD authentication (silent token acquisition + login redirect)
  - [ ] 3.3: Handle API errors gracefully (loading states, error messages, retry)

- [ ] Task 4: Responsive design & polish (AC: #3)
  
  - [ ] 4.1: Implement responsive layout (mobile, tablet, desktop breakpoints)
  - [ ] 4.2: Add micro-animations: chart transitions, hover effects, loading skeletons
  - [ ] 4.3: Implement glassmorphism card components for KPI widgets
  - [ ] 4.4: Add dark/light theme toggle

- [ ] Task 5: Deployment configuration (AC: #1)
  
  - [ ] 5.1: Create `staticwebapp.config.json` — routing, API proxy, auth configuration
  - [ ] 5.2: Add Terraform resource for Azure Static Web App (extend `infra/`)
  - [ ] 5.3: Document deployment process in README

- [ ] Task 6: Tests (AC: #1, #2)
  
  - [ ] 6.1: Component tests for chart rendering with mock data
  - [ ] 6.2: API client tests — mock fetch responses
  - [ ] 6.3: E2E smoke test — dashboard loads and displays data

## Dev Notes

### Architecture Requirements

- **Framework:** Vite + React (lightweight, fast builds) — or vanilla JS if simplicity is preferred
- **Hosting:** Azure Static Web Apps (free tier available — budget-conscious)
- **Charting:** Prefer `recharts` (React-native) or `chart.js` (vanilla-compatible) — avoid heavy D3 unless needed
- **Auth:** MSAL.js v2 (`@azure/msal-browser`) for Azure AD SSO
- **Design:** Premium, modern UI as per PRD — "Consumer-Grade UX for Grid Monitoring"

### UX Design Principles (from PRD)

- Vibrant dark mode with harmonious color palette
- Glassmorphism card components
- Smooth micro-animations on data transitions
- Modern typography (Inter or Outfit from Google Fonts)
- Responsive: mobile-first

### API Endpoints to Consume

- `GET /v1/production/regional?region_code={code}&start_date={}&end_date={}`
- Auth: Bearer JWT token via MSAL.js

### Dependencies

- Story 4.1: API endpoints available
- Story 4.2: Azure AD auth configured
- Story 1.0: Infrastructure (extend Terraform for Static Web App)

### Project Structure (additions)

```
WATT_WATCHER/
├── frontend/                     # [NEW] Dashboard app
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── staticwebapp.config.json
│   ├── src/
│   │   ├── main.js
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ProductionChart.jsx
│   │   │   ├── CarbonGauge.jsx
│   │   │   ├── RegionSelector.jsx
│   │   │   └── KPICard.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   └── styles/
│   │       └── index.css
│   └── public/
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 5.1] — Original AC
- [Source: _bmad-output/planning-artifacts/prd.md#FR16] — Real-time dashboard
- [Source: _bmad-output/planning-artifacts/prd.md#Innovation Areas] — Consumer-Grade UX, modern UI

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log

# Story 6.1: Dashboard Data & Feature Discovery

Status: done

## Story

As a Product Manager / Solution Architect,
I want to define precisely which data, metrics, and features the GRID_POWER_STREAM dashboard should expose,
so that the UX/UI agent (6-2) and Dev benchmark agent (6-3) receive a clear, grounded brief before any design or tool choice is made.

## Acceptance Criteria

1. **Given** the current Gold layer schema and available data sources,
   **When** the discovery analysis is complete,
   **Then** a prioritized list of KPIs and visualizations is produced, with each item mapped to its source table/column in the Gold DB.

2. **Given** the two user personas (Technical Auditor, Wind Farm Manager),
   **When** the feature list is defined,
   **Then** each feature is tagged with its primary persona and a MoSCoW priority (Must/Should/Could/Won't).

3. **Given** the EU Regulation 543/2013 (ENTSO-E grid data transparency),
   **When** the feature scope is reviewed,
   **Then** a brief compliance note is added flagging any data display or retention constraint relevant to the dashboard (light pass — full veille is story 6-4).

4. **Given** the time-series nature of the data,
   **When** retention is defined,
   **Then** the recommended on-screen time range and data retention policy (e.g. 24h live, 30d history) is documented.

5. **Given** the geographic dimension (12 French regions, code INSEE),
   **When** the geo-feature scope is defined,
   **Then** the agent explicitly recommends whether a choropleth map, a list, or a region selector is sufficient for the prototype — and justifies the choice against available data granularity.

## Tasks / Subtasks

- [ ] Task 1 — Audit what data is actually available in Gold (AC: #1)
  - [ ] 1.1 List all columns in FACT_ENERGY_FLOW + DIM tables with sample values
  - [ ] 1.2 Note which sources have sparse/null data (e.g. ERA5 temperature not yet joined)
  - [ ] 1.3 Identify computed fields already available (facteur_charge, carbon intensity proxy)

- [ ] Task 2 — Define KPI & visualisation candidates (AC: #1, #2)
  - [ ] 2.1 Production par source (bar/area chart, par région, par créneau 15 min)
  - [ ] 2.2 Intensité carbone estimée (gCO₂/kWh — calcul via facteurs d'émission story 2-3)
  - [ ] 2.3 Facteur de charge par source (nécessite capacités installées story 1-2)
  - [ ] 2.4 Mix énergétique régional (% renouvelable vs. fossile vs. nucléaire)
  - [ ] 2.5 Historique de production (time-series 24h glissant minimum)
  - [ ] 2.6 Carte géographique — choroplèthe ou sélecteur de région (à trancher)
  - [ ] 2.7 Alertes surproduction / prix négatifs (story 5-2 — scope futur, noter dépendance)
  - [ ] 2.8 Fenêtres de maintenance planifiées (story 2-1 scraping — disponibilité à confirmer)

- [ ] Task 3 — MoSCoW + persona tagging (AC: #2)
  - [ ] 3.1 Tagguer chaque feature Must/Should/Could/Won't
  - [ ] 3.2 Identifier quelles features sont prioritaires pour le jury (auditeur technique) vs. l'opérationnel (gestionnaire)

- [ ] Task 4 — Rétention & time-range (AC: #4)
  - [ ] 4.1 Recommander la fenêtre temporelle de l'affichage par défaut
  - [ ] 4.2 Recommander la politique de rétention des données en Gold DB
  - [ ] 4.3 Documenter la fréquence de rafraîchissement cible (NFR-P1 = 15 min max latency)

- [ ] Task 5 — Géo-dimension (AC: #5)
  - [ ] 5.1 Évaluer la granularité disponible (12 régions, code INSEE, pas de données infra-régionales)
  - [ ] 5.2 Trancher carte choroplèthe vs. sélecteur liste/dropdown pour le prototype
  - [ ] 5.3 Documenter les données géo nécessaires (GeoJSON régions françaises, source publique)

- [ ] Task 6 — Note de conformité EU 543/2013 (AC: #3)
  - [ ] 6.1 Identifier si l'affichage de données RTE/ENTSO-E au public pose une contrainte de licence
  - [ ] 6.2 Vérifier les conditions d'usage de l'API RTE eCO2mix (open data, licence Etalab ?)
  - [ ] 6.3 Flaguer tout risque pour story 6-4 (veille réglementaire complète)

## Dev Notes

### Contexte Gold DB actuel

Le Gold DB SQLite local (prototype) contient :
- **FACT_ENERGY_FLOW** — `id_date`, `id_region`, `id_source`, `valeur_mw`, `facteur_charge`, `temperature_moyenne`
- **DIM_REGION** — 12 régions françaises, `code_insee`, `nom_region`
- **DIM_SOURCE** — 8 sources : `nucleaire`, `eolien`, `solaire`, `hydraulique`, `gaz`, `charbon`, `fioul`, `bioenergies`
- **DIM_TIME** — timestamps 15 min, `horodatage`, `jour`, `mois`, `annee`, `heure`

**Données réelles disponibles (bronze sample 2026-02-25) :**
- Seulement 2 timestamps avec valeurs non-nulles (14:45 et 15:00 UTC) — données temps réel partielles
- 3 régions avec production significative dans l'échantillon actuel
- `facteur_charge` = NULL pour tous (capacités installées non encore jointes)
- `temperature_moyenne` = NULL (ERA5 non encore jointé au FACT)

**Données potentiellement disponibles mais non encore jointes :**
- Facteurs d'émission CO₂ (story 2-3 done) → non encore intégrés au Gold
- Températures ERA5 (story 2-2 done) → non encore jointes à FACT
- Capacités installées CSV (story 1-2 done) → facteur_charge calculable mais non peuplé

### Contraintes architecturales

- API actuelle expose `/v1/production/regional` uniquement — pas d'endpoint géo, pas d'endpoint historique
- La migration SQLite → Azure SQL n'est pas encore faite (prototype local)
- NFR-P2 : réponse API < 500ms — contrainte à garder en tête pour les features time-series

### Sources de référence

- Gold schema : `functions/shared/gold/dim_loader.py`, `fact_loader.py`
- API actuelle : `functions/shared/api/production_service.py`
- PRD features FR16-FR18 : [Source: `_bmad-output/planning-artifacts/prd.md`]
- Epic 5 stories : [Source: `_bmad-output/planning-artifacts/epics.md`]
- EU Regulation 543/2013 mention : [Source: `_bmad-output/planning-artifacts/prd.md` §Grid Compliance & Transparency]
- Licence RTE open data : à vérifier sur https://data.rte-france.com/

### Note pour les stories suivantes

- **Story 6-2 (UX/UI)** consomme le livrable de cette story — attendre la liste MoSCoW finalisée
- **Story 6-3 (Dev Benchmark)** doit connaître la feature "carte géo" (Task 5) car c'est le critère discriminant entre Taipy, React+Leaflet, Streamlit, etc.
- **Story 6-4 (Veille réglementaire)** — noter ici tout risque identifié en Task 6

### Project Structure Notes

- Cette story est une story de **discovery** — le livrable est un document de brief, pas du code
- Output attendu : mise à jour de ce fichier story avec les résultats des Tasks, + éventuellement un doc séparé `6-1-dashboard-brief.md` dans `_bmad-output/implementation-artifacts/`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (Architect analysis — Winston)

### Debug Log References

Gold DB audit: 20 FACT rows, 3 regions avec données réelles, 5 sources actives, 33 timestamps (2 non-null).

### Completion Notes List

Analysis completed by Winston (Architect agent). See brief complet ci-dessous.

### File List

- `_bmad-output/implementation-artifacts/6-1-dashboard-data-feature-discovery.md` (this file)

---

# LIVRABLE — Dashboard Discovery Brief

> Produit par Winston (Architect) · 2026-02-27
> Consommé par : Story 6-2 (UX/UI) · Story 6-3 (Dev Benchmark)

---

## TASK 1 — Audit Gold DB réel

### Schéma effectif

| Table | Colonnes clés | Rows (sample) | État |
|-------|--------------|---------------|------|
| FACT_ENERGY_FLOW | id_date, id_region, id_source, **valeur_mw**, facteur_charge, temperature_moyenne | 20 | ✅ actif |
| DIM_REGION | code_insee, nom_region | 12 | ✅ complet |
| DIM_SOURCE | source_name, is_green | 8 | ✅ complet |
| DIM_TIME | horodatage, jour, mois, annee, heure | 33 | ✅ actif |

### Données réellement disponibles (sample 2026-02-25)

| Source | Rows | Total MW | Avg MW | Statut |
|--------|------|----------|--------|--------|
| nucleaire | 4 | 22 286 | 5 571 | ✅ données réelles |
| solaire | 4 | 4 367 | 1 092 | ✅ données réelles |
| hydraulique | 4 | 658 | 165 | ✅ données réelles |
| eolien | 4 | 228 | 57 | ✅ données réelles |
| bioenergies | 4 | 156 | 39 | ✅ données réelles |
| gaz, charbon, fioul | — | — | — | ⚠️ 0 dans l'échantillon* |

*Normal pour un snapshot 15h UTC en France — gaz/charbon/fioul ont une production réelle mais l'échantillon Bronze est partiel.

| Région | Rows FACT | Total MW | Note |
|--------|-----------|----------|------|
| Centre-Val de Loire (24) | 10 | 19 743 | Région nucléaire majeure |
| Nouvelle-Aquitaine (75) | 5 | 7 508 | Mix nucléaire + solaire |
| Bretagne (53) | 5 | 444 | Éolien + bioénergies |
| 9 autres régions | 0 | 0 | ⚠️ Non encore dans l'échantillon Bronze |

### Champs nuls / non encore peuplés

| Champ | État | Raison | Dépendance |
|-------|------|--------|------------|
| `facteur_charge` | NULL pour tous | Capacités installées (story 1-2) non encore jointes au FACT | Pipeline à compléter |
| `temperature_moyenne` | NULL pour tous | ERA5 (story 2-2) non encore jointé au FACT | Pipeline à compléter |
| Intensité carbone | Non calculée | Facteurs d'émission (story 2-3 done) non encore intégrés au Gold | Story 3-x manquante |

**Conclusion Task 1 :** Les données fondamentales (production par source par région) sont disponibles. Les champs enrichis (facteur_charge, température, CO₂) sont calculables mais nécessitent une jointure pipeline à planifier avant la v2.

---

## TASK 2 + 3 — Feature MoSCoW par persona

### Légende personas
- 🔬 = Auditeur Technique (jury) — veut voir la rigueur data
- ⚙️ = Marc (gestionnaire parc éolien) — veut l'opérationnel immédiat
- 🔬⚙️ = les deux

| # | Feature | Source Gold | MoSCoW | Persona | Notes |
|---|---------|------------|--------|---------|-------|
| F1 | **Production par source — time-series 24h** | FACT.valeur_mw + DIM_SOURCE + DIM_TIME | **MUST** | 🔬⚙️ | Cœur du dashboard. Area chart empilé par source sur 24h glissant |
| F2 | **KPI — Production totale MW (instant)** | SUM(valeur_mw) sur dernier slot | **MUST** | 🔬⚙️ | Carte KPI en haut de page |
| F3 | **KPI — Source dominante** | MAX(valeur_mw) sur dernier slot | **MUST** | ⚙️ | Texte + couleur codée par source |
| F4 | **Sélection de région** | DIM_REGION.code_insee | **MUST** | 🔬⚙️ | Filtre primaire — tout le dashboard en dépend |
| F5 | **Indicateur de fraîcheur / last update** | DIM_TIME.horodatage (max) | **MUST** | 🔬 | Critique pour l'auditeur : "les données sont-elles fraîches ?" |
| F6 | **Mix énergétique — répartition % (dernier slot)** | FACT.valeur_mw GROUP BY source | **MUST** | 🔬⚙️ | Donut chart. % renouvelable vs fossile vs nucléaire — lecture immédiate |
| F7 | **Intensité carbone estimée (gCO₂/kWh)** | FACT.valeur_mw × facteurs ADEME | **SHOULD** | 🔬⚙️ | Calcul côté API/Gold. Dépend story 2-3 integration. Badge coloré (vert/orange/rouge) |
| F8 | **Carte choroplèthe France — production totale par région** | SUM(valeur_mw) GROUP BY code_insee | **SHOULD** | 🔬⚙️ | Voir décision géo Task 5. Fort impact visuel pour le jury |
| F9 | **Facteur de charge par source** | FACT.facteur_charge | **SHOULD** | 🔬 | Dépend jointure capacités installées. Progress bar par source. Montre la rigueur analytique |
| F10 | **Historique 7 jours — navigation temporelle** | FACT + DIM_TIME range query | **SHOULD** | ⚙️ | Brush/zoom sur time-series. Utile Marc pour comparer J-1/J-7 |
| F11 | **Export CSV régional** | API /v1/export (story 4-1 done) | **COULD** | ⚙️ | Déjà implémenté côté API. Bouton download |
| F12 | **Overlay météo (température, vent)** | FACT.temperature_moyenne (ERA5) | **COULD** | 🔬 | Dépend jointure ERA5. Pertinent pour corréler vent ↔ éolien |
| F13 | **Comparaison inter-régions** | Multi-region query | **COULD** | 🔬 | Nice to have. Complexifie l'UI |
| F14 | **Alertes surproduction / prix négatifs** | Story 5-2 (non déployée) | **WON'T** (prototype) | ⚙️ | Nécessite déploiement Azure + logique alerting. Post-prototype |
| F15 | **Fenêtres de maintenance planifiées** | Story 2-1 scraping | **WON'T** (prototype) | ⚙️ | Données scraping intermittentes, non encore en Gold |
| F16 | **Prédiction production (AI)** | Non implémentée | **WON'T** | 🔬 | Vision long terme PRD — hors scope prototype |

### Résumé MoSCoW

| Priorité | Features | Données disponibles ? |
|----------|----------|----------------------|
| **MUST** (6) | F1-F6 | ✅ Toutes disponibles en Gold aujourd'hui |
| **SHOULD** (4) | F7-F10 | ⚠️ F7/F9/F12 nécessitent jointures pipeline |
| **COULD** (3) | F11-F13 | ✅ F11 déjà dispo · F12 dépend ERA5 |
| **WON'T** (3) | F14-F16 | ❌ Post-prototype |

---

## TASK 4 — Rétention & Time-range

### Fenêtre d'affichage par défaut

| Vue | Fenêtre recommandée | Slots (15 min) | Justification |
|-----|---------------------|----------------|---------------|
| Vue live (défaut) | **24h glissant** | 96 slots | Granularité opérationnelle pour Marc · lisible sans scroll |
| Vue historique | **7 jours** | 672 slots | Tendances hebdo · benchmark J-7 |
| Vue jury | **Jour courant depuis minuit** | 0–96 slots | Démo propre avec données du jour |

### Politique de rétention Gold DB

| Horizon | Recommandation | Justification |
|---------|---------------|---------------|
| Prototype jury | **90 jours minimum** | Plusieurs semaines de données pour montrer les tendances |
| Production v1 | **1 an glissant** | Comparaison N-1 utile pour Marc |
| Archive | Azure Blob Cold Tier | Post-1 an → stockage froid, non queryable live |

### Rafraîchissement

- **NFR-P1 = 15 min max latency** → refresh UI toutes les **15 min** (déjà implémenté en App.jsx)
- Indicateur de fraîcheur obligatoire (F5) — afficher l'horodatage du dernier slot en Gold

---

## TASK 5 — Décision géo

### Recommandation : **Choroplèthe France — SHOULD, pas MUST**

**Justification :**

| Critère | Choroplèthe | Sélecteur dropdown |
|---------|-------------|-------------------|
| Impact visuel jury | ⭐⭐⭐⭐⭐ Fort | ⭐⭐ Neutre |
| Lisibilité opérationnelle | ⭐⭐⭐⭐ Marc voit immédiatement les régions en surproduction | ⭐⭐⭐ Correct |
| Adéquation données | ✅ 12 régions = granularité parfaite pour choroplèthe | ✅ Fonctionne aussi |
| Complexité implémentation | ⚠️ GeoJSON requis + lib cartographique | ✅ Déjà implémenté (RegionSelector.jsx) |
| Impact benchmark outils (6-3) | 🔴 Critère discriminant majeur | ⚫ Neutre |

**Décision architecturale :** La carte choroplèthe est recommandée pour le prototype **si** l'outil frontend le supporte nativement ou avec une lib légère. C'est le critère discriminant #1 pour story 6-3.

**Si l'outil ne supporte pas la carte** → fallback acceptable : sélecteur amélioré (autocomplete + flag couleur par production).

### Données GeoJSON requises

- Source : `https://geo.data.gouv.fr/fr/datasets/` — GeoJSON régions françaises (Licence Ouverte)
- Fichier : contours des 13 régions métropolitaines (code INSEE 11, 24, 27, 28, 32, 44, 52, 53, 75, 76, 84, 93, 94)
- Taille estimée : ~500 Ko — acceptable pour le bundle frontend
- Jointure : `DIM_REGION.code_insee` ↔ propriété `code` du GeoJSON

---

## TASK 6 — Note de conformité EU 543/2013 (light pass)

### Résultat de l'analyse

| Point | Statut | Note |
|-------|--------|------|
| **Licence RTE eCO2mix** | ✅ Sûr | API publique RTE → **Licence Ouverte v2 (Etalab)** — réutilisation libre, commerciale et non commerciale, avec attribution |
| **EU Reg. 543/2013** | ✅ Sûr (en tant que consommateur) | Cette réglementation impose des **obligations aux TSOs (RTE, ENTSO-E)** pour publier leurs données. En tant que consommateur de ces données, GRID_POWER_STREAM n'est pas soumis à ces obligations directes |
| **GDPR / NFR-S2** | ✅ Couvert | Le dashboard affiche uniquement des agrégats régionaux — aucune donnée personnelle ou de comptage individuel |
| **Attribution requise** | ⚠️ À implémenter | La Licence Ouverte impose une mention de source. Ajouter un footer "Source : RTE Open Data / eCO2mix" sur le dashboard |
| **Données ENTSO-E (story 2-1)** | ⚠️ À vérifier en 6-4 | Les données scrappées sur transparency.entsoe.eu peuvent avoir des CGU spécifiques — à auditer dans la veille réglementaire complète |

### Actions immédiates (avant déploiement public)

1. Ajouter footer **"Données : RTE Open Data (Licence Ouverte v2 / Etalab)"** sur le dashboard
2. Story 6-4 : vérifier CGU ENTSO-E transparency portal et Règlement 543/2013 Art. 4 (obligations de publication)

---

## SYNTHÈSE POUR STORIES 6-2 ET 6-3

### Brief pour Story 6-2 (UX/UI)

> **Périmètre MUST à designer en priorité :**
> F1 (time-series 24h), F2-F3 (KPIs MW + source), F4 (région), F5 (fraîcheur), F6 (mix donut)
>
> **Périmètre SHOULD à prévoir dans les maquettes :**
> F7 (intensité carbone), F8 (carte choroplèthe — voir décision géo ci-dessus), F9 (facteur charge)
>
> **Contrainte clé :** Le dashboard doit être lisible en 5 secondes par Marc (opérationnel) ET montrer la rigueur technique au jury. Ces deux lectures doivent coexister dans le même layout.

### Brief pour Story 6-3 (Dev Benchmark)

> **Critère discriminant #1 — Géo :** L'outil doit supporter un choroplèthe France avec GeoJSON (12 régions INSEE). C'est le point de différenciation le plus fort visuellement.
>
> **Critère #2 — Time-series :** Area chart empilé multi-source sur 96 points (24h × 15 min), interactif (hover, zoom).
>
> **Critère #3 — Stack Python :** L'outil doit consommer l'API REST existante (`/api/v1/production/regional`) — pas d'accès direct DB pour ne pas court-circuiter la sécurité Azure AD.
>
> **Critère #4 — Déploiement :** Compatible Azure Static Web App (React/JS) ou Azure Container Apps (Python server-side). Budget NFR-E1 : Consumption-based uniquement.
>
> **Stack existante à ne pas jeter :** Services API (`api.js`, `auth.js`), 47 tests Vitest, MSAL.js intégré.

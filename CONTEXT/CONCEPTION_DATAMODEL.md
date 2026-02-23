# Document de Conception de Données (MERISE) - GRID_POWER_STREAM

Ce document détaille la modélisation des données pour la plateforme, de la vision conceptuelle à l'implémentation physique (Star Schema), pour répondre aux exigences de la compétence **C11**.

## I. Modèle Conceptuel des Données (MCD)

Le MCD représente les entités métier et leurs relations, indépendamment de toute contrainte technique.

### 1. Entités et Propriétés

- **REGION :** Identification géographique administrative.
    - `code_insee` (PK)
    - `nom_region`
- **SITE_PRODUCTION :** Unité de production (ex: un parc éolien spécifique).
    - `id_site` (PK)
    - `nom_site`
    - `type_energie` (Éolien, Solaire, Nucléaire, Gaz)
    - `puissance_installee_mw` (Source 2 : Flat File/CSV)
- **MESURE_ENERGIE :** Flux réel de production ou consommation.
    - `id_mesure` (PK)
    - `horodatage`
    - `valeur_mw`
    - `type_mesure` (Production, Consommation)
- **METEO_HISTO :** Données climatiques de benchmarking.
    - `id_meteo` (PK)
    - `horodatage`
    - `vitesse_vent_100m`
    - `rayonnement_solaire` (Source 5 : Parquet/Big Data)
- **MAINTENANCE :** Alertes de disponibilité du réseau.
    - `id_alerte` (PK)
    - `date_debut`
    - `date_fin`
    - `description` (Source 3 : Web Scraping)
- **PRIX_MARCHE :** Tarification historique et spot.
    - `id_prix` (PK)
    - `horodatage`
    - `prix_mwh_euro` (Source 4 : External SQL DB)

### 2. Relations et Cardinalités

- **REGION --(1,n)-- Localiser --(1,1)-- SITE_PRODUCTION**
- **SITE_PRODUCTION --(0,n)-- Générer --(1,1)-- MESURE_ENERGIE**
- **REGION --(0,n)-- Enregistrer --(1,1)-- MESURE_ENERGIE**
- **REGION --(0,n)-- Subir --(1,1)-- METEO_HISTO**
- **REGION --(0,n)-- Concerner --(1,n)-- MAINTENANCE**
- **REGION --(0,n)-- Appliquer --(1,1)-- PRIX_MARCHE**

---

## II. Modèle Logique des Données (MLD)

Le MLD traduit le MCD en structures relationnelles (tables, clés primaires et étrangères).

- **T_REGION** (`code_insee` [PK], `nom_region`)
- **T_SITE_PRODUCTION** (`id_site` [PK], `nom_site`, `type_energie`, `puissance_installee_mw`, `#code_insee` [FK])
- **T_MESURE** (`id_mesure` [PK], `horodatage`, `valeur_mw`, `type_mesure`, `#id_site` [FK], `#code_insee` [FK])
- **T_METEO** (`id_meteo` [PK], `horodatage`, `vitesse_vent_100m`, `rayonnement_solaire`, `#code_insee` [FK])
- **T_MAINTENANCE** (`id_alerte` [PK], `date_debut`, `date_fin`, `description`)
- **TJ_REGION_MAINTENANCE** (`#code_insee` [PK, FK], `#id_alerte` [PK, FK])
- **T_PRIX** (`id_prix` [PK], `horodatage`, `prix_mwh_euro`, `#code_insee` [FK])

---

## III. Modèle Physique (Data Warehouse - Star Schema)

Optimisation pour la **Zone Gold** (C13/C14).

### 1. Table de Faits : `FACT_ENERGY_FLOW`
- `id_fact` [PK]
- `id_date` [FK]
- `id_region` [FK]
- `id_site` [FK]
- `valeur_mw` (Mesure réelle)
- `facteur_charge` (Calculé : valeur_mw / puissance_installee)
- `temperature_moyenne`
- `prix_mwh`

### 2. Tables de Dimensions
- **DIM_REGION :** `id_region`, `code_insee`, `nom_region`.
- **DIM_TIME :** `id_date`, `horodatage`, `jour`, `mois`, `annee`, `heure`.
- **DIM_SITE :** `id_site`, `nom_site`, `type_source`.

---

## IV. Conformité Compétences
- **C11 :** Formalisme MERISE respecté (MCD/MLD).
- **C13 :** Modélisation multidimensionnelle (Faits/Dimensions).
- **C14 :** Optimisation pour l'aide à la décision métier.

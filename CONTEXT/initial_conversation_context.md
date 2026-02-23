# Contexte Initial de Discussion (Gemini Context)

Ce document contient les échanges initiaux ayant conduit à la définition du projet **GRID_POWER_STREAM**. Il retrace la transition d'un projet interne vers une solution **Open Data** suite à des enjeux de sécurité (leak GitHub).

## Points Clés de la Discussion :
- **Problématique :** Nécessité d'un projet 100% public pour le jury suite à un audit de sécurité en entreprise.
- **Thématique :** Énergie et Mobilité Durable (Open Data).
- **Architecture Proposée :** Medallion (Bronze/Silver/Gold) sur Azure.
- **Sources de données :** API RTE, Fichiers Open Data Gouv, Scraping EcoWatt.
- **Justification Big Data :** Utilisation de Spark et partitionnement Parquet pour gérer la vitesse et la volumétrie.
- **Gouvernance :** Privacy by design et anonymisation pour la conformité RGPD.

---

## Extrait de la proposition initiale (Gemini) :

L'objectif est de croiser la production d'énergie en temps réel avec la météo et les tarifs pour conseiller des moments de consommation optimaux.

1. **Stratégie Multi-Sources (E4 - C8, C9)**
API REST (RTE), Fichiers (Tarifs), Scraping (EcoWatt), BDD (Référentiels), Big Data (Logs via Spark).

2. **Architecture Data Lake (E7 - C18, C19, C20)**
Architecture Medallion (Bronze / Silver / Gold) sur Azure (ADLS Gen2).

3. **Data Warehouse & ETL (E5 - C13, C14, C15)**
Modélisation en Étoile : FACT_PRODUCTION_ENERGY, DIM_TIME, DIM_SOURCE, DIM_GEOGRAPHY.

4. **Partage via API (E4 - C12)**
API FastAPI sécurisée via OAuth2/API Key avec documentation Swagger.

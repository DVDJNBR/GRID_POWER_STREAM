# GRID_POWER_STREAM : Plateforme d'Analyse de Tension Électrique Régionale

## 📌 Présentation du Projet
**GRID_POWER_STREAM** est une solution d'ingénierie de données permettant de surveiller en temps réel l'équilibre entre la production et la consommation d'électricité à l'échelle des régions françaises. Le projet croise des données de flux (temps réel) et des données de stock (démographie, météo) pour offrir une vision prédictive de la tension sur le réseau.

### Objectifs techniques (Référentiel E4, E5, E7) :
* **Ingestion multi-sources :** API REST, Scraping, Fichiers plats.
* **Architecture Data Lake :** Stockage objet partitionné (Parquet).
* **Transformation Big Data :** Traitement via Spark (PySpark).
* **Data Warehousing :** Modélisation dimensionnelle en étoile.
* **Exposition :** API REST sécurisée sous Docker.

---

## 🏗️ Architecture Technique (Azure)

L'architecture est conçue pour être "Serverless", limitant les coûts et maximisant la sécurité.

* **Extraction (C8) :** Azure Functions (Python) déclenchées par Timer.
* **Stockage Brut (C18) :** Azure Data Lake Storage (ADLS) Gen2 - Zone Bronze (JSON/CSV).
* **Traitement & Nettoyage (C10, C15) :** Azure Databricks (Spark) - Zone Silver (Parquet).
* **Entrepôt de Données (C13, C14) :** Azure SQL Database - Zone Gold (Schéma en étoile).
* **Distribution (C12) :** FastAPI déployée via Azure App Service (Docker).

---

## 📊 Modélisation des Données (C11)

### Modèle Conceptuel des Données (MCD - Méthode MERISE)
Le projet repose sur les entités suivantes :
1.  **REGION :** Code INSEE, Nom, Population, Superficie.
2.  **MESURE :** Consommation (MW), Production (MW), Horodatage.
3.  **METEO :** Température, Ensoleillement, Vitesse du vent.
4.  **SOURCE_ENERGIE :** Type (Éolien, Nucléaire, Solaire, Gaz).

### Modèle Physique (Data Warehouse)
Modélisation en **étoile** pour optimiser les requêtes analytiques :
* **Table de Faits :** `FACT_ENERGY_FLOW` (IDs Dimensions, Consommation, Production, Température).
* **Dimensions :** `DIM_REGION`, `DIM_TIME`, `DIM_ENERGY_TYPE`.

---

## 🛡️ Gouvernance & RGPD (C20, C21)

Suite à une analyse de conformité, le projet applique les principes de **Privacy by Design** :
* **Données Personnelles :** Le projet traite uniquement des données agrégées par région. Aucune donnée à l'échelle du foyer (type Linky brut) n'est ingérée, éliminant tout risque de fuite de données à caractère personnel (DCP).
* **Sécurité des accès :** Utilisation des **Managed Identities** d'Azure. Aucune clé d'accès (API Key, Database Password) n'est stockée dans le code source ou sur GitHub.
* **Gestion des logs :** Monitorage des erreurs d'ingestion via Azure Monitor avec alertes automatiques en cas de rupture de flux API (C20).

---

## 🛠️ Stack Technique
| Composant | Technologie |
| :--- | :--- |
| **Langage** | Python 3.10+ |
| **Big Data** | PySpark (Apache Spark) |
| **API** | FastAPI + Swagger (OpenAPI) |
| **Conteneur** | Docker |
| **CI/CD** | GitHub Actions |
| **Cloud** | Microsoft Azure |

---

## 🚀 Installation & Exécution (Local)

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/ton-profil/grid-power-stream.git
   ```
2. **Configuration :** Renommer `.env.example` en `.env` et remplir les variables (Secrets Azure).
3. **Lancement via Docker :**
   ```bash
   docker-compose up --build
   ```

# Conception Technique : GRID_POWER_STREAM

Ce document détaille la modélisation des données, les flux d'échanges et les spécifications techniques du projet conformément aux exigences du jury.

---

## 📊 Modélisation des Données (C11)

### 1. Modèle Conceptuel des Données (MCD - MERISE)

Le MCD permet de définir les entités et leurs relations avant l'implémentation physique.

**Entités et Attributs :**
*   **REGION** (<u>ID_Region</u>, Code_INSEE, Nom_Region, Population, Superficie)
*   **DATE** (<u>ID_Date</u>, Date_Complete, Jour, Mois, Annee, Est_Ferie, Saison)
*   **SOURCE_ENERGIE** (<u>ID_Source</u>, Nom_Source, Categorie_Renouvelable)
*   **METEO** (<u>ID_Meteo</u>, Temperature, Vents, Ensoleillement)

**Associations :**
*   **MESURER** : Relie **REGION**, **DATE** et **SOURCE_ENERGIE**.
    *   Attributs : Valeur_MW (Quantité produite ou consommée).
    *   Cardinalités : Une région peut avoir plusieurs mesures (1,n), une date peut avoir plusieurs mesures (1,n).
*   **RELEVER** : Relie **REGION** et **METEO** à une **DATE**.

### 2. Modèle Logique de Données (MLD - Schéma Relationnel)

*   **DIM_REGION** (<u>ID_Region</u>, Code_INSEE, Nom, Population, Superficie)
*   **DIM_TIME** (<u>ID_Time</u>, Full_Date, Year, Month, Day, Is_Holiday)
*   **DIM_SOURCE** (<u>ID_Source</u>, Source_Name, Is_Green)
*   **FACT_ENERGY_FLOW** (<u>#ID_Region, #ID_Time, #ID_Source</u>, Power_MW, Temperature_Celsius)

---

## 📡 Spécifications de l'API Source (RTE Eco2mix)

L'extraction automatisée (C8) s'appuie sur l'API publique de RTE.

*   **Endpoint Principal** : `https://opendata.rte-france.com/api/v1/eco2mix_regional_real_time`
*   **Méthode** : `GET`
*   **Format** : JSON
*   **Fréquence de collecte** : Toutes les 15 minutes.
*   **Données récupérées** :
    *   `code_insee_region`
    *   `date_heure`
    *   `consommation`
    *   `nucleaire`, `eolien`, `solaire`, `hydraulique`, `pompage`, `bioenergies`.

---

## 🛡️ Architecture de Sécurité & Flux Azure (C21)

Pour répondre aux exigences de gouvernance et éviter les fuites de secrets (Identity-based security) :

1.  **Azure Functions (Ingestor)** : Utilisée avec une **System-Assigned Managed Identity**.
2.  **ADLS Gen2 (Data Lake)** : Les droits d'accès sont gérés via **RBAC (Role-Based Access Control)**. La fonction a le rôle "Storage Blob Data Contributor".
3.  **Key Vault (Optionnel)** : Utilisé uniquement pour les clés API externes (RTE) avec accès restreint via Managed Identity. Aucun secret n'est présent dans le code source ou les variables d'environnement exposées.

---

## ⚙️ Pipeline ETL (C15 - Spark)

Le traitement Big Data (C10) suit la logique suivante dans Azure Databricks :

1.  **Bronze to Silver** :
    *   Lecture des JSON bruts.
    *   Déduplication basée sur le couple `(Code_INSEE, Horodatage)`.
    *   Normalisation des noms de colonnes.
    *   Écriture en format **Parquet** partitionné par `Year/Month/Day`.
2.  **Silver to Gold** :
    *   Agrégation des données par région et par heure.
    *   Jointure avec le référentiel population (INSEE).
    *   Calcul de l'indicateur d'intensité énergétique.

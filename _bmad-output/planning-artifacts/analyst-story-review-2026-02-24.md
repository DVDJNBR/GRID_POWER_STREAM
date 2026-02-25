# Analyst Story Review Report 📊

**Date:** 2026-02-24
**Reviewer:** Mary (Business Analyst)
**Scope:** 16 stories — Business value, domain accuracy, data flow coherence, référentiel alignment

---

## Executive Summary

Le backlog est **bien construit** du point de vue business. Les stories suivent un flux logique de la donnée brute à la valeur métier (dashboard + alertes). Cependant, j'ai identifié **7 observations** qui méritent attention avant le dev — principalement autour de la cohérence métier et de la complétude de la chaîne de valeur.

---

## 🔍 Analyse du Flux de Valeur Métier

### Chaîne de valeur : Source → Donnée brute → Connaissance → Décision

```
[Sources externes]      →  [Bronze]  →  [Silver]  →  [Gold/DW]  →  [API]  →  [Insight]
RTE API (production)       Raw JSON     Clean Parquet  Star Schema  REST     Dashboard
CSV (capacité installée)   Raw CSV      Normalized     DIM/FACT    Swagger   Alertes
Scraping (maintenance)     Raw HTML     Partitioned    SQL Views
ERA5 (climat)              Raw Parquet  Standardized
ADEME (émissions)          Raw CSV
```

**Verdict flux :** ✅ La chaîne est complète — chaque source a un chemin vers la valeur.

---

## 📋 Observations Business

### O1. 🟡 Persona "Marc" sous-exploitée — pas de user journey complet

**Constat :** Le PRD définit Marc (Grid Manager) comme persona principal. Les stories 5.1 et 5.2 le mentionnent, mais les stories d'ingestion/pipeline ne font aucun lien avec les questions business de Marc.

**Risque :** Le dev agent pourrait implémenter un pipeline techniquement correct mais qui ne répond pas aux vraies questions de Marc :

- "Quelle région a le plus de surproduction éolienne cette semaine ?"
- "Est-ce que la maintenance prévue à Gravelines va impacter l'approvisionnement ?"

**Recommandation :** Ajouter dans les dev notes de Story 3.2 (Gold) les **questions métier** que le modèle Star Schema doit pouvoir répondre. Cela guidera le choix des agrégations.

---

### O2. 🟡 Données ERA5 (climat) : valeur métier floue

**Constat :** Story 2.2 ingère les données ERA5 (température, vent, ensoleillement). Mais aucune story ne précise **comment** ces données climatiques enrichissent l'analyse.

**Questions non résolues :**

- Corrélation vent ↔ production éolienne ?
- Corrélation température ↔ consommation ?
- Ces données alimentent quel DIM ou FACT dans le Gold ?

**Recommandation :** Clarifier dans Story 3.1 comment les données ERA5 rejoignent le Silver, et dans Story 3.2 comment `temperature_moyenne` est alimentée dans `FACT_ENERGY_FLOW`.

---

### O3. 🟡 Facteur de charge — calcul non spécifié

**Constat :** Le champ `facteur_charge` dans `FACT_ENERGY_FLOW` est mentionné dans le schéma (CONCEPTION_DATAMODEL), mais aucune story ne spécifie la formule de calcul.

**Formule attendue :** `facteur_charge = production_reelle_mw / capacite_installee_mw`

**Dépendance :** Nécessite de croiser Story 1.1 (production réelle via API) avec Story 1.2 (capacité installée via CSV).

**Recommandation :** Ajouter la formule explicitement dans Story 3.2 (Gold), tâche de chargement des FACT.

---

### O4. 🟢 Données prix (`prix_mwh`) — source non identifiée

**Constat :** Le champ `prix_mwh` est dans `FACT_ENERGY_FLOW` mais aucune story ne le sourcing. L'API RTE eCO2mix ne fournit **pas** les prix spot.

**Source probable :** EPEX SPOT (marché européen de l'électricité) — nécessite un accès API séparé ou des données Open Data.

**Recommandation :** Soit :

- Ajouter une Story d'ingestion pour les prix EPEX SPOT
- Soit déclarer `prix_mwh` comme nullable/futur dans le schéma initial (Story 0.1)
- Le 2ème est plus réaliste pour un MVP

---

### O5. 🟢 Orchestration des pipelines — qui déclenche quoi ?

**Constat :** Chaque story définit sa propre Azure Function, mais **aucune story ne définit l'orchestration globale** :

- À quelle heure tourne l'ingestion RTE ? (toutes les 15 min)
- Quand se déclenche Bronze → Silver ? (après ingestion ?)
- Quand se déclenche Silver → Gold ? (après Silver ?)
- Quand tournent les quality gates ? (entre chaque couche ?)

**Recommandation :** Ce n'est pas une story manquante — c'est un sujet de **Sprint Planning**. L'orchestration (Timer triggers, Event triggers, séquençage) sera résolue naturellement lors de l'implémentation. Mais le documenter dans les dev notes de Story 3.1 aiderait.

---

### O6. 🟢 Absence de Story de "démo/validation" métier

**Constat :** Le référentiel (C7) exige des "démonstrations à chaque jalon" et des "temps d'accompagnement utilisateurs finaux". Aucune story ne prévoit explicitement un livrable de démo.

**Recommandation :** Ce n'est pas une story technique — c'est un livrable de **Sprint Review**. Mais prévoir dans Story 5.1 (Dashboard) un mode "démo" avec des données de test serait utile pour les soutenances.

---

### O7. 🟢 Documentation technique exigée par le référentiel

**Constat :** Les compétences C8, C10, C11, C12, C14, C15, C19 exigent toutes une **documentation technique** des scripts. Aucune story ne liste explicitement "produire la doc technique" comme tâche.

**Recommandation :** Ajouter une sous-tâche systématique dans chaque story : "Documenter les dépendances, commandes, et enchaînements logiques dans un README ou docstring". Le dev agent le fera peut-être naturellement, mais mieux vaut le spécifier.

---

## Matrice Référentiel × Valeur Métier

| Épreuve | Compétence                 | Valeur Métier Produite                       | Story                        |
| ------- | -------------------------- | -------------------------------------------- | ---------------------------- |
| E4      | C8 (Extraction)            | Acquisition données multi-source → diversité | 0.1, 1.1, 1.2, 2.1, 2.2, 2.3 |
| E4      | C9 (SQL)                   | Requêtes analytiques → insights              | 3.2                          |
| E4      | C10 (Agrégation)           | Données propres → fiabilité                  | 3.1                          |
| E4      | C11 (BDD/MERISE)           | Modèle validé → traçabilité                  | 0.1                          |
| E4      | C12 (API REST)             | Données accessibles → réutilisabilité        | 4.1, 4.2, 4.3                |
| E5      | C13 (Modélisation DW)      | Star Schema → analyse rapide                 | 0.1, 3.2                     |
| E5      | C14 (Création DW)          | Entrepôt fonctionnel → aide à la décision    | 1.0, 3.2                     |
| E5      | C15 (ETL)                  | Qualité données → confiance                  | 3.1, 3.2, 3.3                |
| E7      | C18 (Architecture DL)      | Infra scalable → pérennité                   | 1.0                          |
| E7      | C19 (Intégration DL)       | Pipeline automatisé → productivité           | 1.1, 1.2, 2.1, 2.2           |
| E7      | C20 (Catalogue/monitoring) | Visibilité ops → réactivité                  | 1.3, 3.3, 5.2                |
| E7      | C21 (Gouvernance)          | Sécurité/RGPD → conformité                   | 1.0, 4.2                     |

---

## Verdict Final : 🟢 PRÊT avec 3 ajustements recommandés

Le backlog est **solide et complet** du point de vue business. Les 3 ajustements prioritaires :

1. **O1** : Ajouter les questions métier de Marc dans Story 3.2 (Gold)
2. **O3** : Spécifier la formule du facteur de charge dans Story 3.2
3. **O4** : Déclarer `prix_mwh` comme nullable dans Story 0.1 (source inexistante pour le MVP)

Les observations O2, O5, O6, O7 sont des "nice to have" qui se résoudront naturellement pendant l'implémentation.

---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', 'CONTEXT/CONCEPTION_TECHNIQUE.md']
---

# GRID_POWER_STREAM - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for GRID_POWER_STREAM, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: The system can automatically poll the RTE Open Data API (eCO2mix) on a configurable hourly schedule.
FR2: The system can extract data from Flat Files (CSV) containing regional installed power capacity targets and site inventories.
FR3: The system can programmatically scrape grid maintenance status pages to identify scheduled downtime.
FR4: The system can query a Reference SQL Database to map production sites to their respective grid nodes and regional territories.
FR5: The system can extract massive historical weather context (ERA5 Reanalysis) in Parquet format from a Big Data system.
FR6: The system can securely store all raw multi-source extracts in Azure Data Lake Storage Gen2 (Bronze layer).
FR7: The system can handle API/Connection retries and log ingestion heartbeats for observability.
FR8: The system can clean (handle NaNs, corrupted entries) and partition data into optimized Parquet files (Silver layer).
FR9: The system can model energy flow data into a relational Star Schema (Gold layer) for efficient querying.
FR10: The system can aggregate production metrics at the regional level, crossing API data with Flat-file demographic data.
FR11: The system can validate data integrity between layers using automated quality gates.
FR12: Users can query regional production and carbon intensity data via a RESTful API.
FR13: Users can authenticate using Azure AD / JWT Bearer tokens to access protected endpoints.
FR14: Developers can access automated API documentation via a Swagger/OpenAPI UI.
FR15: Wind farm managers can export aggregated production reports in CSV format for Excel analysis.
FR16: Users can visualize real-time grid metrics through a modern web dashboard.
FR17: The system can trigger automated alerts when regional over-production exceeds local demand.
FR18: The system can detect and notify users of potential negative price scenarios based on production peaks.
FR19: The platform generates audit logs for every successful and failed data ingestion job (C20).
FR20: Administrators can restrict write access to the Gold layer using RBAC/ACLs (C21).
FR21: The entire application stack can be deployed in a containerized environment (Docker) for VPS portability.

### NonFunctional Requirements

NFR-P1 (Freshness): The end-to-end data pipeline must ensure a maximum data latency of 15 minutes.
NFR-P2 (Response Time): The API must respond to /production/regional queries in less than 500ms.
NFR-S1 (Authentication): 100% of non-public API endpoints must require a valid Azure AD JWT token.
NFR-S2 (Privacy by Design): No Individual Metering Data (DCP) shall be ingested.
NFR-S3 (Integrity): Gold layer tables must be read-only for the API service principal.
NFR-R1 (Resilience): Ingestion jobs must implement exponential backoff and retry logic.
NFR-R2 (Monitoring): Historical logs of ingestion heartbeats must be available for audit (C20).
NFR-E1 (Cost Optimization): The architecture must prioritize Consumption-based services to stay within the $84 budget.
NFR-E2 (Compute Efficiency): Data transformations using Polars/Pandas must be optimized for memory efficiency.

### Additional Requirements

- **Compute Strategy Update:** Replace Databricks/Spark with **Azure Functions + Polars** (per PRD update).
- **Medallion Architecture:** Bronze (JSON/Raw) -> Silver (Parquet/Clean) -> Gold (Azure SQL/Relational Fact & Dim).
- **Security:** Managed Identity for Azure Functions to query/write SQL, RBAC for ADLS Gen2, Key Vault for RTE Secrets.
- **Portability:** Docker/Containerization for potential migration to VPS.
- **Data Model:** Star Schema in Azure SQL (FACT_ENERGY_FLOW connected to dimensions REGION, TIME, DATE).

### FR Coverage Map

FR1: Epic 1 - RTE API Ingestion
FR2: Epic 1 - CSV Capacity Ingestion
FR3: Epic 2 - Maintenance Scraping
FR4: Epic 1 - SQL Reference Ingestion
FR5: Epic 2 - ERA5 Parquet Ingestion
FR6: Epic 1/2 - Storage in Bronze
FR7: Epic 1/2 - Ingestion Resilience
FR8: Epic 3 - Cleaning & Silver layer
FR9: Epic 3 - Star Schema & Gold layer
FR10: Epic 3 - Regional Aggregation
FR11: Epic 3 - Quality Gates
FR12: Epic 4 - Production API
FR13: Epic 4 - Secure JWT Auth
FR14: Epic 4 - Swagger Docs
FR15: Epic 4 - CSV Export for Managers
FR16: Epic 5 - Monitoring Dashboard
FR17: Epic 5 - Over-production Alerts
FR18: Epic 5 - Negative Price Detection
FR19: Epic 1-5 - Audit Logs
FR20: Epic 3 - RBAC/ACLs
FR21: Epic 1-5 - Docker Portability

## Epic List

### Epic 1: Multi-Source Production Ingestion
Establish the foundational data stream by ingesting core production data and reference capacity.
**FRs covered:** FR1, FR2, FR4, FR6, FR7, FR19, FR21.

## Epic 1: Multi-Source Production Ingestion

**Goal:** Ingest the primary production and reference data streams into the Bronze layer to enable the first level of grid visibility.

### Story 1.0: Infrastructure as Code with Terraform (C18)
**As a** DevOps Engineer,
**I want** to use Terraform to provision the Azure Resource Group, ADLS Gen2, and Azure SQL Serverless instance,
**So that** my entire infrastructure is versioned, reproducible, and documented.

**Acceptance Criteria:**
- **Given** a set of Terraform configuration files (`main.tf`, `variables.tf`).
- **When** executing `terraform apply`.
- **Then** the Azure resources are created correctly according to the plan.
- **And** the state is managed securely (local or remote).
- **And** (Architect Note): Use `null_resource` or specific providers to handle the initial SQL schema setup if possible.

### Story 1.1: Automated RTE eCO2mix API Ingestion
**As a** Platform Builder,
**I want** to configure an Azure Function to extract real-time energy production data from the RTE API,
**So that** the raw JSON payloads are securely stored in the Bronze layer for further processing.

**Acceptance Criteria:**
- **Given** the RTE API credentials are securely stored in Azure Key Vault.
- **When** the ingestion Azure Function is triggered by the 15-minute timer.
- **Then** the raw JSON response is saved as a timestamped file in `bronze/rte/production/`.
- **And** a heartbeat entry is created in the ingestion audit logs.

### Story 1.2: Regional Installed Capacity (CSV) Ingestion
**As a** Platform Builder,
**I want** to automate the collection of regional installed capacity CSV files,
**So that** we have the reference points needed to calculate performance metrics (load factors).

**Acceptance Criteria:**
- **Given** the capacity CSV files are uploaded to the source landing zone.
- **When** the ingestion process runs.
- **Then** the files are moved to `bronze/reference/capacity/` without schema alteration.
- **And** the data is logged as successfully received.

### Story 1.3: Dynamic Asset Discovery & Lifecycle Management (C11, C14)
**As a** Data Architect,
**I want** the system to manage the full lifecycle of grid assets by discovering new entities and marking stale ones as inactive in the SQL database,
**So that** we maintain a high-quality, up-to-date registry without losing historical referential integrity.

**Acceptance Criteria:**
- **Given** the extraction of current RTE data (Bronze).
- **When** a region or node is found in the flux that doesn't exist in SQL, it is inserted with `status='active'` and `first_seen_at`.
- **When** an existing SQL node is NOT found in the RTE flux for a configurable period (e.g., 24h), its status is updated to `status='stale'` or `inactive` (Soft Delete).
- **Then** the system avoids hard-deleting records to preserve historical production links in the Gold layer.
- **And** the discovery/decommissioning events are logged for operational review.

### Epic 2: Advanced Grid Context Enrichment
Augment the core production data with external maintenance alerts and large-scale weather benchmarks.
**FRs covered:** FR3, FR5, FR6, FR7, FR19, FR21.

## Epic 2: Advanced Grid Context Enrichment

**Goal:** Enrich the production data with external context (Maintenance & Climate) to enable advanced reasoning and benchmarking.

### Story 2.1: Web Scraping of Grid Maintenance Portals
**As a** Platform Builder,
**I want** to programmatically scrape the ENTSO-E or RTE transparency status pages,
**So that** we can capture scheduled downtime and maintenance events in the Bronze layer.

**Acceptance Criteria:**
- **Given** the URL of the maintenance transparency portal.
- **When** the scraping Azure Function is triggered.
- **Then** the extracted HTML/JSON data (Event ID, Dates, Description) is saved in `bronze/maintenance/`.
- **And** the scraper handles common HTTP errors (404, 429) gracefully.

### Story 2.2: Historical Climate Reanalysis (ERA5) Parquet Ingestion
**As a** Platform Builder,
**I want** to extract weather datasets (wind speed, solar radiation) in Parquet format from a public Big Data storage (Azure Open Datasets/S3),
**So that** we can perform large-scale theoretical yield calculations.

**Acceptance Criteria:**
- **Given** access to the public ERA5 object storage.
- **When** the ingestion job (using Polars) pulls the hourly deltas.
- **Then** the Parquet files are partitioned and saved in `bronze/climate/era5/`.
- **And** the ingestion process utilizes **Polars "streaming" mode** to minimize memory footprint.
- **And** (Architect Note): The implementation must handle Azure Function execution limits (max 10min) by processing in chunks if necessary and ensuring high I/O throughput to avoid timeouts during mass historical imports.

### Epic 3: Automated Medallion Pipeline & Warehouse
Implement the transformation logic to clean raw data and model it into a high-performance Star Schema (Gold zone).
**FRs covered:** FR8, FR9, FR10, FR11, FR20, FR21.

## Epic 3: Automated Medallion Pipeline & Warehouse

**Goal:** Transform multi-source raw data into a curated, relational Data Warehouse (Star Schema) using Polars for high-performance processing.

### Story 3.1: Bronze to Silver - Data Cleaning & Partitioning
**As a** Data Engineer,
**I want** to use Polars to clean the raw multi-source data (Bronze),
**So that** it is standardized, deduplicated, and stored as optimized Parquet files in the Silver layer.

**Acceptance Criteria:**
- **Given** raw JSON/CSV files in the Bronze layer.
- **When** the Silver transformation job runs.
- **Then** columns are renamed to snake_case, nulls are handled, and duplicates are removed.
- **And** the data is written to `silver/` partitioned by `Year/Month/Day`.

### Story 3.2: Silver to Gold - Relational Serving & Reconciliation (C11, C14)
**As a** Data Analyst,
**I want** to reconcile the newly discovered RTE assets with their SQL metadata (Population, Area) during the Gold move,
**So that** our warehouse is always synchronized with the reality of the grid flux.

**Acceptance Criteria:**
- **Given** new assets discovered in Story 1.3.
- **When** the Gold transformation job runs.
- **Then** it performs a relational join in Azure SQL between the measurements and the asset registry.
- **And** it updates the `FACT_ENERGY_FLOW` with the most recent resolved metadata.

### Story 3.3: Data Quality Gates & Integrity Checks
**As a** Data Governor,
**I want** to implement automated quality checks between the Silver and Gold layers,
**So that** we ensure the integrity of the metrics served to the API.

**Acceptance Criteria:**
- **Given** the completion of a Gold ingestion job.
- **When** the quality gate script runs.
- **Then** it verifies that row counts match expectations and mandatory fields are non-null.
- **And** any failure triggers an alert in the audit logs.

### Epic 4: Secure Energy API & Reporting Layer
Expose the curated warehouse data through a secure, documented API for internal and external stakeholders.
**FRs covered:** FR12, FR13, FR14, FR15, FR21.

## Epic 4: Secure Energy API & Reporting Layer

**Goal:** Provide a secure and documented access point for the grid production data, enabling external consumption and reporting.

### Story 4.1: Production API Endpoints (FastAPI/Functions)
**As a** Developer,
**I want** to access regional production and carbon intensity data via RESTful endpoints,
**So that** I can build downstream applications or integrate the data into other systems.

**Acceptance Criteria:**
- **Given** an authenticated request to `/production/regional`.
- **When** valid query parameters (region_code, timeframe) are provided.
- **Then** the system returns a JSON response containing the aggregated metrics from the Gold SQL layer.
- **And** the response time is less than 500ms (NFR-P2).

### Story 4.2: Azure AD / JWT Security Implementation (C21)
**As a** Security Officer,
**I want** to ensure that all non-public API endpoints require valid Azure AD credentials,
**So that** our energy data is protected against unauthorized access.

**Acceptance Criteria:**
- **Given** an API request without a valid Bearer token.
- **When** accessing a protected endpoint.
- **Then** the API returns a 401 Unauthorized response.
- **And** valid tokens are verified against the configured Azure AD tenant.

### Story 4.3: Automated Swagger/OpenAPI Documentation
**As a** Developer,
**I want** to access a self-documenting API interface (Swagger UI),
**So that** I can easily test the endpoints and understand the data schema.

**Acceptance Criteria:**
- **Given** the API service is running.
- **When** navigating to the `/docs` or `/swagger` URL.
- **Then** a functional Swagger UI is displayed with all available endpoints, schemas, and authentication requirements.

### Epic 5: Operational Monitoring & Intelligent Alerting
Deliver the final user value through a real-time dashboard and proactive grid anomaly notifications.
**FRs covered:** FR16, FR17, FR18, FR21.

## Epic 5: Operational Monitoring & Intelligent Alerting

**Goal:** Provide Marc and the grid managers with high-level visibility and proactive alerting on grid health and production anomalies.

### Story 5.1: Grid Monitoring Dashboard (Azure Static Web App)
**As a** Grid Manager (Marc),
**I want** a modern web dashboard to visualize regional production peaks and demand trends,
**So that** I can make informed decisions about grid balancing.

**Acceptance Criteria:**
- **Given** the dashboard is deployed as an Azure Static Web App.
- **When** the page is loaded.
- **Then** it fetches real-time data from the API and displays interactive charts (Production per source, Carbon Intensity).
- **And** the interface is responsive and follows the UX design patterns.

### Story 5.2: Over-Production & Negative Price Alerts
**As a** Grid Manager (Marc),
**I want** to receive visual alerts when production exceeds demand or when prices are at risk of turning negative,
**So that** I can preemptively adjust the grid maintenance or export strategies.

**Acceptance Criteria:**
- **Given** the 15-minute data ingestion cycle.
- **When** the production-to-demand ratio exceeds the safety threshold (Alerting Logic).
- **Then** a high-priority "Risk Alert" is displayed on the dashboard.
- **And** the event is logged in the audit trail for later review.

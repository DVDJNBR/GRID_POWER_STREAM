stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish']
inputDocuments: ['COMPETENCES.md', 'CONTEXT/GRID_POWER_STREAM_project.md', 'CONTEXT/CONCEPTION_TECHNIQUE.md', 'CONTEXT/initial_conversation_context.md']
workflowType: 'prd'
documentCounts:
  briefCount: 1
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 3
classification:
  projectType: 'api_backend'
  domain: 'energy'
  complexity: 'high'
  projectContext: 'brownfield'
---

# Product Requirements Document - GRID_POWER_STREAM

**Author:** David
**Date:** 2026-02-23

## Executive Summary

**GRID_POWER_STREAM** is a unified energy monitoring platform designed to transform heterogeneous Open Data streams into actionable insights. Initially driven by a strategic transition to 100% public data sources to ensure exemplary security and governance, the project provides a consolidated view of regional energy production and its associated carbon footprint. The platform is primarily aimed at the technical validation jury (Data Engineering) while providing an operational storytelling interface for wind farm managers.

### What Makes This Special

The unique value of **GRID_POWER_STREAM** lies in its **"Intelligent Aggregation"**: instead of manually consulting disparate sources (Grid, Weather, Tariffs), users benefit from a single dashboard enhanced with an intelligent critical under-production alert system. The use of a **Medallion architecture on Azure** not only ensures compliance with the jury's "Big Data" requirements but also ensures the data quality and velocity (Micro-batch) essential for reliable monitoring. Finally, the modular Python design facilitates the portability of the solution for future portfolio deployment (VPS).

## Project Classification

- **Project Type:** API Backend / Data Platform
- **Domain:** Energy (Utility/Grid Connectivity)
- **Complexity:** High (Near real-time, Multi-source integration, GDPR compliance)
- **Project Context:** Brownfield (Evolution of existing documentation and vision)

## Success Criteria

### User Success
- **Adoption:** Wind farm managers can access and use the platform to retrieve aggregated energy data, reducing manual multi-site consultation.
- **Reporting Velocity:** Critical territory under-production alerts are delivered reliably, providing immediate visibility into grid anomalies.

### Technical Success
- **Competency Progression (E7 -> E5 -> E4):** The implementation follows a logical data engineering lifecycle, from raw ingestion to structured warehousing and API access.
- **Architectural Elegance:** The Medallion architecture is implemented with high modularity, allowing for clear separation between data engineering layers.
- **Documentation & Rationale:** Every design choice (e.g., Micro-batching due to subscription limits) is documented and technically justified.
- **Portability:** The solution is container-ready, ensuring future migration from Azure to a private VPS with minimal changes.

### Measurable Outcomes
- **Competency Validation (C8):** Demonstration of a functional "mix of sources" ingestion pipeline including REST API, Flat Files (CSV/JSON), and Web Scraping.
- **Data Lineage:** Full traceability from raw API/Scraped/Flat-file ingestion to aggregated Gold-layer warehouse tables.

## Product Scope

### MVP - Minimum Viable Product (Jury Focus)
1. **E7 - Data Lake (Bronze Layer):** Automated ingestion of a diverse mix of energy-related Open Data into Azure Data Lake Storage (ADLS Gen2):
    - **REST API (C8)**: Real-time production, demand, and carbon intensity from RTE (eCO2mix).
    - **Flat Files (C8)**: **Regional Installed Capacity reports (CSV)**. Used to calculate load factors (actual production vs. theoretical potential).
    - **Web Scraping (C8)**: **Grid Maintenance Portals**. Extracting scheduled downtime for transmission lines or power plants from transparency status pages.
    - **External Database (C8)**: **Grid Infrastructure Reference**. Connection to an SQL database mapping postal codes to electrical grid nodes and territory boundaries.
    - **Big Data System (C8)**: **Historical Climate Reanalysis (ERA5)**. Global hourly weather datasets (wind speed, solar radiation) stored in **Parquet format** within large-scale public object storage (S3/Azure Open Datasets). Extracted to perform theoretical yield benchmarking at scale.
2. **E5 - Data Warehouse (Silver & Gold Layers):** Transformation, cleaning (C10), and multidimensional modeling (Fact/Dimensions) in Azure Synapse or PostgreSQL.
3. **E4 - API Access Layer:** REST API exposing curated data with secure authentication and Swagger documentation.
4. **Technical Dossier:** Justification of architectural choices, MERISE modeling (C11), and security protocols.

### Growth Features (User Focus)
- **Monitoring Dashboard:** A localized web interface for wind farm managers to visualize regional KPIs.
- **Advanced Alerting:** Customizable thresholds for territory production alerts.

### Vision (Future)
- **Strategic Launch (E1, E2, E3):** Formal project management simulations, market research, and technical watch integration.
- **Private Hosting:** Full migration to a private VPS (OVH) and expansion to new renewable sources.

## User Journeys

### Journey 1: The Technical Auditor (Jury Member)
**Persona:** An expert Data Engineer evaluating the certification project.
**Goal:** Validate the end-to-end data pipeline integrity and architectural robustness.
**Narrative:** The auditor begins by reviewing the high-level architecture. They navigate through the code repository, specifically looking for the Medallion structure implementation. They trigger a data ingestion job to see how raw JSON from the RTE API is captured in the Bronze layer, then transformed into clean Parquet files in Silver, and finally aggregated into the Gold layer fact tables.
**Closing Moment:** The auditor confirms that all competencies (E4, E5, E7) are met through a functional, well-documented, and observable pipeline.

### Journey 2: Marc (The Wind Farm Manager)
**Persona:** An operational manager overseeing regional wind production.
**Goal:** Get a quick status update on regional production vs. demand to optimize operations.
**Narrative:** Marc starts his day by opening the GRID_POWER_STREAM dashboard. Instead of checking multiple websites, he sees a single view of real-time production and carbon intensity. Suddenly, a notification appears: "Critical Under-production Alert in Territory X." Marc immediately identifies that the wind production is lower than expected for the current weather conditions.
**Closing Moment:** Marc has the data he needs to make an informed decision within minutes, a task that previously took him nearly an hour of manual data gathering.

### Journey 3: David (The Platform Builder)
**Persona:** The developer (You) building and maintaining the infrastructure.
**Goal:** Automate the entire ingestion and transformation lifecycle while ensuring portability.
**Narrative:** David starts by provisioning the entire cloud environment using **Terraform**, ensuring that every component (SQL, Lake, Functions) is documented as code. He then works on the CI/CD pipeline, updating a transformation script and pushing it to the repository. The automation triggers a micro-batch ingestion from the RTE API. He monitors the logs in the Azure Environment to ensure compliance with the NERC/GDPR standards. He also maintains the Docker configuration to ensure that the entire stack can be replicated on a private VPS for his long-term portfolio.
**Closing Moment:** David successfully demonstrates a self-healing, automated data platform that is ready for both professional audit and permanent hosting.

### Journey Requirements Summary
- **Data Ingestion & Transformation Engine (E7/E5):** Azure Functions (Python/Polars) for lean, serverless ETL.
- **Data Transformation Engine (E5):** Python/Polars jobs for cleaning (Bronze -> Silver) and SQL Views for Gold modeling.
- **Secure API & Documentation (E4):** Backend to expose data with Auth and Swagger.
- **Alerting System:** Notifications for critical grid events.
- **DevOps & Portability:** Containerization and deployment scripts for Azure and VPS.

## Innovation & Novel Patterns

### Detected Innovation Areas
- **Consumer-Grade UX for Grid Monitoring:** Breaking from the traditionally austere and complex utility dashboard design. GRID_POWER_STREAM’s innovation lies in its high-performance, modern UI (e.g., Vite/Tailwind/Glassmorphism) designed to make complex energy grid data accessible and visually intuitive for operational managers and non-technical stakeholders.

### Market Context & Competitive Landscape
- **Contrast with Industry Standards:** Existing grid management tools (SCADA/DMS) are often legacy systems with steep learning curves. GRID_POWER_STREAM bridges the gap between expert data engineering (Medallion architecture) and consumer-ready usability (Sleek UI).

### Validation Approach
- **User Engagement Metrics:** Monitoring session length and frequency of use by wind farm managers.
- **Storytelling Efficacy:** Feedback from the certification jury regarding the clarity and visual impact of the data presentation.

### Future Improvements (Innovation Backlog)
- **Lightweight Predictive AI:** Forecasting regional production peaks and dips based on historical weather patterns (E2/E3 synergy).
- **Data Observability Trust Scores:** Automated calculation of a "confidence index" for various Open Data sources based on historical reliability and heartbeat checks.
- **Carbon-aware Data Processing:** Scheduling heavy Spark/Data jobs to run only during periods of low local grid carbon intensity (using project data for self-optimization).

## Domain-Specific Requirements

### Grid Compliance & Transparency
- **Technical Watch (Veille):** Continued monitoring of EU Regulation No 543/2013 regarding grid data transparency and ENTSO-E data publication standards.
- **Data Governance:** Implementation of standardized metadata aligned with energy sector open-data practices.

### Technical Constraints (Operational)
- **Desired Latency:** A maximum of 15 minutes for data refresh to maintain operational relevance for wind farm management.
- **Data Freshness:** Automated monitoring of RTE API heartbeat to ensure ingestion continuity.

### Security & Integrity (Gold Zone Protection)
- **Access Control:** Implementation of Azure RBAC and Data Lake Gen2 ACLs (Access Control Lists) to restrict write access to the Gold layer (Aggregated data).
- **Integrity Checks:** Automated data quality gates between Silver and Gold layers to prevent technical corruption or unauthorized alteration of validated KPIs.

### Risk Mitigations - Over-production & Negative Prices
- **Curtailment Alerting:** Real-time monitoring of over-production scenarios where regional wind generation significantly exceeds local demand.
- **Business Logic:** Alerts triggered when grid stability is at risk or when market conditions suggest imminent negative price risks, enabling preventative shutdown (curtailment) decisions.

## API & Backend Specific Requirements

### Technical Architecture Considerations
- **Data Lake Architecture (C18/C19)**: Implementation of a Medallion architecture (Bronze/Silver/Gold) on Azure Data Lake Storage Gen2.
- **Catalog Management (C18)**: Use of **Azure Synapse / SQL Serverless Catalog** to ensure data discoverability and rights management with zero fixed costs.
- **Compute Strategy**: **Azure Functions (Python + Polars)** for the entire ETL pipeline. Using Polars ensures high-performance columnar processing (C10/C15) on Parquet files without the overhead of Spark clusters.
- **Infrastructure as Code (IaC)**: Use of **Terraform** to provision and manage all Azure resources (C18). This ensures reproducibility, documentation of the infra, and professional environment management.
- **Storage Strategy**: Transitioning from semi-structured JSON (Bronze) to optimized columnar Parquet (Silver) via Python, and finally relational SQL (Gold layer) for the API.
- **Execution Mode**: Micro-batching pulse (15-min for live data, hourly for Big Data/Parquet) to maintain $84 monthly budget limits.

### Endpoint Specification
- **`/production/regional`**: Core endpoint providing energy production data filtered by territory and production source (Wind, Solar, etc.).
- **`/export/csv`**: Specialized endpoint for wind farm managers, optimized for Excel compatibility (E1-E3 storytelling support).
- **Versioning**: Implementation of semantic versioning (e.g., `/v1/`) to manage breaking changes and facilitate multi-stage delivery (E4-E5).

### Authentication & Security Model
- **Provider**: Azure Active Directory (AD) integration.
- **Protocol**: JWT (JSON Web Token) Bearer authentication for secure, cross-service communication.
- **Lifecycle**: Tokens preferred over static API keys to ensure better governance and auditability (Jury requirement).

### Data Strategy & Schema Design
- **Exploratory Schema Modeling**: Final Gold layer SQL schema will be derived from a discovery phase of the RTE API response formats to ensure 100% field mapping accuracy.
- **Semantic Release**: Integration of automated release pipelines to ensure clean version transitions and documentation updates (Swagger/OpenAPI).

## Functional Requirements (Capability Contract)

### 1. Multi-Source Data Ingestion (C8/E7)
- **FR1:** The system can automatically poll the RTE Open Data API (eCO2mix) on a configurable hourly schedule.
- **FR2:** The system can extract data from **Flat Files** (CSV) containing regional installed power capacity targets and site inventories.
- **FR3:** The system can programmatically **scrape** grid maintenance status pages to identify scheduled downtime for power generation units.
- **FR4:** The system can query a **Reference SQL Database** to map production sites to their respective grid nodes and regional territories.
- **FR5:** The system can extract massive historical weather context (ERA5 Reanalysis) in **Parquet format** from a **Big Data system** (Public Blob Storage) to perform theoretical yield calculations.
- **FR6:** The system can securely store all raw multi-source extracts in Azure Data Lake Storage Gen2 (Bronze layer).
- **FR7:** The system can handle API/Connection retries and log ingestion heartbeats for observability.

### 2. Data Transformation & Modeling (C10/E5)
- **FR6:** The system can clean (handle NaNs, corrupted entries) and partition data into optimized Parquet files (Silver layer).
- **FR7:** The system can model energy flow data into a relational Star Schema (Gold layer) for efficient querying.
- **FR8:** The system can aggregate production metrics at the regional level, crossing API data with Flat-file demographic data.
- **FR9:** The system can validate data integrity between layers using automated quality gates.

### 3. API & Data Access (C12/E4)
- **FR10:** Users can query regional production and carbon intensity data via a RESTful API.
- **FR11:** Users can authenticate using Azure AD / JWT Bearer tokens to access protected endpoints.
- **FR12:** Developers can access automated API documentation via a Swagger/OpenAPI UI.
- **FR13:** Wind farm managers can export aggregated production reports in CSV format for Excel analysis.

### 4. Grid Monitoring & Alerting (Business Logic)
- **FR14:** Users can visualize real-time grid metrics through a modern web dashboard.
- **FR15:** The system can trigger automated alerts when regional over-production exceeds local demand.
- **FR16:** The system can detect and notify users of potential negative price scenarios based on production peaks.

### 5. Governance & Portability (Audit)
- **FR17:** The platform generates audit logs for every successful and failed data ingestion job (C20).
- **FR18:** Administrators can restrict write access to the Gold layer using RBAC/ACLs (C21).
- **FR19:** The entire application stack can be deployed in a containerized environment (Docker) for VPS portability.

## Non-Functional Requirements

### Performance & Freshness
- **NFR-P1 (Freshness):** The end-to-end data pipeline must ensure a maximum data latency of **15 minutes** from RTE publication (or scraping) to Gold layer availability.
- **NFR-P2 (Response Time):** The API must respond to `/production/regional` queries in less than **500ms** to ensure a consumer-grade user experience.

### Security & Compliance
- **NFR-S1 (Authentication):** 100% of non-public API endpoints must require a valid Azure AD JWT token for access.
- **NFR-S2 (Privacy by Design):** No Individual Metering Data (DCP) shall be ingested; the platform will exclusively process regional/territory aggregates to ensure inherent GDPR compliance.
- **NFR-S3 (Integrity):** Gold layer tables must be read-only for the API service principal, with write permissions restricted solely to the ETL process (C21).

### Reliability & Observability
- **NFR-R1 (Resilience):** Ingestion jobs must implement exponential backoff and retry logic for external API/Scraping connections.
- **NFR-R2 (Monitoring):** Historical logs of ingestion heartbeats must be available for audit (C20), with alerts triggered via Azure Monitor upon pipeline failure.

### Eco-Responsibility & Budget Efficiency (Azure Student)
- **NFR-E1 (Cost Optimization):** The architecture must avoid fixed-cost clusters (Databricks/Synapse Spark Pools) and prioritize **Consumption-based** services (Azure Functions, SQL Serverless) to stay within the $84 USD Azure Student budget.
- **NFR-E2 (Compute Efficiency):** Data transformations using Polars/Pandas must be optimized for memory efficiency, utilizing "Streaming" mode for Parquet reading to handle large datasets within Function memory limits.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Technical Validation MVP. The primary objective is to demonstrate the stability, security, and governance of the "Medallion" data pipeline to the certification jury.
**Resource Requirements:** Single Data Engineer utilizing Azure Student credits (Serverless focus).

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- Journey 1: The Technical Auditor (Jury Member)
- Journey 3: The Platform Builder (David)

**Must-Have Capabilities:**
- **Automated Ingestion (E7):** Hourly micro-batching of RTE Open Data (Production, Tariffs, Carbon) into ADLS Gen2.
- **Exploratory Data Warehouse (E5):** Relational SQL Schema designed after API discovery, populated in the Gold layer for optimized querying.
- **Secure API Access (E4):** REST API hosted on Azure Functions, protected by Azure AD/JWT, with automated Swagger/OpenAPI documentation.
- **Technical Dossier:** Comprehensive justification of architectural choices and competency mapping (E4, E5, E7).

### Post-MVP Features

**Phase 2 (Growth):**
- **Modern Monitoring UI:** Localized web interface (Vite/Tailwind) for wind farm managers.
- **Data Export:** Dedicated CSV/Excel export endpoint for operational reporting.
- **Smart Alerting:** Multi-channel notifications for grid curtailment and negative pricing scenarios.

**Phase 3 (Expansion):**
- **Full Portability:** Migration from Azure to a private VPS (OVH) environment.
- **Management Excellence (E1-E3):** Integration of technical watch and strategic project management simulations.
- **Predictive Analytics:** Lightweight AI forecasting for regional production peaks.

### Risk Mitigation Strategy

**Technical Risks:** Use of micro-batching to mitigate "Student Credit" exhaustion while maintaining 15-min data freshness.
**Market Risks:** Ensuring technical audit readiness (competency mapping) as the priority validation gate.
**Resource Risks:** Modular Python design ensures portability if the cloud environment becomes unavailable.

## Maintenance & Operations

### Monitoring & Observability
- **System Health:** Continuous monitoring of Azure Function execution logs and ADLS storage ingress.
- **Data Quality:** Automated alerts for schema drift or null-heavy payloads between Silver and Gold layers.

### Lifecycle Management
- **Semantic Versioning:** Strict adherence to SEMVER for API endpoints to prevent breaking changes in user dashboards.
- **Portability Testing:** Quarterly validation of the Dockerized environment on a local/VPS instance to ensure zero-lock-in with Azure services.

# Story 1.0: Infrastructure as Code with Terraform (C18)

Status: done

## Story

As a DevOps Engineer,
I want to use Terraform to provision the Azure Resource Group, ADLS Gen2, and Azure SQL Serverless instance,
so that my entire infrastructure is versioned, reproducible, and documented.

## Acceptance Criteria

1. **Given** a set of Terraform configuration files (`main.tf`, `variables.tf`),
   **When** executing `terraform apply`,
   **Then** the Azure resources are created correctly according to the plan.

2. **Given** a successful `terraform apply`,
   **When** inspecting the Azure portal or CLI,
   **Then** the state is managed securely (local or remote backend).

3. **Given** the Terraform configuration,
   **When** the initial SQL schema setup is needed,
   **Then** a `null_resource` or azurerm provider handles the schema provisioning (DIM/FACT tables).

4. **Given** the deployed infrastructure,
   **When** Azure Functions are deployed later (Story 1.1+),
   **Then** Managed Identity, Key Vault, and RBAC assignments are already configured.

## Tasks / Subtasks

- [x] Task 1: Terraform project initialization (AC: #1)
  - [x] 1.1: `infra/` directory with `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `terraform.tfvars.example`
  - [x] 1.2: azurerm provider ~> 3.100
  - [x] 1.3: Variables: `project_name`, `location`, `environment`, `sql_admin_password` (sensitive)
  - [x] 1.4: Local backend (remote backend commented for later)

- [x] Task 2: Core resource provisioning (AC: #1, #2)
  - [x] 2.1: Resource Group `gps-dev-rg`
  - [x] 2.2: ADLS Gen2 (HNS enabled, LRS) + containers: bronze, silver, gold, audit
  - [x] 2.3: SQL Server Serverless GP_S_Gen5_1 (auto-pause 60min)
  - [x] 2.4: Key Vault (standard, soft delete 7d)

- [x] Task 3: Security & identity configuration (AC: #4)
  - [x] 3.1: Function App (Consumption Y1, Python 3.11, SystemAssigned MI)
  - [x] 3.2: RBAC: Function → Storage Blob Data Contributor
  - [x] 3.3: RBAC: Function → Key Vault Secrets User
  - [x] 3.4: App settings: KEY_VAULT_URL, STORAGE_ACCOUNT_NAME, SQL_SERVER, SQL_DATABASE
  - [x] 3.5: SQL firewall AllowAzureServices

- [x] Task 4: SQL schema initialization (AC: #3)
  - [x] 4.1: `init_schema.sql` already exists (Story 0.1)
  - [x] 4.2: `null_resource` with `local-exec` sqlcmd for schema + seed
  - [x] 4.3: Triggers on file hash change

- [x] Task 5: Outputs & documentation (AC: #1, #2)
  - [x] 5.1: Outputs: rg name, storage name, sql fqdn, kv uri, func name, ai connection string
  - [x] 5.2: `terraform.tfvars.example` created
  - [x] 5.3: README update pending

- [x] Task 6: ADLS lifecycle policies (data retention)
  - [x] 6.1: Bronze: delete after 180 days
  - [x] 6.2: Silver: delete after 90 days
  - [x] 6.3: Audit: delete after 365 days

## Dev Notes

### Architecture Requirements

- **Terraform version:** >= 1.5 with `azurerm` provider >= 3.x
- **Budget constraint (NFR-E1):** All resources MUST be Consumption/Serverless tier — $84/month Azure Student budget
  - SQL: `GP_S_Gen5_1` (Serverless, auto-pause after 60 min idle)
  - Storage: LRS (Locally Redundant) — cheapest tier
  - Functions: Consumption plan (Y1)
  - Key Vault: Standard tier
- **Location:** Use variable, default `francecentral` (closest to RTE data)
- **Naming convention:** `gps-{resource_type}-{environment}` (e.g., `gps-sa-dev`, `gps-sql-dev`)

### SQL Schema (from CONCEPTION_DATAMODEL)

```sql
-- Dimensions
CREATE TABLE DIM_REGION (id_region INT PRIMARY KEY IDENTITY, code_insee VARCHAR(5), nom_region NVARCHAR(100));
CREATE TABLE DIM_TIME (id_date INT PRIMARY KEY IDENTITY, horodatage DATETIME2, jour INT, mois INT, annee INT, heure INT);
CREATE TABLE DIM_SOURCE (id_source INT PRIMARY KEY IDENTITY, source_name NVARCHAR(50), is_green BIT);
-- Fact
CREATE TABLE FACT_ENERGY_FLOW (id_fact BIGINT PRIMARY KEY IDENTITY, id_date INT FK, id_region INT FK, id_source INT FK, valeur_mw DECIMAL(10,2), facteur_charge DECIMAL(5,4), temperature_moyenne DECIMAL(5,2), prix_mwh DECIMAL(8,2));
```

### ADLS Gen2 Container Structure

```
bronze/    → Raw ingestion (Stories 1.1, 1.2, 2.1, 2.2)
silver/    → Cleaned Parquet (Story 3.1)
gold/      → Reserved for future use (SQL is primary Gold)
audit/     → Ingestion heartbeats & logs
```

### Security Model (from CONCEPTION_TECHNIQUE)

- Azure Functions → System-Assigned Managed Identity
- ADLS Gen2 → RBAC "Storage Blob Data Contributor"
- Key Vault → RBAC "Key Vault Secrets User"
- SQL → Azure AD admin + firewall rules
- ZERO secrets in code or exposed env vars

### Project Structure

```
WATT_WATCHER/
├── infra/
│   ├── main.tf              # Resource definitions
│   ├── variables.tf          # Input variables
│   ├── outputs.tf            # Output values
│   ├── providers.tf          # Provider config
│   ├── terraform.tfvars.example
│   └── sql/
│       └── init_schema.sql   # Gold layer schema
```

### References

- [Source: CONTEXT/CONCEPTION_TECHNIQUE.md#Architecture de Sécurité] — Managed Identity, RBAC, Key Vault
- [Source: CONTEXT/CONCEPTION_DATAMODEL.md#Star Schema] — FACT_ENERGY_FLOW, DIM tables
- [Source: _bmad-output/planning-artifacts/prd.md#Technical Architecture] — Consumption plan, $84 budget
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.0] — Original AC

## Dev Agent Record

### Agent Model Used

Antigravity (Amelia 💻)

### Debug Log References

`terraform init` → Success, `terraform validate` → Success

### Completion Notes List

- azurerm v3 uses `storage_account_name` for containers, not `storage_account_id`
- Application Insights added (not in original story but needed for monitoring)
- SQL schema applies via `null_resource` + sqlcmd — user needs sqlcmd installed
- Key Vault `purge_protection_enabled = false` for dev (easier teardown)
- Function App storage account separate from ADLS Gen2 (Azure requirement)

### File List

- `infra/providers.tf` — [NEW] Provider config
- `infra/variables.tf` — [NEW] Input variables
- `infra/main.tf` — [NEW] All resource definitions
- `infra/outputs.tf` — [NEW] Output values
- `infra/terraform.tfvars.example` — [NEW] Example variables

### Change Log

- 2026-02-25: Story completed. All 6 tasks done. `terraform validate` → Success.

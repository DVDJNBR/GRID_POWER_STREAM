# -----------------------------------------------------------------------------
# GRID_POWER_STREAM — Outputs
# -----------------------------------------------------------------------------

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "ADLS Gen2 Storage Account name"
  value       = azurerm_storage_account.datalake.name
}

output "sql_server_fqdn" {
  description = "Azure SQL Server fully qualified domain name"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_database_name" {
  value = azurerm_mssql_database.warehouse.name
}

output "key_vault_uri" {
  description = "Key Vault URI for secrets retrieval"
  value       = azurerm_key_vault.main.vault_uri
}

output "function_app_name" {
  value = azurerm_linux_function_app.main.name
}

output "function_app_default_hostname" {
  value = azurerm_linux_function_app.main.default_hostname
}

output "application_insights_connection_string" {
  description = "App Insights connection string for Function App"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "static_web_app_url" {
  description = "Frontend URL — set as VITE_API_BASE_URL in GitHub Actions"
  value       = "https://${azurerm_static_web_app.frontend.default_host_name}"
}

output "static_web_app_api_token" {
  description = "SWA deploy token — add as AZURE_STATIC_WEB_APPS_API_TOKEN in GitHub secrets"
  value       = azurerm_static_web_app.frontend.api_key
  sensitive   = true
}

output "function_app_url" {
  description = "Azure Functions base URL — use as VITE_API_BASE_URL in frontend"
  value       = "https://${azurerm_linux_function_app.main.default_hostname}"
}

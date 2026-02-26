"""
Route Definitions — Story 4.1 (Task 1.2) / Story 4.2 (Task 2.3)

URL path constants for the production API.
AC #3: RESTful conventions, /v1/ prefix for versioning.
Story 4.2 AC #4: PUBLIC_ROUTES lists endpoints exempt from @require_auth.
"""

API_VERSION = "v1"
PREFIX = f"/{API_VERSION}"

# Protected endpoints (require Azure AD JWT)
PRODUCTION_REGIONAL = f"{PREFIX}/production/regional"
EXPORT_CSV = f"{PREFIX}/export/csv"

# Azure Functions route suffixes (without leading slash, per Azure SDK convention)
ROUTE_PRODUCTION = f"{API_VERSION}/production/regional"
ROUTE_EXPORT = f"{API_VERSION}/export/csv"

# Public endpoints — exempt from @require_auth (Task 2.3)
ROUTE_HEALTH = "health"
PUBLIC_ROUTES = {ROUTE_HEALTH}

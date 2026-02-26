"""
Route Definitions — Story 4.1, Task 1.2

URL path constants for the production API.
AC #3: RESTful conventions, /v1/ prefix for versioning.
"""

API_VERSION = "v1"
PREFIX = f"/{API_VERSION}"

# Endpoint paths — AC #1, #4
PRODUCTION_REGIONAL = f"{PREFIX}/production/regional"
EXPORT_CSV = f"{PREFIX}/export/csv"

# Azure Functions route suffixes (without leading slash, per Azure SDK convention)
ROUTE_PRODUCTION = f"{API_VERSION}/production/regional"
ROUTE_EXPORT = f"{API_VERSION}/export/csv"

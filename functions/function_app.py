"""
GRID_POWER_STREAM — Azure Function App Entry Point

Story 1.1: Timer trigger — RTE eCO2mix ingestion → Bronze layer.
Story 4.1: HTTP triggers — /v1/production/regional, /v1/export/csv.
"""

import json
import logging
import os
import uuid
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    import azure.functions as func

try:
    import azure.functions as func  # type: ignore[no-redef]
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False

from shared.rte_client import RTEClient, RTEClientError
from shared.bronze_storage import BronzeStorage
from shared.audit_logger import AuditLogger
from shared.api.models import parse_production_request, parse_export_request
from shared.api.production_service import query_production
from shared.api.export_service import export_to_csv
from shared.api.error_handlers import bad_request, not_found, server_error
from shared.api.routes import ROUTE_PRODUCTION, ROUTE_EXPORT
from shared.api.auth import require_auth

logger = logging.getLogger(__name__)


# ─── DB connection helper ────────────────────────────────────────────────────

def _get_db_connection() -> Any:
    """
    Return a Gold SQL DB connection.

    Production: pyodbc with Managed Identity.
    Local dev: falls back to environment variable SQL_CONNECTION_STRING.
    """
    conn_str = os.environ.get("SQL_CONNECTION_STRING", "")
    if not conn_str:
        raise EnvironmentError("SQL_CONNECTION_STRING not set")

    try:
        import pyodbc  # type: ignore[import]
        return pyodbc.connect(conn_str)
    except ImportError as e:
        raise RuntimeError("pyodbc not available") from e


# ─── Function App ───────────────────────────────────────────────────────────

if AZURE_FUNCTIONS_AVAILABLE:
    app = func.FunctionApp()

    # ── Story 1.1: RTE ingestion timer ──────────────────────────────────────

    @app.timer_trigger(
        schedule="0 */15 * * * *",  # every 15 minutes
        arg_name="timer",
        run_on_startup=False,
    )
    def rte_ingestion(timer: func.TimerRequest) -> None:
        """Timer-triggered RTE eCO2mix ingestion to Bronze layer."""
        job_id = str(uuid.uuid4())
        logger.info("Starting RTE ingestion job: %s", job_id)
        run_ingestion(job_id=job_id)

    # ── Story 4.1: Production regional endpoint ──────────────────────────────

    @app.route(route=ROUTE_PRODUCTION, methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_auth
    def get_production_regional(req: func.HttpRequest) -> func.HttpResponse:
        """
        GET /v1/production/regional

        AC #1: Returns aggregated production metrics from Gold SQL.
        AC #2: <500ms target (parameterized queries + SQL indexes).
        AC #3: RESTful — 200, 400, 404, 500.
        """
        request_id = str(uuid.uuid4())

        prod_req, validation_error = parse_production_request(dict(req.params))
        if validation_error:
            body = bad_request(validation_error, request_id)
            return func.HttpResponse(
                json.dumps(body), status_code=400,
                mimetype="application/json",
                headers={"X-Request-Id": request_id},
            )

        try:
            conn = _get_db_connection()
            result = query_production(
                conn,
                region_code=prod_req.region_code,
                start_date=prod_req.start_date,
                end_date=prod_req.end_date,
                source_type=prod_req.source_type,
                limit=prod_req.limit,
                offset=prod_req.offset,
                request_id=request_id,
            )

            if not result["data"]:
                body = not_found(request_id=request_id)
                return func.HttpResponse(
                    json.dumps(body), status_code=404,
                    mimetype="application/json",
                    headers={"X-Request-Id": request_id},
                )

            return func.HttpResponse(
                json.dumps(result), status_code=200,
                mimetype="application/json",
                headers={"X-Request-Id": request_id},
            )

        except Exception as exc:
            logger.error("production endpoint error [%s]: %s", request_id, exc, exc_info=True)
            body = server_error(request_id=request_id)
            return func.HttpResponse(
                json.dumps(body), status_code=500,
                mimetype="application/json",
                headers={"X-Request-Id": request_id},
            )

    # ── Story 4.1: CSV export endpoint ──────────────────────────────────────

    @app.route(route=ROUTE_EXPORT, methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_auth
    def get_export_csv(req: func.HttpRequest) -> func.HttpResponse:
        """
        GET /v1/export/csv

        AC #4: Returns downloadable CSV with UTF-8 BOM, semicolon separator.
        AC #3: RESTful — 200, 400, 404, 500.
        """
        request_id = str(uuid.uuid4())
        export_req = parse_export_request(dict(req.params))

        try:
            conn = _get_db_connection()
            csv_bytes, filename, row_count = export_to_csv(
                conn,
                region_code=export_req.region_code,
                start_date=export_req.start_date,
                end_date=export_req.end_date,
                source_type=export_req.source_type,
                request_id=request_id,
            )

            if row_count == 0:
                body = not_found(request_id=request_id)
                return func.HttpResponse(
                    json.dumps(body), status_code=404,
                    mimetype="application/json",
                    headers={"X-Request-Id": request_id},
                )

            return func.HttpResponse(
                csv_bytes,
                status_code=200,
                mimetype="text/csv; charset=utf-8",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "X-Request-Id": request_id,
                },
            )

        except Exception as exc:
            logger.error("export endpoint error [%s]: %s", request_id, exc, exc_info=True)
            body = server_error(request_id=request_id)
            return func.HttpResponse(
                json.dumps(body), status_code=500,
                mimetype="application/json",
                headers={"X-Request-Id": request_id},
            )


def run_ingestion(
    job_id: str | None = None,
    local_mode: bool = False,
) -> dict:
    """
    Core ingestion logic — callable both from Azure Function and locally.

    Args:
        job_id: Unique job identifier.
        local_mode: If True, write to local filesystem instead of ADLS.

    Returns:
        Audit log entry dict.
    """
    job_id = job_id or str(uuid.uuid4())

    # Initialize modules
    storage_account = os.environ.get("STORAGE_ACCOUNT_NAME") if not local_mode else None
    bronze = BronzeStorage(
        storage_account_name=storage_account,
        local_mode=local_mode,
    )
    audit = AuditLogger(source="rte_eco2mix", bronze_storage=bronze)
    client = RTEClient()

    try:
        # Fetch latest records (last 30 minutes to handle overlap)
        records = client.fetch_all_recent(minutes=30)

        if not records:
            logger.info("No records returned from API")
            return audit.log_success(record_count=0, job_id=job_id)

        # Write raw JSON to Bronze
        path = bronze.write_json(records)
        logger.info("Written %d records to %s", len(records), path)

        # Audit success
        return audit.log_success(
            record_count=len(records),
            job_id=job_id,
            details={"bronze_path": path},
        )

    except RTEClientError as e:
        logger.error("RTE API error: %s", e)
        return audit.log_failure(
            error=str(e),
            job_id=job_id,
        )

    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        return audit.log_failure(
            error=f"Unexpected: {e}",
            job_id=job_id,
        )


# ─── Local dev entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_ingestion(local_mode=True)
    print(f"\nResult: {result['status']} — {result['record_count']} records")

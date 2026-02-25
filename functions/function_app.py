"""
GRID_POWER_STREAM — Azure Function App Entry Point
Story 1.1: Automated RTE eCO2mix API Ingestion

Timer trigger: every 15 minutes → fetch eCO2mix → store in Bronze → audit log.
"""

import logging
import os
import uuid
from typing import TYPE_CHECKING

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

logger = logging.getLogger(__name__)

# ─── Function App ───────────────────────────────────────────────────────────

if AZURE_FUNCTIONS_AVAILABLE:
    app = func.FunctionApp()

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

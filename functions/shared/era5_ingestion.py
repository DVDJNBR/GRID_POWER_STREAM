"""
ERA5 Climate Ingestion Module — Story 2.2, Task 2

Reads ERA5 Parquet data using Polars streaming mode for memory efficiency.
Computes derived fields (wind speed magnitude) and writes partitioned
output to Bronze layer.

Key design decisions:
- pl.scan_parquet() for lazy/streaming evaluation (NFR-E2)
- Chunked processing by month to respect Azure Function 10-min timeout
- Checkpoint mechanism to track last processed timestamp
"""

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

logger = logging.getLogger(__name__)

# France metropolitan bounding box (approximate)
FRANCE_LAT_MIN = 41.3
FRANCE_LAT_MAX = 51.1
FRANCE_LON_MIN = -5.2
FRANCE_LON_MAX = 9.6

# Region centroids for nearest-neighbor mapping
REGION_CENTROIDS = {
    "11": (48.86, 2.35),    # Île-de-France
    "24": (47.39, 1.69),    # Centre-Val de Loire
    "27": (47.47, -0.55),   # Bourgogne-Franche-Comté
    "28": (48.51, -2.76),   # Bretagne
    "32": (48.30, 7.44),    # Grand Est
    "44": (50.63, 3.06),    # Hauts-de-France
    "52": (49.12, -0.37),   # Normandie
    "53": (47.22, -1.55),   # Pays de la Loire
    "75": (46.58, 0.34),    # Nouvelle-Aquitaine
    "76": (43.60, 1.44),    # Occitanie
    "84": (45.76, 4.83),    # Auvergne-Rhône-Alpes
    "93": (43.30, 5.37),    # PACA
}


class ERA5Ingestion:
    """Ingest ERA5 climate Parquet data to Bronze layer."""

    def __init__(self, bronze_storage=None, audit_logger=None):
        """
        Args:
            bronze_storage: BronzeStorage instance for writing output.
            audit_logger: AuditLogger instance for heartbeat logging.
        """
        self.bronze = bronze_storage
        self.audit = audit_logger

    def ingest_parquet(
        self,
        source_path: str | Path,
        output_dir: str | Path | None = None,
    ) -> dict:
        """
        Ingest ERA5 Parquet using Polars streaming mode.

        AC #1: Pull hourly data, partition by region/month.
        AC #2: Use scan_parquet (lazy) for memory efficiency.

        Args:
            source_path: Path to ERA5 Parquet file.
            output_dir: Local output directory (dev mode). If None, uses Bronze storage.

        Returns:
            Summary dict: {total_rows, files_written, regions_processed}.
        """
        source_path = Path(source_path)
        logger.info("Scanning ERA5 Parquet: %s", source_path)

        # AC #2: Lazy scan — no data loaded into memory yet
        lf = pl.scan_parquet(source_path)

        # Filter to France bounding box (lazy)
        lf = lf.filter(
            (pl.col("latitude") >= FRANCE_LAT_MIN)
            & (pl.col("latitude") <= FRANCE_LAT_MAX)
            & (pl.col("longitude") >= FRANCE_LON_MIN)
            & (pl.col("longitude") <= FRANCE_LON_MAX)
        )

        # Compute derived fields (lazy)
        lf = lf.with_columns([
            # Wind speed at 100m from u/v components
            (pl.col("u100").pow(2) + pl.col("v100").pow(2)).sqrt().alias("wind_speed_100m"),
            # Temperature in Celsius
            (pl.col("t2m") - 273.15).round(2).alias("temperature_c"),
            # Extract date parts for partitioning
            pl.col("valid_time").dt.year().alias("year"),
            pl.col("valid_time").dt.month().alias("month"),
        ])

        # Map grid points to nearest region
        lf = self._map_to_regions(lf)

        # AC #2: Collect with streaming=True for memory efficiency
        df = lf.collect(engine="streaming")

        if df.is_empty():
            logger.warning("No ERA5 data after filtering")
            if self.audit:
                self.audit.log_success(record_count=0, details={"era5": "no_data"})
            return {"total_rows": 0, "files_written": 0, "regions_processed": []}

        # Write partitioned output
        files_written = self._write_partitioned(df, output_dir)

        summary = {
            "total_rows": len(df),
            "files_written": files_written,
            "regions_processed": df["region_code"].unique().sort().to_list(),
        }

        logger.info(
            "ERA5 ingestion: %d rows, %d files, %d regions",
            summary["total_rows"],
            summary["files_written"],
            len(summary["regions_processed"]),
        )

        if self.audit:
            self.audit.log_success(
                record_count=len(df),
                details={"era5": summary},
            )

        return summary

    def ingest_chunked(
        self,
        source_path: str | Path,
        output_dir: str | Path | None = None,
        chunk_months: int = 1,
    ) -> dict:
        """
        AC #3: Chunked processing for large files to avoid Function timeout.

        Processes data month by month to stay within 10-min limit.
        """
        source_path = Path(source_path)
        lf = pl.scan_parquet(source_path)

        # Get time range
        time_range = lf.select([
            pl.col("valid_time").min().alias("min_time"),
            pl.col("valid_time").max().alias("max_time"),
        ]).collect()

        min_time = time_range["min_time"][0]
        max_time = time_range["max_time"][0]

        total_rows = 0
        total_files = 0
        all_regions = set()

        # Process month by month
        current = min_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        while current <= max_time:
            next_month = current.replace(
                month=current.month % 12 + 1,
                year=current.year + (1 if current.month == 12 else 0),
            )

            chunk_lf = lf.filter(
                (pl.col("valid_time") >= current)
                & (pl.col("valid_time") < next_month)
            )

            result = self.ingest_parquet.__wrapped__(self, chunk_lf, output_dir) if hasattr(self.ingest_parquet, '__wrapped__') else self._process_lazy_frame(chunk_lf, output_dir)

            total_rows += result["total_rows"]
            total_files += result["files_written"]
            all_regions.update(result["regions_processed"])

            logger.info("Chunk %s: %d rows", current.strftime("%Y-%m"), result["total_rows"])
            current = next_month

        return {
            "total_rows": total_rows,
            "files_written": total_files,
            "regions_processed": sorted(all_regions),
        }

    def _process_lazy_frame(
        self, lf: pl.LazyFrame, output_dir: str | Path | None
    ) -> dict:
        """Process a lazy frame chunk."""
        lf = lf.filter(
            (pl.col("latitude") >= FRANCE_LAT_MIN)
            & (pl.col("latitude") <= FRANCE_LAT_MAX)
            & (pl.col("longitude") >= FRANCE_LON_MIN)
            & (pl.col("longitude") <= FRANCE_LON_MAX)
        )

        lf = lf.with_columns([
            (pl.col("u100").pow(2) + pl.col("v100").pow(2)).sqrt().alias("wind_speed_100m"),
            (pl.col("t2m") - 273.15).round(2).alias("temperature_c"),
            pl.col("valid_time").dt.year().alias("year"),
            pl.col("valid_time").dt.month().alias("month"),
        ])

        lf = self._map_to_regions(lf)
        df = lf.collect(engine="streaming")

        if df.is_empty():
            return {"total_rows": 0, "files_written": 0, "regions_processed": []}

        files = self._write_partitioned(df, output_dir)
        return {
            "total_rows": len(df),
            "files_written": files,
            "regions_processed": df["region_code"].unique().sort().to_list(),
        }

    def _map_to_regions(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Map each grid point to nearest French region via centroid distance."""
        # Create a mapping expression: compute distance to each centroid
        # and pick the closest region
        region_exprs = []
        for code, (lat, lon) in REGION_CENTROIDS.items():
            dist = (
                (pl.col("latitude") - lat).pow(2)
                + (pl.col("longitude") - lon).pow(2)
            ).sqrt().alias(f"dist_{code}")
            region_exprs.append(dist)

        lf = lf.with_columns(region_exprs)

        dist_cols = [f"dist_{code}" for code in REGION_CENTROIDS]
        # Find minimum distance and map to region code
        lf = lf.with_columns(
            pl.concat_list(dist_cols).list.arg_min().alias("nearest_idx")
        )

        region_codes = list(REGION_CENTROIDS.keys())
        lf = lf.with_columns(
            pl.col("nearest_idx")
            .map_elements(lambda idx: region_codes[idx], return_dtype=pl.Utf8)
            .alias("region_code")
        )

        # Drop distance columns
        lf = lf.drop(dist_cols + ["nearest_idx"])

        return lf

    def _write_partitioned(
        self, df: pl.DataFrame, output_dir: str | Path | None
    ) -> int:
        """Write partitioned Parquet files by region and month."""
        ts_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        files_written = 0

        groups = df.group_by(["region_code", "year", "month"])
        for (region, year, month), group_df in groups:
            filename = f"era5_{region}_{ts_str}.parquet"
            path = f"climate/era5/{year}/{month:02d}/{filename}"

            if output_dir:
                full_path = Path(output_dir) / path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                group_df.write_parquet(full_path)
                logger.info("Written: %s (%d rows)", full_path, len(group_df))
            elif self.bronze and self.bronze.local_mode:
                full_path = self.bronze.local_root / path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                group_df.write_parquet(full_path)
                logger.info("Written (local): %s (%d rows)", full_path, len(group_df))

            files_written += 1

        return files_written

    # ─── Checkpoint management ───────────────────────────────────────────

    @staticmethod
    def save_checkpoint(checkpoint_path: str | Path, last_processed: datetime) -> None:
        """Save ingestion checkpoint."""
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({
                "last_processed": last_processed.isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }),
            encoding="utf-8",
        )

    @staticmethod
    def load_checkpoint(checkpoint_path: str | Path) -> datetime | None:
        """Load last processed timestamp from checkpoint."""
        path = Path(checkpoint_path)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return datetime.fromisoformat(data["last_processed"])

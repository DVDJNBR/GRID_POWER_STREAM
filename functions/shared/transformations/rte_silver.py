"""
RTE Silver Transformation — Story 3.1, Task 1

Cleans raw RTE eCO2mix JSON from Bronze:
- Column rename → snake_case
- Type casting (pompage, stockage_batterie → Float64)
- Drop artifact columns (column_68, column_30)
- Deduplication on (code_insee_region, date_heure)
- Hive-partitioned Parquet output
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from functions.shared.transformations.data_quality import (
    RTE_QUALITY_RULES,
    apply_quality_rules,
)

logger = logging.getLogger(__name__)

# Columns to drop (null artifacts from API)
DROP_COLUMNS = ["column_68", "column_30"]

# MW columns that need Float64 casting (sometimes str in raw data)
MW_CAST_COLUMNS = [
    "pompage", "stockage_batterie", "destockage_batterie",
    "eolien", "solaire", "hydraulique", "nucleaire", "gaz",
    "charbon", "fioul", "bioenergies",
]

# Rename map: raw API names → clean snake_case
RENAME_MAP = {
    "consommation": "consommation_mw",
    "nucleaire": "nucleaire_mw",
    "eolien": "eolien_mw",
    "solaire": "solaire_mw",
    "hydraulique": "hydraulique_mw",
    "gaz": "gaz_mw",
    "charbon": "charbon_mw",
    "bioenergies": "bioenergies_mw",
    "fioul": "fioul_mw",
    "pompage": "pompage_mw",
    "stockage_batterie": "stockage_batterie_mw",
    "destockage_batterie": "destockage_batterie_mw",
}


def transform_rte_to_silver(
    bronze_path: str | Path,
    output_dir: str | Path,
) -> dict:
    """
    Transform RTE Bronze JSON → Silver Parquet.

    Args:
        bronze_path: Path to Bronze JSON file or directory.
        output_dir: Silver output directory.

    Returns:
        Summary dict.
    """
    bronze_path = Path(bronze_path)
    output_dir = Path(output_dir)

    # Load Bronze data
    if bronze_path.is_file():
        df = _load_json_file(bronze_path)
    elif bronze_path.is_dir():
        frames = []
        for f in sorted(bronze_path.rglob("*.json")):
            frames.append(_load_json_file(f))
        if not frames:
            logger.warning("No JSON files found in %s", bronze_path)
            return {"status": "empty", "rows": 0}
        df = pl.concat(frames)
    else:
        raise FileNotFoundError(f"Bronze path not found: {bronze_path}")

    if df.is_empty():
        return {"status": "empty", "rows": 0}

    # Drop artifact columns
    existing_drops = [c for c in DROP_COLUMNS if c in df.columns]
    if existing_drops:
        df = df.drop(existing_drops)

    # Cast MW columns to Float64
    for col in MW_CAST_COLUMNS:
        if col in df.columns:
            df = df.with_columns(
                pl.col(col).cast(pl.Utf8).str.strip_chars().cast(pl.Float64, strict=False)
            )

    # Rename columns → snake_case
    existing_renames = {k: v for k, v in RENAME_MAP.items() if k in df.columns}
    if existing_renames:
        df = df.rename(existing_renames)

    # Parse datetime
    if "date_heure" in df.columns:
        df = df.with_columns(
            pl.col("date_heure")
            .str.to_datetime(time_zone="UTC", strict=False)
        )

    # AC #3: Deduplicate on composite key
    dedup_cols = ["code_insee_region", "date_heure"]
    existing_dedup = [c for c in dedup_cols if c in df.columns]
    before_dedup = len(df)
    if len(existing_dedup) == 2:
        df = df.unique(subset=existing_dedup, keep="last")
    dupes_removed = before_dedup - len(df)

    # AC #4: Apply quality rules
    df, quality_metrics = apply_quality_rules(df, RTE_QUALITY_RULES, "rte_production")

    # AC #2: Write Hive-partitioned Parquet
    files_written = _write_hive_partitioned(df, output_dir, "silver/rte/production")

    summary = {
        "status": "success",
        "input_rows": before_dedup,
        "output_rows": len(df),
        "duplicates_removed": dupes_removed,
        "files_written": files_written,
        "quality": quality_metrics,
    }

    logger.info("RTE Silver: %d → %d rows, %d dupes removed, %d files",
                before_dedup, len(df), dupes_removed, files_written)
    return summary


def _load_json_file(path: Path) -> pl.DataFrame:
    """Load a Bronze JSON file into a DataFrame."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        records = [data]
    return pl.DataFrame(records)


def _write_hive_partitioned(
    df: pl.DataFrame, base_dir: Path, prefix: str
) -> int:
    """Write DataFrame as Hive-partitioned Parquet."""
    if "date_heure" not in df.columns:
        # No partitioning possible — write single file
        out = base_dir / prefix / "data.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(out)
        return 1

    # Add partition columns
    df = df.with_columns([
        pl.col("date_heure").dt.year().alias("year"),
        pl.col("date_heure").dt.month().alias("month"),
        pl.col("date_heure").dt.day().alias("day"),
    ])

    files = 0
    for (year, month, day), group in df.group_by(["year", "month", "day"]):
        part_path = (
            base_dir / prefix
            / f"year={year}" / f"month={month:02d}" / f"day={day:02d}"
            / "data.parquet"
        )
        part_path.parent.mkdir(parents=True, exist_ok=True)
        group.drop(["year", "month", "day"]).write_parquet(part_path)
        files += 1

    return files

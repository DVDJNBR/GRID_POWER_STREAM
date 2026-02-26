"""
Capacity Silver Transformation — Story 3.1, Task 2

Cleans Bronze CSV capacity data:
- Snake_case column normalization
- Handle missing values (FILL_ZERO for puissance)
- Output Hive-partitioned Parquet
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from functions.shared.transformations.data_quality import (
    CAPACITY_QUALITY_RULES,
    apply_quality_rules,
)

logger = logging.getLogger(__name__)


def transform_capacity_to_silver(
    bronze_path: str | Path,
    output_dir: str | Path,
) -> dict:
    """Transform capacity Bronze CSV → Silver Parquet."""
    bronze_path = Path(bronze_path)
    output_dir = Path(output_dir)

    if bronze_path.is_file():
        df = pl.read_csv(bronze_path, infer_schema_length=1000)
    elif bronze_path.is_dir():
        csvs = sorted(bronze_path.rglob("*.csv"))
        if not csvs:
            return {"status": "empty", "rows": 0}
        df = pl.concat([pl.read_csv(f, infer_schema_length=1000) for f in csvs])
    else:
        raise FileNotFoundError(f"Bronze path not found: {bronze_path}")

    # Normalize column names → snake_case
    df = df.rename({c: c.lower().replace(" ", "_").replace("-", "_") for c in df.columns})

    # Cast numeric columns
    if "puissance_installee_mw" in df.columns:
        df = df.with_columns(
            pl.col("puissance_installee_mw").cast(pl.Float64, strict=False)
        )

    # Apply quality rules
    df, quality = apply_quality_rules(df, CAPACITY_QUALITY_RULES, "capacity")

    # Deduplicate
    before = len(df)
    dedup_cols = [c for c in ["code_insee_region", "filiere"] if c in df.columns]
    if dedup_cols:
        df = df.unique(subset=dedup_cols, keep="last")

    # Write to Silver
    out_path = output_dir / "silver/reference/capacity/data.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_path)

    summary = {
        "status": "success",
        "input_rows": before,
        "output_rows": len(df),
        "files_written": 1,
        "quality": quality,
    }
    logger.info("Capacity Silver: %d → %d rows", before, len(df))
    return summary

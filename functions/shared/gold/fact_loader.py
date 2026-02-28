"""
Fact Table Loader — Story 3.2, Task 2

Reads Silver Parquet, resolves FK references to DIM tables,
calculates facteur_charge, and INSERTs into FACT_ENERGY_FLOW.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any

import polars as pl

from functions.shared.gold.dim_loader import DimLoader

logger = logging.getLogger(__name__)

# Energy sources that map from Silver column names
SOURCE_COLUMN_MAP = {
    "nucleaire_mw": "nucleaire",
    "eolien_mw": "eolien",
    "solaire_mw": "solaire",
    "hydraulique_mw": "hydraulique",
    "gaz_mw": "gaz",
    "charbon_mw": "charbon",
    "fioul_mw": "fioul",
    "bioenergies_mw": "bioenergies",
}


class FactLoader:
    """Load FACT_ENERGY_FLOW from Silver Parquet + DIM references."""

    def __init__(self, db_connection: Any, capacity_data: dict[str, float] | None = None):
        """
        Args:
            db_connection: Database connection.
            capacity_data: Dict mapping source_name → installed capacity (MW)
                          for facteur_charge calculation.
        """
        self.conn = db_connection
        self.dim = DimLoader(db_connection)
        self.capacity = capacity_data or {}

    def load_from_silver(self, silver_path: str | Path) -> dict:
        """
        Read Silver Parquet and load into FACT_ENERGY_FLOW.

        AC #1: Relational join between measurements and asset registry.
        AC #2: Updates FACT with most recent resolved metadata.
        AC #3: DIM tables upserted, FACT rows reference valid dimension keys.

        Args:
            silver_path: Path to Silver Parquet file or directory.

        Returns:
            Summary dict.
        """
        silver_path = Path(silver_path)

        # Read Silver data
        if silver_path.is_file():
            df = pl.read_parquet(silver_path)
        elif silver_path.is_dir():
            parquets = sorted(silver_path.rglob("*.parquet"))
            if not parquets:
                return {"status": "empty", "rows_loaded": 0}
            df = pl.concat([pl.read_parquet(f) for f in parquets])
        else:
            raise FileNotFoundError(f"Silver path not found: {silver_path}")

        if df.is_empty():
            return {"status": "empty", "rows_loaded": 0}

        # Ensure DIM_SOURCE is populated
        self.dim.upsert_sources()

        # Auto-populate DIM_REGION from Silver data
        if "code_insee_region" in df.columns and "libelle_region" in df.columns:
            regions = (
                df.select(["code_insee_region", "libelle_region"])
                .unique()
                .to_dicts()
            )
            self.dim.upsert_regions([
                {"code_insee": r["code_insee_region"], "nom_region": r["libelle_region"]}
                for r in regions
            ])

        # Auto-populate DIM_TIME from Silver timestamps
        if "date_heure" in df.columns:
            timestamps = df["date_heure"].cast(pl.Utf8).unique().to_list()
            self.dim.upsert_time(timestamps)

        # Pivot: unpivot wide format (one row per region/time) to long format
        # (one row per region/time/source)
        rows_loaded = 0
        cursor = self.conn.cursor()

        # Pre-compute timestamp strings in Polars Utf8 format to match what
        # DIM_TIME.horodatage stores (avoids Python datetime str() format mismatch).
        df = df.with_columns(
            pl.col("date_heure").cast(pl.Utf8).alias("_ts_str")
        )

        for row in df.iter_rows(named=True):
            region_code = str(row.get("code_insee_region", ""))
            timestamp = row.get("_ts_str", "")

            id_region = self.dim.get_region_id(region_code)
            id_date = self.dim.get_time_id(timestamp)

            if not id_region or not id_date:
                continue

            for col, source_name in SOURCE_COLUMN_MAP.items():
                if col not in row or row[col] is None:
                    continue

                valeur_mw = float(row[col])
                id_source = self.dim.get_source_id(source_name)
                if not id_source:
                    continue

                # AC: Calculate facteur_charge
                facteur_charge = None
                installed = self.capacity.get(source_name)
                if installed and installed > 0:
                    facteur_charge = round(valeur_mw / installed, 4)

                # Temperature from ERA5 if available
                temp = row.get("temperature_c") or row.get("temperature_moyenne")

                params = (id_date, id_region, id_source, valeur_mw, facteur_charge, temp)
                if self.dim._is_sqlite:
                    cursor.execute(
                        """INSERT INTO FACT_ENERGY_FLOW
                           (id_date, id_region, id_source, valeur_mw, facteur_charge, temperature_moyenne)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ON CONFLICT(id_date, id_region, id_source) DO UPDATE SET
                               valeur_mw = excluded.valeur_mw,
                               facteur_charge = excluded.facteur_charge,
                               temperature_moyenne = excluded.temperature_moyenne""",
                        params,
                    )
                else:
                    cursor.execute(
                        """MERGE FACT_ENERGY_FLOW AS t
                           USING (VALUES (?, ?, ?, ?, ?, ?))
                               AS s(id_date, id_region, id_source,
                                    valeur_mw, facteur_charge, temperature_moyenne)
                           ON t.id_date = s.id_date
                              AND t.id_region = s.id_region
                              AND t.id_source = s.id_source
                           WHEN MATCHED THEN UPDATE SET
                               valeur_mw = s.valeur_mw,
                               facteur_charge = s.facteur_charge,
                               temperature_moyenne = s.temperature_moyenne
                           WHEN NOT MATCHED THEN INSERT
                               (id_date, id_region, id_source,
                                valeur_mw, facteur_charge, temperature_moyenne)
                               VALUES (s.id_date, s.id_region, s.id_source,
                                       s.valeur_mw, s.facteur_charge, s.temperature_moyenne);""",
                        params,
                    )
                rows_loaded += 1

        self.conn.commit()

        summary = {
            "status": "success",
            "rows_loaded": rows_loaded,
            "sources": list(SOURCE_COLUMN_MAP.values()),
        }
        logger.info("Gold FACT loaded: %d rows", rows_loaded)
        return summary

    def get_fact_count(self) -> int:
        """Get total rows in FACT_ENERGY_FLOW."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM FACT_ENERGY_FLOW")
        return cursor.fetchone()[0]

    def get_fact_summary(self) -> dict:
        """Get summary stats from FACT_ENERGY_FLOW."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as total_rows,
                COUNT(DISTINCT id_region) as regions,
                COUNT(DISTINCT id_source) as sources,
                COUNT(DISTINCT id_date) as time_slots,
                ROUND(AVG(valeur_mw), 2) as avg_mw,
                SUM(CASE WHEN facteur_charge IS NOT NULL THEN 1 ELSE 0 END) as with_load_factor
            FROM FACT_ENERGY_FLOW
        """)
        row = cursor.fetchone()
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))

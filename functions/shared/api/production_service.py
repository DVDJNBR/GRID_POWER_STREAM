"""
Production Service — Story 4.1, Task 2

Queries Gold SQL FACT_ENERGY_FLOW + DIM joins.
Returns aggregated JSON: region/timestamp with pivoted source breakdown.

AC #1: Aggregated metrics from Gold SQL layer.
AC #2: Parameterized queries for <500ms (NFR-P2), index hint in docstring.
"""

import logging
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)

# SQL index recommendation (applied at DB provisioning, not here):
# CREATE INDEX IX_FACT_region_date ON FACT_ENERGY_FLOW (id_region, id_date);


def build_production_query(
    region_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[str, list]:
    """
    Build parameterized SQL query for production data.

    Returns (sql, params). Uses ? placeholders (pyodbc / sqlite3 compatible).
    AC #2: Parameterized → query plan caching, index usage.
    """
    where_clauses: list[str] = []
    params: list[Any] = []

    if region_code:
        where_clauses.append("r.code_insee = ?")
        params.append(region_code)

    if start_date:
        where_clauses.append("t.horodatage >= ?")
        params.append(start_date)

    if end_date:
        where_clauses.append("t.horodatage <= ?")
        params.append(end_date)

    if source_type:
        where_clauses.append("s.source_name = ?")
        params.append(source_type)

    where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT
            r.code_insee,
            r.nom_region,
            t.horodatage,
            s.source_name,
            f.valeur_mw,
            f.facteur_charge
        FROM FACT_ENERGY_FLOW f
        JOIN DIM_REGION r ON f.id_region = r.id_region
        JOIN DIM_TIME t ON f.id_date = t.id_date
        JOIN DIM_SOURCE s ON f.id_source = s.id_source
        {where}
        ORDER BY t.horodatage DESC, r.code_insee
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    return sql, params


def _aggregate_rows(rows: list, cols: list[str]) -> list[dict]:
    """
    Pivot flat SQL rows into region/timestamp records with source breakdown.

    AC #3: {region, timestamp, sources: {eolien, ...}, facteur_charge}
    """
    aggregated: dict[tuple, dict] = {}

    for row in rows:
        r = dict(zip(cols, row))
        key = (r["code_insee"], r["horodatage"])

        if key not in aggregated:
            aggregated[key] = {
                "code_insee": r["code_insee"],
                "region": r["nom_region"],
                "timestamp": r["horodatage"],
                "sources": {},
                "facteur_charge": r["facteur_charge"],
            }

        source = r["source_name"]
        aggregated[key]["sources"][source] = r["valeur_mw"]

    return list(aggregated.values())


def query_production(
    conn: Any,
    region_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    request_id: Optional[str] = None,
) -> dict:
    """
    Execute production query and return aggregated JSON response.

    AC #1: Returns aggregated metrics from Gold SQL FACT_ENERGY_FLOW + DIM joins.
    AC #2: Parameterized queries → <500ms with proper indexes.

    Args:
        conn: Any DB connection with cursor() support (pyodbc, sqlite3…).
        request_id: Trace ID; auto-generated if None.

    Returns:
        dict with request_id, total_records, limit, offset, data list.
    """
    request_id = request_id or str(uuid.uuid4())

    sql, params = build_production_query(
        region_code, start_date, end_date, source_type, limit, offset
    )

    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]

    data = _aggregate_rows(rows, cols)

    logger.debug(
        "production query: region=%s, start=%s, end=%s → %d records [req=%s]",
        region_code, start_date, end_date, len(data), request_id,
    )

    return {
        "request_id": request_id,
        "total_records": len(data),
        "limit": limit,
        "offset": offset,
        "data": data,
    }

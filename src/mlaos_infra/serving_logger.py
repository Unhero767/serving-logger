"""ServingLogger: Production-grade ML model serving logger for MLAOS infrastructure.

Rule #2: First, design and implement metrics.
Rule #10: Watch for silent failures.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class ServingLogger:
    """Logs ML model serving events to a PostgreSQL database.

    Attributes
    ----------
    model_name : str
        Name of the model being served.
    model_version : str
        Version identifier for the model.
    db_url : str
        PostgreSQL connection URL.
    """

    def __init__(self, model_name: str, model_version: str, db_url: str) -> None:
        self.model_name = model_name
        self.model_version = model_version
        self.db_url = db_url
        self._error_count: int = 0
        self._last_success_time: Optional[str] = None
        self._ensure_table()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _connect(self):
        """Return a new psycopg2 connection."""
        return psycopg2.connect(self.db_url)

    def _ensure_table(self) -> None:
        """Create the serving_logs table if it does not exist."""
        ddl = """
        CREATE TABLE IF NOT EXISTS serving_logs (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            model_name    TEXT        NOT NULL,
            model_version TEXT        NOT NULL,
            input_hash    TEXT,
            prediction    JSONB,
            actual_label  TEXT,
            latency_ms    FLOAT,
            served_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(ddl)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:  # Rule #10: surface silent failures
            logger.error("Table init failed: %s", e)
            self._error_count += 1

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(
        self,
        input_hash: str,
        prediction: Any,
        actual_label: Optional[str] = None,
        latency_ms: Optional[float] = None,
    ) -> Optional[str]:
        """Persist a single serving event.

        Parameters
        ----------
        input_hash : str
            Deterministic hash of the model input (for deduplication).
        prediction : Any
            Model output; will be serialised to JSONB.
        actual_label : str, optional
            Ground-truth label when available (for drift / accuracy tracking).
        latency_ms : float, optional
            End-to-end inference latency in milliseconds (Rule #2 metric).

        Returns
        -------
        str or None
            UUID of the inserted row, or None on failure.
        """
        row_id = str(uuid.uuid4())
        served_at = datetime.now(timezone.utc).isoformat()
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO serving_logs
                    (id, model_name, model_version, input_hash,
                     prediction, actual_label, latency_ms, served_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row_id,
                    self.model_name,
                    self.model_version,
                    input_hash,
                    json.dumps(prediction),
                    actual_label,
                    latency_ms,
                    served_at,
                ),
            )
            conn.commit()
            cur.close()
            conn.close()
            self._last_success_time = served_at
            return row_id
        except Exception as e:  # Rule #10: never silently swallow errors
            logger.error("Log insert failed: %s", e)
            self._error_count += 1
            return None

    def batch_log(self, records: List[Dict[str, Any]]) -> int:
        """Bulk-insert multiple serving events.

        Parameters
        ----------
        records : list of dict
            Each dict may contain keys: input_hash, prediction,
            actual_label, latency_ms.

        Returns
        -------
        int
            Number of rows successfully inserted.
        """
        if not records:
            return 0
        now = datetime.now(timezone.utc).isoformat()
        rows = [
            (
                str(uuid.uuid4()),
                self.model_name,
                self.model_version,
                r.get("input_hash"),
                json.dumps(r.get("prediction")),
                r.get("actual_label"),
                r.get("latency_ms"),
                now,
            )
            for r in records
        ]
        try:
            conn = self._connect()
            cur = conn.cursor()
            execute_values(
                cur,
                """
                INSERT INTO serving_logs
                    (id, model_name, model_version, input_hash,
                     prediction, actual_label, latency_ms, served_at)
                VALUES %s
                """,
                rows,
            )
            conn.commit()
            cur.close()
            conn.close()
            self._last_success_time = now
            return len(rows)
        except Exception as e:
            logger.error("Batch insert failed: %s", e)
            self._error_count += 1
            return 0

    def recent_predictions(self) -> List[Any]:
        """Return all predictions logged in the last 24 hours.

        Rule #2: Fi
        Rule #10: Watch for silent failures.

        Returns
        -------
        list
            Rows containing (prediction, actual_label, served_at).
        """
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT prediction, actual_label, served_at
                FROM serving_logs
                WHERE model_version = %s
                  AND served_at > NOW() - INTERVAL '24 hours'
                ORDER BY served_at DESC
                """,
                (self.model_version,),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            logger.error("Query failed (Rule #10): %s", e)
            return []

    def get_health_status(self) -> Dict[str, Any]:
        """Get logger health status for monitoring.

        Glossary:
        - metric: A number that you care about (Rule #2: Design and implement metrics)
        - silent failure: Problem occurring more for ML systems
          (stale tables, gradual decay, incomplete logging)

        Rule #10: Watch for silent failures
        Rule #2: First, design and implement metrics

        Returns:
        --------
        Dict containing:
            error_count       : int  - cumulative errors since last success (Rule #2 metric)
            last_success_time : str  - UTC timestamp of last successful log write
            is_healthy        : bool - True if error_count < 100
        """
        return {
            'error_count': self._error_count,        # Rule #2: Metric to track
            'last_success_time': self._last_success_time,
            'is_healthy': self._error_count < 100    # Threshold for alert (Rule #10)
        }

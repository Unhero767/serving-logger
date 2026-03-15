"""
Serving Logger (Rule #29: Log features at serving time)
Author: Kenneth Dallmier | kennydallmier@gmail.com
Repository: serving-logger

CRITICAL: Call log_inference() AFTER feature extraction, BEFORE returning prediction.
This captures the EXACT features used, preventing training-serving skew (Rule #37).
"""

import logging
from typing import Any, Dict, Optional

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

logger = logging.getLogger(__name__)


class ServingLogger:
    """
    Logs exact feature values at inference time (Rule #29).

    Design Principles:
    - NEVER raises exceptions (Rule #10: silent failure)
    - Logs AFTER feature extraction, BEFORE prediction return
    - Uses same feature values as the model (no re-computation)
    - Enables weekly skew audits (Rule #37)
    """

    def __init__(self, db_conn_string: str, model_version: str,
                 environment: str = 'production'):
        """
        Initialize ServingLogger.

        Args:
            db_conn_string: PostgreSQL connection string
            model_version: Current model version (e.g., 'AURELIA-v2.3')
            environment: Deployment environment
        """
        self.db_conn_string = db_conn_string
        self.model_version = model_version
        self.environment = environment
        self._conn: Optional[Any] = None

    def _get_connection(self) -> Optional[Any]:
        """Lazily establish DB connection. Returns None on failure."""
        if psycopg2 is None:
            return None
        try:
            if self._conn is None or self._conn.closed:
                self._conn = psycopg2.connect(self.db_conn_string)
            return self._conn
        except Exception as e:
            logger.warning(f"ServingLogger: DB connection failed: {e}")
            return None

    def log_inference(
        self,
        request_id: str,
        memory_id: str,
        features: Dict[str, Any]
    ) -> bool:
        """
        Log the exact features used for a prediction request (Rule #29).

        Args:
            request_id: Unique ID for this inference (UUID recommended)
            memory_id: The memory node ID being processed
            features: EXACT features used in prediction (from FeatureExtractor)

        Returns:
            True if logged successfully, False on any failure (never raises)

        Example:
            features = extractor.extract_features(raw_data)
            prediction = model.predict(features)
            logger.log_inference(request_id, memory_id, features)  # <- here
            return prediction
        """
        conn = self._get_connection()
        if conn is None:
            return False

        try:
            with conn.cursor() as cur:
                rows = [
                    (
                        request_id,
                        memory_id,
                        feature_name,
                        psycopg2.extras.Json({'value': feature_value}),
                        self.model_version,
                        self.environment
                    )
                    for feature_name, feature_value in features.items()
                ]
                psycopg2.extras.execute_values(
                    cur,
                    """INSERT INTO serving_logs
                       (request_id, memory_id, feature_name,
                        feature_value, model_version, environment)
                       VALUES %s""",
                    rows
                )
            conn.commit()
            return True
        except Exception as e:
            logger.warning(f"ServingLogger: log_inference failed: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            return False

    def close(self) -> None:
        """Close the database connection gracefully."""
        if self._conn and not self._conn.closed:
            try:
                self._conn.close()
            except Exception:
                pass

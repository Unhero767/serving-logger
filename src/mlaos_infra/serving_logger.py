"""ServingLogger: Rule #29 - Log features at serving time."""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import psycopg2
except ImportError:
    psycopg2 = None

logger = logging.getLogger(__name__)
VALID_ENVIRONMENTS = ("production", "staging", "test", "development")


class ServingLogger:
    """Logs inference features to DB for Rule #29 and #37 compliance.

    Rule #29: Log features at serving time.
    Rule #10: Fail silently - never crash inference on DB failure.
    """

    def __init__(self, db_conn_string: str, model_version: str, environment: str = "production"):
        if environment not in VALID_ENVIRONMENTS:
            raise ValueError(f"Invalid environment '{environment}'. Must be one of: {VALID_ENVIRONMENTS}")
        self.db_conn_string = db_conn_string
        self.model_version = model_version
        self.environment = environment

    def log_inference(self, request_id: str, memory_id: str, features_dict: Dict[str, Any], latency_ms: Optional[float] = None) -> Optional[str]:
        """Log feature values at inference time. Rule #29 / Rule #10 (fail silently)."""
        log_id = str(uuid.uuid4())
        try:
            if psycopg2 is None:
                return None
            conn = psycopg2.connect(self.db_conn_string)
            with conn.cursor() as cur:
                for feature_name, feature_value in features_dict.items():
                    cur.execute(
                        "INSERT INTO serving_logs (log_id, request_id, memory_id, model_version, environment, feature_name, feature_value, latency_ms, logged_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (log_id, request_id, memory_id, self.model_version, self.environment, feature_name, json.dumps({"value": feature_value}), latency_ms, datetime.utcnow())
                    )
            conn.commit()
            conn.close()
            return log_id
        except Exception as e:
            logger.warning("ServingLogger DB write failed silently: %s", e)
            return None

    def log_feedback(self, request_id: str, actual_label: Any, feedback_source: str = "system") -> None:
        """Log ground-truth feedback for a previous inference request."""
        try:
            if psycopg2 is None:
                return
            conn = psycopg2.connect(self.db_conn_string)
            with conn.cursor() as cur:
                cur.execute("UPDATE serving_logs SET actual_label = %s, feedback_source = %s WHERE request_id = %s", (json.dumps({"value": actual_label}), feedback_source, request_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning("ServingLogger feedback write failed silently: %s", e)

    def get_recent_predictions(self, hours: int = 24) -> list:
        """Retrieve recent prediction logs for skew analysis."""
        try:
            if psycopg2 is None:
                return []
            conn = psycopg2.connect(self.db_conn_string)
            cur = conn.cursor()
            cur.execute("SELECT request_id, model_version, feature_name, feature_value, actual_label, latency_ms, logged_at FROM serving_logs WHERE model_version = %s AND environment = %s AND logged_at > NOW() - INTERVAL '24 hours' ORDER BY logged_at DESC", (self.model_version, self.environment))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            logger.warning("ServingLogger query failed: %s", e)
            return []

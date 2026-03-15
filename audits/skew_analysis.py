"""Skew Analysis Module - MLAOS Audits

Rule #37: Measure Training/Serving Skew.
Rule #10: Watch for silent failures.

Performs statistical comparison of feature distributions between
training data and recent serving logs to detect training-serving skew.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats
import psycopg2

logger = logging.getLogger(__name__)

# Rule #37: KS statistic threshold for skew alert
SKEW_ALERT_THRESHOLD = 0.1
# Rule #37: p-value threshold for significance
PVALUE_THRESHOLD = 0.05


class SkewAnalysis:
    """Computes Kolmogorov-Smirnov test between training and serving distributions.

    Rule #37: Measure training/serving skew weekly.
    Rule #10: Never silently swallow analysis failures.
    """

    def __init__(self, db_url: str) -> None:
        self.db_url = db_url
        self._error_count: int = 0

    def _connect(self):
        return psycopg2.connect(self.db_url)

    def fetch_serving_features(
        self,
        feature_name: str,
        hours_back: int = 168,  # 7 days
    ) -> List[float]:
        """Fetch recent serving-time values for a feature (Rule #37)."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT (prediction->>%s)::float
                FROM serving_logs
                WHERE served_at > %s
                  AND prediction ? %s
                """,
                (feature_name, cutoff, feature_name),
            )
            values = [row[0] for row in cur.fetchall() if row[0] is not None]
            cur.close()
            conn.close()
            return values
        except Exception as e:
            logger.error("fetch_serving_features failed (Rule #10): %s", e)
            self._error_count += 1
            return []

    def run_ks_test(
        self,
        training_values: List[float],
        serving_values: List[float],
    ) -> Tuple[float, float]:
        """Run KS test between training and serving distributions.

        Rule #37: Target KS stat < 0.1.

        Returns
        -------
        (ks_statistic, p_value)
        """
        if len(training_values) < 10 or len(serving_values) < 10:
            logger.warning("Insufficient data for KS test (min 10 samples)")
            return 0.0, 1.0
        ks_stat, p_value = stats.ks_2samp(training_values, serving_values)
        return float(ks_stat), float(p_value)

    def analyze_feature(
        self,
        feature_name: str,
        training_values: List[float],
    ) -> Dict:
        """Full skew analysis for a single feature.

        Rule #37: Measure training/serving skew.
        Rule #10: Surface all failures in health report.
        """
        serving_values = self.fetch_serving_features(feature_name)
        ks_stat, p_value = self.run_ks_test(training_values, serving_values)
        skew_detected = ks_stat > SKEW_ALERT_THRESHOLD and p_value < PVALUE_THRESHOLD

        if skew_detected:
            logger.warning(
                "SKEW ALERT (Rule #37): feature=%s ks_stat=%.4f p_value=%.4f",
                feature_name, ks_stat, p_value,
            )

        return {
            "feature_name": feature_name,
            "ks_statistic": ks_stat,
            "p_value": p_value,
            "skew_detected": skew_detected,
            "serving_sample_size": len(serving_values),
            "training_sample_size": len(training_values),
            "threshold": SKEW_ALERT_THRESHOLD,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def run_full_audit(
        self,
        training_data: Dict[str, List[float]],
    ) -> List[Dict]:
        """Run skew analysis across all features in training_data.

        Rule #37: Weekly audit of all active features.

        Parameters
        ----------
        training_data : dict
            Map of feature_name -> list of training values.
        """
        results = []
        for feature_name, training_values in training_data.items():
            result = self.analyze_feature(feature_name, training_values)
            results.append(result)
            logger.info(
                "Skew audit: feature=%s ks=%.4f skew_detected=%s",
                feature_name, result["ks_statistic"], result["skew_detected"],
            )
        return results

    def get_health_status(self) -> Dict:
        """Return health status of the skew analyzer (Rule #10)."""
        return {
            "error_count": self._error_count,
            "is_healthy": self._error_count < 10,
        }

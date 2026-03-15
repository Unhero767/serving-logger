"""
Skew Auditor (Rule #37: Measure training/serving skew)
Author: Kenneth Dallmier | kennydallmier@gmail.com
Repository: serving-logger

Run weekly (or on every deployment) to detect distribution drift
between training and serving feature values.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SkewReport:
    """Report for a single feature's skew measurement."""
    feature_name: str
    training_mean: float
    serving_mean: float
    skew_pct: float
    alert: bool
    threshold: float = 10.0
    sample_count: int = 0

    @property
    def status(self) -> str:
        if self.sample_count == 0:
            return 'NO_DATA'
        return 'ALERT' if self.alert else 'OK'

    def __str__(self) -> str:
        return (
            f"{self.feature_name}: "
            f"train={self.training_mean:.4f} "
            f"serve={self.serving_mean:.4f} "
            f"skew={self.skew_pct:.1f}% "
            f"[{self.status}]"
        )


class SkewAuditor:
    """
    Detects training-serving distribution skew (Rule #37).

    Weekly audit compares training statistics against recent
    serving logs to catch drift before it degrades model quality.

    Threshold guidance:
    - <5%: Healthy, no action needed
    - 5-10%: Monitor closely
    - >10%: ALERT - investigate immediately
    - >25%: CRITICAL - consider rolling back model version
    """

    CRITICAL_THRESHOLD_PCT = 25.0

    def __init__(
        self,
        db_conn_string: str,
        model_version: str,
        skew_threshold_pct: float = 10.0,
        lookback_days: int = 7
    ):
        self.db_conn_string = db_conn_string
        self.model_version = model_version
        self.skew_threshold_pct = skew_threshold_pct
        self.lookback_days = lookback_days

    def run_audit(self, training_stats: Dict[str, Dict]) -> List[SkewReport]:
        """
        Run skew audit for all features in training_stats.

        Args:
            training_stats: {feature_name: {'mean': float, 'std': float}}
                           (obtained from your training pipeline)

        Returns:
            List of SkewReport, one per feature
        """
        serving_stats = self._get_serving_stats()
        reports = []

        for feature_name, train_stat in training_stats.items():
            serving_stat = serving_stats.get(feature_name)

            if serving_stat is None:
                logger.warning(
                    f"Rule #37: No serving data for '{feature_name}'. "
                    f"Feature may not be logged yet or has no recent traffic."
                )
                reports.append(SkewReport(
                    feature_name=feature_name,
                    training_mean=train_stat.get('mean', 0),
                    serving_mean=0.0,
                    skew_pct=0.0,
                    alert=False,
                    threshold=self.skew_threshold_pct,
                    sample_count=0
                ))
                continue

            train_mean = float(train_stat.get('mean', 0))
            serving_mean = float(serving_stat.get('mean', 0))
            sample_count = int(serving_stat.get('count', 0))

            skew_pct = 0.0
            if train_mean != 0:
                skew_pct = abs(serving_mean - train_mean) / abs(train_mean) * 100

            is_alert = skew_pct > self.skew_threshold_pct
            is_critical = skew_pct > self.CRITICAL_THRESHOLD_PCT

            if is_critical:
                logger.error(
                    f"CRITICAL SKEW: {feature_name} "
                    f"train={train_mean:.4f} serve={serving_mean:.4f} "
                    f"skew={skew_pct:.1f}% (threshold={self.skew_threshold_pct}%)"
                )
            elif is_alert:
                logger.warning(
                    f"SKEW ALERT: {feature_name} "
                    f"train={train_mean:.4f} serve={serving_mean:.4f} "
                    f"skew={skew_pct:.1f}%"
                )

            reports.append(SkewReport(
                feature_name=feature_name,
                training_mean=train_mean,
                serving_mean=serving_mean,
                skew_pct=skew_pct,
                alert=is_alert,
                threshold=self.skew_threshold_pct,
                sample_count=sample_count
            ))

        return reports

    def _get_serving_stats(self) -> Dict[str, Dict]:
        """Query recent serving_logs for feature statistics."""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_conn_string)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        feature_name,
                        AVG((feature_value->>'value')::FLOAT) as mean,
                        STDDEV((feature_value->>'value')::FLOAT) as std,
                        COUNT(*) as count
                    FROM serving_logs
                    WHERE model_version = %s
                      AND environment = 'production'
                      AND logged_at > NOW() - INTERVAL '%s days'
                      AND jsonb_typeof(feature_value->'value') = 'number'
                    GROUP BY feature_name
                """, (self.model_version, self.lookback_days))
                rows = cur.fetchall()
            conn.close()
            return {
                row[0]: {'mean': row[1], 'std': row[2], 'count': row[3]}
                for row in rows
                if row[1] is not None
            }
        except Exception as e:
            logger.error(f"SkewAuditor: Failed to query serving stats: {e}")
            return {}

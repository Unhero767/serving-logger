"""SkewAuditor: Rule #37 - Measure training/serving skew."""

import logging
from typing import Dict, Optional

try:
    import numpy as np
    from scipy import stats
    import pandas as pd
except ImportError:
    np = None
    stats = None
    pd = None

logger = logging.getLogger(__name__)


class SkewAuditor:
    """Measures training-serving skew using KS test (Rule #37).

    Args:
        model_version: Model version being audited.
        lookback_days: Days of serving data to compare against training.
        alert_threshold: KS test p-value threshold for skew alert.
    """

    def __init__(self, model_version: str, lookback_days: int = 7, alert_threshold: float = 0.05):
        self.model_version = model_version
        self.lookback_days = lookback_days
        self.alert_threshold = alert_threshold

    def measure_skew(self, training_data, serving_data, threshold: float = 0.05) -> Dict:
        """Measure training-serving skew between two datasets using KS test.

        Args:
            training_data: Training set feature distributions (pd.DataFrame or dict).
            serving_data: Serving log feature distributions (pd.DataFrame or dict).
            threshold: KS test p-value threshold for alert.

        Returns:
            Dict with ks_statistic, p_value, skew_detected per feature.
        """
        if stats is None:
            logger.warning("scipy not available; cannot measure skew.")
            return {}

        results = {}
        if hasattr(training_data, 'columns'):
            features = training_data.columns
        else:
            features = training_data.keys()

        for feature in features:
            train_vals = training_data[feature] if hasattr(training_data, '__getitem__') else []
            serve_vals = serving_data[feature] if feature in serving_data else []

            if len(train_vals) < 2 or len(serve_vals) < 2:
                continue

            ks_stat, p_value = stats.ks_2samp(train_vals, serve_vals)
            results[feature] = {
                "ks_statistic": float(ks_stat),
                "p_value": float(p_value),
                "skew_detected": p_value < threshold
            }

        return results

    def run_audit(self, training_data, serving_data) -> Dict:
        """Run a full skew audit and return summary report.

        Returns:
            Audit report with per-feature skew results and summary.
        """
        skew_results = self.measure_skew(training_data, serving_data, self.alert_threshold)
        skewed_features = [f for f, r in skew_results.items() if r.get("skew_detected")]
        return {
            "model_version": self.model_version,
            "lookback_days": self.lookback_days,
            "features_audited": len(skew_results),
            "features_skewed": len(skewed_features),
            "skewed_features": skewed_features,
            "alert": len(skewed_features) > 0,
            "results": skew_results
        }

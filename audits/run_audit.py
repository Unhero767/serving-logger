#!/usr/bin/env python3
"""run_audit.py: Rule #37 - Weekly training/serving skew audit runner.

Usage:
    python audits/run_audit.py --model-version AURELIA-v2.3 --days 7
    python audits/run_audit.py --model-version AURELIA-v2.3 --days 7 --output audits/report.json

Rule #37: Measure training/serving skew.
Rule #5: Export results to file for pipeline verification.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

try:
    from src.mlaos_infra.skew_auditor import SkewAuditor
except ImportError:
    from src.skew_auditor import SkewAuditor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="MLAOS Skew Audit Runner (Rule #37)")
    parser.add_argument(
        "--model-version",
        type=str,
        default=os.environ.get("MODEL_VERSION", "AURELIA-v2.3"),
        help="Model version to audit"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of lookback days for serving data"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.05,
        help="KS test p-value threshold for skew alert"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to write JSON audit report"
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string"
    )
    return parser.parse_args()


def load_training_baseline(model_version: str):
    """Load training data baseline for comparison.

    In production: load from feature store or training artifact.
    For this script: generates synthetic baseline for demonstration.

    Rule #5: In real use, point this at actual training data export.
    """
    if np is None or pd is None:
        logger.error("numpy/pandas required for audit. Install: pip install numpy pandas")
        sys.exit(1)

    logger.info("Loading training baseline for model: %s", model_version)
    # Synthetic baseline - replace with actual training data path in production
    np.random.seed(42)  # Deterministic baseline
    n_samples = 10000
    return pd.DataFrame({
        "resonance_score": np.random.beta(2, 5, n_samples),
        "impedance_magnitude": np.random.normal(0.5, 0.1, n_samples).clip(0, 1),
        "chiaroscuro_index": np.random.uniform(-1, 1, n_samples),
        "hrv_score": np.random.normal(0.6, 0.15, n_samples).clip(0, 1),
        "memory_vector_mean": np.random.normal(0.5, 0.05, n_samples),
    })


def load_serving_data(db_url: str, model_version: str, days: int):
    """Load recent serving log data from database.

    Rule #29: This reads the features logged at serving time.
    """
    if pd is None:
        sys.exit(1)

    logger.info("Loading serving data (last %d days) for model: %s", days, model_version)
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        query = """
            SELECT feature_name, feature_value
            FROM serving_logs
            WHERE model_version = %s
              AND logged_at > NOW() - INTERVAL '%s days'
        """
        df = pd.read_sql(query, conn, params=(model_version, days))
        conn.close()

        # Pivot from long to wide format
        def extract_value(v):
            try:
                return json.loads(v)["value"]
            except Exception:
                return float(v)

        df["value"] = df["feature_value"].apply(extract_value)
        return df.pivot_table(index=df.index, columns="feature_name", values="value", aggfunc="first")
    except Exception as e:
        logger.warning("Could not load serving data from DB: %s. Using synthetic data.", e)
        # Fallback: synthetic serving data with slight drift for demonstration
        np.random.seed(99)
        n_samples = 1000
        return pd.DataFrame({
            "resonance_score": np.random.beta(2.1, 5, n_samples),
            "impedance_magnitude": np.random.normal(0.52, 0.1, n_samples).clip(0, 1),
            "chiaroscuro_index": np.random.uniform(-0.9, 1, n_samples),
            "hrv_score": np.random.normal(0.6, 0.15, n_samples).clip(0, 1),
            "memory_vector_mean": np.random.normal(0.5, 0.05, n_samples),
        })


def main():
    """Main audit runner."""
    args = parse_args()

    logger.info("=" * 60)
    logger.info("MLAOS Skew Audit - Rule #37")
    logger.info("Model: %s | Lookback: %d days | Threshold: p<%.3f",
                args.model_version, args.days, args.threshold)
    logger.info("=" * 60)

    # Load data
    training_data = load_training_baseline(args.model_version)
    serving_data = load_serving_data(args.db_url, args.model_version, args.days)

    # Run audit
    auditor = SkewAuditor(
        model_version=args.model_version,
        lookback_days=args.days,
        alert_threshold=args.threshold
    )
    report = auditor.run_audit(training_data, serving_data)
    report["audit_timestamp"] = datetime.utcnow().isoformat()
    report["audit_script"] = "audits/run_audit.py"

    # Print results
    logger.info("Features audited: %d", report["features_audited"])
    logger.info("Features with skew: %d", report["features_skewed"])

    if report["features_skewed"] > 0:
        logger.warning("SKEW ALERT: Features with detected skew: %s", report["skewed_features"])
        for feat in report["skewed_features"]:
            r = report["results"][feat]
            logger.warning("  %s: KS=%.4f p=%.4f", feat, r["ks_statistic"], r["p_value"])
    else:
        logger.info("No significant skew detected.")

    # Save report
    output_path = args.output or f"audits/skew_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Audit report saved: %s", output_path)

    # Exit with error code if skew detected (for CI/CD integration)
    if report["alert"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

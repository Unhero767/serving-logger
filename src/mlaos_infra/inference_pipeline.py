"""inference_pipeline.py

End-to-end MLAOS inference pipeline with Rules #29 and #37 compliance.

This module is the canonical production usage example showing how
ServingLogger (Rule #29) and SkewAuditor (Rule #37) integrate into
a live inference handler.

Google ML Glossary Alignment:
    feature        : An input variable to a machine learning model
    feature vector : The array of feature values comprising one example
    inference      : Making predictions by applying trained model to unlabeled examples
    instance       : Thing about which you want to make a prediction
    label          : The "answer" portion of an example (resonance_score)
    example        : One row of features (one MLAOS memory node session)
    training set   : Subset used to train the model (baseline for skew comparison)
    training-serving skew : Difference in feature distributions between train and serve

Rules Compliance:
    Rule #29 : Log features at serving time via logger.log_inference()
    Rule #37 : Measure training-serving skew via SkewAuditor.run_audit()
    Rule #32 : Re-use FeatureExtractor between training and serving
    Rule #10 : Logger never crashes inference on DB failure
"""

import logging
import os
import uuid
from typing import Any, Dict, Optional

from .serving_logger import ServingLogger
from .skew_auditor import SkewAuditor

try:
    from src.mlaos_features.feature_extractor import FeatureExtractor
except ImportError:
    FeatureExtractor = None

logger = logging.getLogger(__name__)


class InferencePipeline:
    """MLAOS inference pipeline with Rule #29 and #37 compliance.

    Wraps feature extraction, model prediction, and serving log in
    one atomic call. The feature vector is logged EXACTLY as used
    in prediction - not before, not after any transformation.

    Args:
        model: Trained MLAOS model with a .predict(features) method.
        feature_extractor: FeatureExtractor instance (Rule #32: shared with training).
        serving_logger: ServingLogger instance (Rule #29: log features at serve time).
        skew_auditor: SkewAuditor instance (Rule #37: measure skew).
    """

    def __init__(
        self,
        model: Any,
        feature_extractor,
        serving_logger: ServingLogger,
        skew_auditor: Optional[SkewAuditor] = None
    ):
        self.model = model
        self.feature_extractor = feature_extractor
        self.serving_logger = serving_logger
        self.skew_auditor = skew_auditor

    def predict(
        self,
        memory_id: str,
        raw_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run one inference request with full Rule #29 + #37 compliance.

        Glossary:
            instance       = memory_id (the thing being predicted)
            feature vector = features (extracted from raw_data)
            example        = one complete {features, label} row
            inference      = this method call
            label          = prediction['resonance_score']

        Args:
            memory_id:   Glossary "instance" - the MLAOS memory node being predicted.
            raw_data:    Raw sensor data dict from EIS/biometric pipeline.
            request_id:  Optional UUID; auto-generated if not provided.

        Returns:
            Dict with 'prediction', 'request_id', 'log_id', 'features'.
        """
        # Generate request_id if not provided
        # Glossary: "inference" - each prediction is one inference request
        if request_id is None:
            request_id = str(uuid.uuid4())

        # Step 1: Extract feature vector (Rule #32: same code as training)
        # Glossary: "feature vector" - array of feature values for one example
        # Glossary: "feature engineering" - FeatureExtractor transforms raw_data
        features: Dict[str, Any] = self.feature_extractor.extract_features(raw_data)

        # Step 2: Run model prediction
        # Glossary: "inference" - applying trained model to unlabeled example
        # Glossary: "label" - the prediction output (resonance_score)
        try:
            prediction = self.model.predict(features)
        except Exception as e:
            logger.error("Model prediction failed for request_id=%s: %s", request_id, e)
            raise

        # Step 3: Rule #29 - Log features at serving time
        # CRITICAL: Log the exact features_dict used in prediction.
        # Do NOT log raw_data. Do NOT log transformed/post-processed features.
        # Glossary: "feature vector" = features (the exact dict passed to model)
        log_id = self.serving_logger.log_inference(
            request_id=request_id,
            memory_id=memory_id,
            features_dict=features  # Glossary: feature vector
        )

        return {
            "request_id": request_id,
            "memory_id": memory_id,
            "prediction": prediction,
            "log_id": log_id,
            "features": features  # Glossary: feature vector returned for audit
        }

    def predict_batch(
        self,
        instances: list,
        raw_data_list: list
    ) -> list:
        """Run a batch of inference requests.

        Glossary:
            instances = list of memory_ids ("things about which you want predictions")

        Args:
            instances:      List of memory_ids (Glossary: instances).
            raw_data_list:  Corresponding list of raw sensor data dicts.

        Returns:
            List of prediction result dicts.
        """
        if len(instances) != len(raw_data_list):
            raise ValueError("instances and raw_data_list must have the same length.")

        results = []
        for memory_id, raw_data in zip(instances, raw_data_list):
            result = self.predict(memory_id=memory_id, raw_data=raw_data)
            results.append(result)
        return results

    def run_skew_audit(
        self,
        training_data,
        serving_data,
        threshold: float = 0.05
    ) -> Dict:
        """Rule #37: Measure training-serving skew.

        Compare the distribution of the training set feature values against
        the distribution of features logged at serving time.

        Glossary:
            training set          : Subset of dataset used to train model
            training-serving skew : Difference in feature distributions
            generalization        : Model ability to perform on new data
            concept drift         : Shift in feature-label relationship over time

        Args:
            training_data: pd.DataFrame of training set feature distributions.
                           Glossary: "training set" - subset used to train model.
            serving_data:  pd.DataFrame of serving log feature distributions.
                           Glossary: extracted from serving_logs table (Rule #29).
            threshold:     KS test p-value threshold. Alert if p < threshold.
                           Default: 0.05 (industry standard for statistical significance).

        Returns:
            Audit report dict with per-feature ks_statistic, p_value, skew_detected.
            'alert' key is True if any feature exceeds threshold.
        """
        if self.skew_auditor is None:
            logger.warning(
                "No SkewAuditor configured. Skipping Rule #37 skew measurement. "
                "Pass skew_auditor= to InferencePipeline to enable."
            )
            return {"alert": False, "skew_auditor_configured": False}

        # Rule #37: measure training-serving skew
        # Glossary: "training-serving skew" = difference between train/serve distributions
        report = self.skew_auditor.run_audit(
            training_data=training_data,
            serving_data=serving_data
        )

        if report.get("alert"):
            logger.warning(
                "[Rule #37] Training-serving skew detected in %d feature(s): %s. "
                "Consider retraining or investigating data pipeline.",
                report["features_skewed"],
                report["skewed_features"]
            )
        else:
            logger.info(
                "[Rule #37] No training-serving skew detected across %d features.",
                report.get("features_audited", 0)
            )

        return report


def build_pipeline(
    model: Any,
    db_url: Optional[str] = None,
    model_version: Optional[str] = None,
    environment: str = "production",
    feature_config_path: str = "src/mlaos_features/config.yaml",
    enable_skew_audit: bool = True
) -> InferencePipeline:
    """Factory function: build a fully configured InferencePipeline.

    Reads DATABASE_URL and MODEL_VERSION from environment if not provided.
    Suitable for production MLAOS deployment.

    Args:
        model:               Trained model with .predict(features) method.
        db_url:              PostgreSQL connection string (default: DATABASE_URL env var).
        model_version:       Model version string (default: MODEL_VERSION env var).
        environment:         Deployment environment ('production', 'staging', 'test').
        feature_config_path: Path to feature extractor YAML config (Rule #32).
        enable_skew_audit:   Whether to attach SkewAuditor (Rule #37).

    Returns:
        Fully configured InferencePipeline instance.

    Example:
        pipeline = build_pipeline(
            model=aurelia_model,
            model_version='AURELIA-v2.3'
        )

        result = pipeline.predict(
            memory_id='mem-node-001',
            raw_data={
                'resonance_raw': 0.75,
                'light_intensity': 0.8,
                'dark_intensity': 0.2,
                'hrv_score': 0.65,
                'memory_vector': [0.5, 0.5, 0.5]
            }
        )

        # Rule #29: features were logged to serving_logs automatically
        # Rule #37: run weekly skew audit:
        # report = pipeline.run_skew_audit(training_df, serving_df)
    """
    db_url = db_url or os.environ.get("DATABASE_URL", "")
    model_version = model_version or os.environ.get("MODEL_VERSION", "MLAOS-v1.0")

    # Rule #32: build FeatureExtractor - same instance config for train and serve
    if FeatureExtractor is not None:
        feature_extractor = FeatureExtractor(config_path=feature_config_path)
    else:
        raise ImportError(
            "FeatureExtractor not available. Ensure src/mlaos_features/ is on PYTHONPATH."
        )

    # Rule #29: build ServingLogger
    # Rule #10: ServingLogger fails silently - never crashes inference
    serving_logger = ServingLogger(
        db_conn_string=db_url,
        model_version=model_version,
        environment=environment
    )

    # Rule #37: build SkewAuditor (optional, for weekly audit runs)
    skew_auditor = None
    if enable_skew_audit:
        skew_auditor = SkewAuditor(
            model_version=model_version,
            lookback_days=7,
            alert_threshold=0.05
        )

    return InferencePipeline(
        model=model,
        feature_extractor=feature_extractor,
        serving_logger=serving_logger,
        skew_auditor=skew_auditor
    )

"""tests/test_inference_pipeline.py

Tests for InferencePipeline - Rules #29 and #37 compliance.

Glossary Alignment:
    feature vector : The array of feature values comprising one example
    inference      : Making predictions by applying trained model to unlabeled examples
    instance       : Thing about which you want to make a prediction (memory_id)
    training-serving skew : Difference in feature distributions between train and serve
"""

import unittest
import uuid
from unittest.mock import MagicMock, patch

from src.mlaos_infra.inference_pipeline import InferencePipeline
from src.mlaos_infra.serving_logger import ServingLogger
from src.mlaos_infra.skew_auditor import SkewAuditor
from src.mlaos_features.feature_extractor import FeatureExtractor


class MockModel:
    """Minimal mock model for testing."""

    def predict(self, features: dict) -> dict:
        """Return deterministic prediction from feature vector."""
        return {
            "resonance_score": features.get("resonance_score", 0.5),
            "label": "resonant" if features.get("resonance_score", 0) > 0.5 else "baseline"
        }


RAW_DATA = {
    "resonance_raw": 0.75,
    "light_intensity": 0.8,
    "dark_intensity": 0.2,
    "hrv_score": 0.65,
    "memory_vector": [0.5, 0.5, 0.5]
}


class TestInferencePipelineRule29(unittest.TestCase):
    """Rule #29: Log features at serving time."""

    def _make_pipeline(self, log_return_value="log-001"):
        model = MockModel()
        extractor = FeatureExtractor("src/mlaos_features/config.yaml")
        mock_logger = MagicMock(spec=ServingLogger)
        mock_logger.log_inference.return_value = log_return_value
        return InferencePipeline(
            model=model,
            feature_extractor=extractor,
            serving_logger=mock_logger
        ), mock_logger

    def test_predict_calls_log_inference(self):
        """Rule #29: predict() must call log_inference exactly once per request."""
        pipeline, mock_logger = self._make_pipeline()
        pipeline.predict(memory_id="mem-001", raw_data=RAW_DATA)
        mock_logger.log_inference.assert_called_once()

    def test_predict_logs_correct_request_id(self):
        """Rule #29: log_inference receives the same request_id as the response."""
        pipeline, mock_logger = self._make_pipeline()
        request_id = str(uuid.uuid4())
        result = pipeline.predict(
            memory_id="mem-001",
            raw_data=RAW_DATA,
            request_id=request_id
        )
        call_kwargs = mock_logger.log_inference.call_args
        logged_request_id = (
            call_kwargs.kwargs.get("request_id")
            or call_kwargs.args[0]
        )
        self.assertEqual(logged_request_id, request_id)
        self.assertEqual(result["request_id"], request_id)

    def test_predict_logs_feature_vector_not_raw_data(self):
        """Rule #29: log_inference must receive feature_vector, not raw_data.

        Glossary: feature_vector = extracted features, NOT raw sensor readings.
        Logging raw_data would cause training-serving skew (Rule #37 violation).
        """
        pipeline, mock_logger = self._make_pipeline()
        pipeline.predict(memory_id="mem-001", raw_data=RAW_DATA)

        call_kwargs = mock_logger.log_inference.call_args
        logged_features = (
            call_kwargs.kwargs.get("features_dict")
            or call_kwargs.args[2]
        )

        # Must NOT contain raw sensor keys
        self.assertNotIn("resonance_raw", logged_features)
        self.assertNotIn("light_intensity", logged_features)
        self.assertNotIn("dark_intensity", logged_features)

        # Must contain extracted feature keys
        self.assertIn("resonance_score", logged_features)
        self.assertIn("chiaroscuro_index", logged_features)

    def test_predict_logs_correct_memory_id(self):
        """Rule #29: memory_id (Glossary: instance) is passed to log_inference."""
        pipeline, mock_logger = self._make_pipeline()
        pipeline.predict(memory_id="mem-node-42", raw_data=RAW_DATA)

        call_kwargs = mock_logger.log_inference.call_args
        logged_memory_id = (
            call_kwargs.kwargs.get("memory_id")
            or call_kwargs.args[1]
        )
        self.assertEqual(logged_memory_id, "mem-node-42")

    def test_predict_returns_log_id(self):
        """Rule #29: result must include log_id from ServingLogger."""
        pipeline, mock_logger = self._make_pipeline(log_return_value="log-xyz-789")
        result = pipeline.predict(memory_id="mem-001", raw_data=RAW_DATA)
        self.assertEqual(result["log_id"], "log-xyz-789")

    def test_predict_does_not_crash_when_logger_fails(self):
        """Rule #10: inference must complete even if ServingLogger fails silently."""
        model = MockModel()
        extractor = FeatureExtractor("src/mlaos_features/config.yaml")
        mock_logger = MagicMock(spec=ServingLogger)
        mock_logger.log_inference.return_value = None  # Simulates silent DB failure
        pipeline = InferencePipeline(
            model=model,
            feature_extractor=extractor,
            serving_logger=mock_logger
        )
        # Must not raise even with None log_id
        result = pipeline.predict(memory_id="mem-001", raw_data=RAW_DATA)
        self.assertIsNone(result["log_id"])
        self.assertIn("prediction", result)

    def test_predict_auto_generates_request_id(self):
        """Rule #29: request_id is auto-generated as UUID if not provided."""
        pipeline, mock_logger = self._make_pipeline()
        result = pipeline.predict(memory_id="mem-001", raw_data=RAW_DATA)
        # Verify it's a valid UUID string
        parsed = uuid.UUID(result["request_id"])
        self.assertIsInstance(parsed, uuid.UUID)


class TestInferencePipelineRule37(unittest.TestCase):
    """Rule #37: Measure training-serving skew."""

    def _make_pipeline_with_auditor(self):
        model = MockModel()
        extractor = FeatureExtractor("src/mlaos_features/config.yaml")
        mock_logger = MagicMock(spec=ServingLogger)
        mock_logger.log_inference.return_value = "log-001"
        mock_auditor = MagicMock(spec=SkewAuditor)
        mock_auditor.run_audit.return_value = {
            "model_version": "TEST-v0.1",
            "features_audited": 5,
            "features_skewed": 0,
            "skewed_features": [],
            "alert": False,
            "results": {}
        }
        return InferencePipeline(
            model=model,
            feature_extractor=extractor,
            serving_logger=mock_logger,
            skew_auditor=mock_auditor
        ), mock_auditor

    def test_run_skew_audit_calls_auditor(self):
        """Rule #37: run_skew_audit() must call SkewAuditor.run_audit()."""
        pipeline, mock_auditor = self._make_pipeline_with_auditor()
        training_data = MagicMock()
        serving_data = MagicMock()
        pipeline.run_skew_audit(training_data=training_data, serving_data=serving_data)
        mock_auditor.run_audit.assert_called_once()

    def test_run_skew_audit_passes_training_and_serving_data(self):
        """Rule #37: Glossary training set vs serving distribution comparison."""
        pipeline, mock_auditor = self._make_pipeline_with_auditor()
        training_data = MagicMock(name="training_set")
        serving_data = MagicMock(name="serving_logs")
        pipeline.run_skew_audit(training_data=training_data, serving_data=serving_data)
        call_kwargs = mock_auditor.run_audit.call_args
        self.assertIs(
            call_kwargs.kwargs.get("training_data") or call_kwargs.args[0],
            training_data
        )

    def test_run_skew_audit_returns_report(self):
        """Rule #37: audit report must include expected keys."""
        pipeline, _ = self._make_pipeline_with_auditor()
        report = pipeline.run_skew_audit(
            training_data=MagicMock(),
            serving_data=MagicMock()
        )
        self.assertIn("alert", report)
        self.assertIn("features_audited", report)
        self.assertIn("features_skewed", report)

    def test_run_skew_audit_without_auditor_returns_no_alert(self):
        """Rule #37: pipeline without auditor returns safe default (no crash)."""
        model = MockModel()
        extractor = FeatureExtractor("src/mlaos_features/config.yaml")
        mock_logger = MagicMock(spec=ServingLogger)
        pipeline = InferencePipeline(
            model=model,
            feature_extractor=extractor,
            serving_logger=mock_logger,
            skew_auditor=None
        )
        report = pipeline.run_skew_audit(
            training_data=MagicMock(),
            serving_data=MagicMock()
        )
        self.assertFalse(report["alert"])


class TestInferencePipelineGlossary(unittest.TestCase):
    """Verify feature vector glossary alignment in the pipeline."""

    def test_feature_vector_is_extracted_not_raw(self):
        """Glossary: feature vector = extracted features, not raw sensor data."""
        model = MockModel()
        extractor = FeatureExtractor("src/mlaos_features/config.yaml")
        mock_logger = MagicMock(spec=ServingLogger)
        mock_logger.log_inference.return_value = "log-001"
        pipeline = InferencePipeline(
            model=model,
            feature_extractor=extractor,
            serving_logger=mock_logger
        )
        result = pipeline.predict(memory_id="mem-glossary", raw_data=RAW_DATA)

        # Glossary: feature vector must be normalized, extracted values
        features = result["features"]
        self.assertIsInstance(features, dict)
        # resonance_score is normalized [0,1]
        self.assertGreaterEqual(features["resonance_score"], 0.0)
        self.assertLessEqual(features["resonance_score"], 1.0)
        # chiaroscuro_index is synthetic: (0.8-0.2)/(0.8+0.2) = 0.6
        self.assertAlmostEqual(features["chiaroscuro_index"], 0.6, places=5)

    def test_prediction_contains_label(self):
        """Glossary: label = prediction output (resonance_score answer)."""
        model = MockModel()
        extractor = FeatureExtractor("src/mlaos_features/config.yaml")
        mock_logger = MagicMock(spec=ServingLogger)
        mock_logger.log_inference.return_value = "log-001"
        pipeline = InferencePipeline(
            model=model,
            feature_extractor=extractor,
            serving_logger=mock_logger
        )
        result = pipeline.predict(memory_id="mem-glossary", raw_data=RAW_DATA)
        # Glossary: label is in prediction dict
        self.assertIn("resonance_score", result["prediction"])
        self.assertIn("label", result["prediction"])


if __name__ == "__main__":
    unittest.main()

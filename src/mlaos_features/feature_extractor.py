"""FeatureExtractor: Rule #32 - Re-use code between training and serving.

Shared feature extraction logic used identically in both training pipeline
and online serving to prevent training-serving skew.
"""

import logging
import os
from typing import Dict, Any, List

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

FEATURE_EXTRACTOR_VERSION = "1.0.0"


class FeatureExtractor:
    """Extracts features from raw MLAOS data (Rule #32: shared train/serve code).

    Args:
        config_path: Path to YAML configuration file.
    """

    def __init__(self, config_path: str = "mlaos_features/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._version = FEATURE_EXTRACTOR_VERSION

    def _load_config(self, config_path: str) -> Dict:
        """Load feature extraction configuration from YAML."""
        if yaml is None:
            logger.warning("PyYAML not available; using default config.")
            return {"normalization": "zscore", "features": []}
        if not os.path.exists(config_path):
            logger.warning("Config not found at %s; using defaults.", config_path)
            return {"normalization": "zscore", "features": []}
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def get_version(self) -> str:
        """Return the feature extractor version string.

        Rule #32: Training and serving must use identical version.
        """
        return self._version

    def extract_features(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature vector from raw sensor data.

        Rule #32: This exact method is used in both training and serving pipelines.
        Feature extraction is deterministic - same input always produces same output.

        Args:
            raw_data: Raw instance data containing sensor readings.

        Returns:
            feature_vector: Normalized feature values for model input.
        """
        features = {}

        # Continuous features: resonance and impedance
        if "resonance_raw" in raw_data:
            features["resonance_score"] = self._normalize(float(raw_data["resonance_raw"]), 0.0, 1.0)

        if "impedance_raw" in raw_data:
            features["impedance_magnitude"] = self._normalize(float(raw_data["impedance_raw"]), 0.0, 100.0)

        # Synthetic feature: chiaroscuro_index (Rule: document synthetic features)
        if "light_intensity" in raw_data and "dark_intensity" in raw_data:
            light = float(raw_data["light_intensity"])
            dark = float(raw_data["dark_intensity"])
            denom = light + dark
            features["chiaroscuro_index"] = (light - dark) / denom if denom != 0.0 else 0.0

        # HRV score passthrough
        if "hrv_score" in raw_data:
            features["hrv_score"] = float(raw_data["hrv_score"])

        # Memory vector mean (discrete reduction)
        if "memory_vector" in raw_data:
            vec = raw_data["memory_vector"]
            if vec and len(vec) > 0:
                features["memory_vector_mean"] = sum(vec) / len(vec)

        return features

    @staticmethod
    def _normalize(value: float, min_val: float, max_val: float) -> float:
        """Min-max normalization to [0, 1] range."""
        if max_val == min_val:
            return 0.0
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    def get_feature_names(self) -> List[str]:
        """Return the list of feature names this extractor produces."""
        return [
            "resonance_score",
            "impedance_magnitude",
            "chiaroscuro_index",
            "hrv_score",
            "memory_vector_mean"
        ]

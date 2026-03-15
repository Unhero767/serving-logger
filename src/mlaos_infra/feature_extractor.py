"""Feature Extractor Module - MLAOS Production ML Infrastructure

Glossary Terms:
- feature: Input variable to a machine learning model
- feature engineering: Determining useful features & converting raw data (Rule #16)
- feature extraction: Retrieving intermediate feature representations
- synthetic feature: Feature assembled from one or more input features
- continuous feature: Floating-point feature with infinite range
- discrete feature: Feature with finite set of possible values
- normalization: Converting variable's actual range into standard range

Rules of ML Alignment:
- Rule #32: Re-use code between training and serving (single source of truth)
- Rule #16: Plan to launch and iterate (easy to add/remove features)
- Rule #11: Give feature columns owners and documentation
- Rule #17: Start with directly observed and reported features
"""

import yaml
import numpy as np
from typing import Dict, Any


class FeatureExtractor:
    """
    Glossary: feature engineering - Process of determining useful features & converting raw data

    Rule #32: "Re-use code between your training pipeline and your serving pipeline
    whenever possible." This eliminates a source of training-serving skew.

    This module is the SINGLE SOURCE OF TRUTH for feature extraction.
    Used by BOTH training_pipeline.py AND serving_logger.py.

    Glossary:
    - training: Process of determining ideal model parameters
    - serving: Process of making trained model available for predictions
    - training-serving skew: Difference between performance during training and serving
    """

    def __init__(self, config_path: str = "mlaos_features/config.yaml"):
        """
        Initialize FeatureExtractor with configuration.

        Glossary:
        - hyperparameter: Variables that you adjust during successive runs of training
        - configuration: Process of assigning initial property values used to train model

        Rule #32: Same configuration for training and serving
        Rule #11: Document feature configuration with owners

        Parameters:
        -----------
        config_path : str
            Path to feature configuration YAML file
        """
        self.config = self._load_config(config_path)
        self._version = "2.3"  # Rule #37: Track version for skew detection

    def _load_config(self, path: str) -> Dict:
        """
        Load feature configuration.

        Glossary:
        - feature column: Set of related features (Google-specific terminology)
        - categorical data: Features having specific set of possible values
        - numerical data: Features represented as integers or real-valued numbers

        Rule #11: Document feature columns with owners and descriptions
        """
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def extract_features(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from raw data.

        Glossary:
        - feature vector: Array of feature values comprising an example
        - example: Instance (with features) and possibly a label
        - instance: Thing about which you want to make prediction
        - synthetic feature: Feature assembled from one or more input features
        - continuous feature: Floating-point feature with infinite range
        - discrete feature: Feature with finite set of possible values

        Rule #32: SAME extraction logic for training AND serving
        Rule #17: Start with directly observed features (not learned features)
        Rule #20: Combine and modify existing features in human-understandable ways

        Parameters:
        -----------
        raw_data : Dict[str, Any]
            Raw instance data from EIS/MLAOS sensors

        Returns:
        --------
        feature_vector : Dict[str, float]
            Array of feature values for model input

        Example:
        --------
        >>> extractor = FeatureExtractor()
        >>> raw_data = {'resonance_raw': 0.75, 'light_intensity': 0.8, 'dark_intensity': 0.2}
        >>> features = extractor.extract_features(raw_data)
        >>> print(features)
        {'resonance_score': 0.875, 'chiaroscuro_index': 0.6, ...}
        """
        features = {}

        # Glossary: continuous feature - Floating-point feature with infinite range
        # Rule #17: Start with directly observed features
        raw_resonance = raw_data.get('resonance_raw', 0.0)
        features['resonance_score'] = self._normalize_resonance(raw_resonance)

        # Glossary: synthetic feature - Feature assembled from one or more input features
        # Rule #20: Combine features in human-understandable ways
        light = raw_data.get('light_intensity', 0.0)
        dark = raw_data.get('dark_intensity', 0.0)
        features['chiaroscuro_index'] = self._compute_chiaroscuro(light, dark)

        # Glossary: normalization - Converting variable's actual range into standard range
        # Rule #32: Same normalization for training and serving
        identity_vector = self.config.get('sigma7_vector', [0.5, 0.5, 0.5])
        memory_vector = raw_data.get('memory_vector', [0.0, 0.0, 0.0])
        features['sigma7_alignment'] = self._compute_alignment(identity_vector, memory_vector)

        return features

    def _normalize_resonance(self, raw_value: float) -> float:
        """
        Normalize resonance score to 0.0-1.0 range.

        Glossary:
        - normalization: Converting variable's actual range into standard range
        - continuous feature: Floating-point feature with infinite range

        Rule #32: Same normalization for training and serving (eliminates skew)
        """
        min_val = self.config.get('resonance_min', -1.0)
        max_val = self.config.get('resonance_max', 1.0)
        return (raw_value - min_val) / (max_val - min_val)

    def _compute_chiaroscuro(self, light: float, dark: float) -> float:
        """
        Compute chiaroscuro index from light/dark intensity.

        Glossary:
        - synthetic feature: Feature assembled from one or more input features
        - feature engineering: Determining useful features & converting raw data

        Rule #20: Combine and modify existing features in human-understandable ways
        """
        if light + dark == 0:
            return 0.0
        return abs(light - dark) / (light + dark)

    def _compute_alignment(self, vec1: list, vec2: list) -> float:
        """
        Compute cosine similarity alignment score.

        Glossary:
        - feature vector: Array of feature values comprising an example
        - normalization: Converting variable's actual range into standard range

        Rule #32: Same computation for training and serving
        """
        v1, v2 = np.array(vec1), np.array(vec2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm == 0:
            return 0.0
        return float(np.dot(v1, v2) / norm)

    def get_version(self) -> str:
        """
        Get feature extractor version.

        Glossary:
        - model: Statistical representation of a prediction task

        Rule #37: Track version for training-serving skew detection
        """
        return self._version

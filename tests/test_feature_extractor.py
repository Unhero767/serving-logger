import unittest
from mlaos_features.feature_extractor import FeatureExtractor


class TestFeatureExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = FeatureExtractor("mlaos_features/config.yaml")

    def test_extractor_version_matches(self):
        """Rule #32: Ensure training and serving use identical feature extraction"""
        training_extractor = FeatureExtractor("mlaos_features/config.yaml")
        serving_extractor = FeatureExtractor("mlaos_features/config.yaml")

        self.assertEqual(
            training_extractor.get_version(),
            serving_extractor.get_version(),
            "Training and serving feature versions must match"
        )

    def test_feature_output_deterministic(self):
        """Same input must produce same output every time"""
        raw_data = {
            'resonance_raw': 0.75,
            'light_intensity': 0.8,
            'dark_intensity': 0.2,
            'memory_vector': [0.5, 0.5, 0.5]
        }

        # Run extraction 10 times
        outputs = [self.extractor.extract_features(raw_data) for _ in range(10)]

        # All outputs must be identical
        for i in range(1, len(outputs)):
            self.assertEqual(outputs[0], outputs[i], "Feature extraction must be deterministic")


if __name__ == '__main__':
    unittest.main()

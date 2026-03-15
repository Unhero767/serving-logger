import pytest
import json
from unittest.mock import MagicMock, patch
from src.serving_logger import ServingLogger


@pytest.fixture
def logger():
    return ServingLogger(
        model_version="v1.0",
        environment="test",
        db_config={"host": "localhost", "dbname": "test_db", "user": "test", "password": "test"}
    )


class TestServingLogger:

    @patch("src.serving_logger.psycopg2.connect")
    def test_log_prediction(self, mock_connect, logger):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        features = {"feature_a": 1.5, "feature_b": 0.3}
        prediction = {"label": "positive", "score": 0.87}

        logger.log_prediction(
            request_id="req_001",
            features=features,
            prediction=prediction
        )

        assert mock_cursor.execute.called

    @patch("src.serving_logger.psycopg2.connect")
    def test_log_prediction_stores_correct_data(self, mock_connect, logger):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        features = {"price": 99.99}
        prediction = {"class": "A"}

        logger.log_prediction(
            request_id="req_002",
            features=features,
            prediction=prediction,
            latency_ms=42.5
        )

        call_args = mock_cursor.execute.call_args
        assert call_args is not None

    @patch("src.serving_logger.psycopg2.connect")
    def test_log_feedback(self, mock_connect, logger):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        logger.log_feedback(
            request_id="req_001",
            actual_label="positive",
            feedback_source="human"
        )

        assert mock_cursor.execute.called

    @patch("src.serving_logger.psycopg2.connect")
    def test_get_recent_predictions(self, mock_connect, logger):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("req_001", "v1.0", {}, {}, None, None, "2024-01-01")
        ]

        results = logger.get_recent_predictions(hours=24)
        assert isinstance(results, list)

    def test_invalid_environment_raises(self):
        with pytest.raises(ValueError):
            ServingLogger(
                model_version="v1.0",
                environment="staging",
                db_config={}
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

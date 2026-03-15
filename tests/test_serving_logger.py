import unittest
import psycopg2
import uuid
from mlaos_infra.serving_logger import ServingLogger


class TestServingLogger(unittest.TestCase):

    def setUp(self):
        self.db_conn_string = "postgresql://test:test@localhost/mlaos_test"
        self.logger = ServingLogger(self.db_conn_string, "TEST-v0.1")

    def test_log_inference_writes_to_db(self):
        """Rule #5: Verify data actually reaches the database"""
        request_id = str(uuid.uuid4())
        memory_id = "test_mem_001"
        features = {'resonance_score': 0.85, 'chiaroscuro_index': 0.42}

        self.logger.log_inference(request_id, memory_id, features)

        # Verify write
        conn = psycopg2.connect(self.db_conn_string)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM serving_logs WHERE request_id = %s", (request_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()

        self.assertEqual(count, 2, "Expected 2 feature rows logged")

    def test_logger_fails_silently_on_db_error(self):
        """Rule #5 & #10: Logger should not crash inference on DB failure"""
        bad_logger = ServingLogger("postgresql://invalid:connection@string", "TEST-v0.1")

        # This should NOT raise an exception
        try:
            bad_logger.log_inference(str(uuid.uuid4()), "test_mem", {'score': 0.5})
            passed = True
        except Exception:
            passed = False

        self.assertTrue(passed, "Logger should fail silently, not crash inference")


if __name__ == '__main__':
    unittest.main()

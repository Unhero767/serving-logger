"""Infrastructure tests for MLAOS.

Rule #5: Test the infrastructure independently from the machine learning.
Verifies that database tables, indexes, and migrations are correctly set up.
"""

import os
import pytest
import psycopg2


DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/mlaos_test")


@pytest.fixture(scope="module")
def db_conn():
    """Return a live DB connection for infrastructure tests."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
        conn.close()
    except psycopg2.OperationalError:
        pytest.skip("No database available for infrastructure tests")


class TestFeatureRegistryTable:
    """Rule #5: Test the feature_registry table infrastructure."""

    def test_feature_registry_exists(self, db_conn):
        """Verify feature_registry table was created by migration 001."""
        cur = db_conn.cursor()
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'feature_registry')"
        )
        assert cur.fetchone()[0] is True, "feature_registry table must exist"
        cur.close()

    def test_feature_registry_columns(self, db_conn):
        """Verify all required columns for Rule #11 compliance."""
        cur = db_conn.cursor()
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'feature_registry'"
        )
        columns = {row[0] for row in cur.fetchall()}
        required = {
            "feature_name", "feature_type", "status",
            "owner_email", "description", "expected_coverage_pct",
            "created_at", "updated_at",
        }
        assert required.issubset(columns), f"Missing columns: {required - columns}"
        cur.close()

    def test_seeded_features_present(self, db_conn):
        """Verify initial MLAOS features were seeded (Rule #17)."""
        cur = db_conn.cursor()
        cur.execute("SELECT feature_name FROM feature_registry WHERE status = 'ACTIVE'")
        names = {row[0] for row in cur.fetchall()}
        expected = {
            "resonance_score", "impedance_magnitude", "hrv_score",
            "chiaroscuro_index", "sigma7_alignment",
        }
        assert expected.issubset(names), f"Missing features: {expected - names}"
        cur.close()


class TestServingLogsTable:
    """Rule #5: Test the serving_logs table infrastructure."""

    def test_serving_logs_exists(self, db_conn):
        """Verify serving_logs table was created by migration 002."""
        cur = db_conn.cursor()
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'serving_logs')"
        )
        assert cur.fetchone()[0] is True, "serving_logs table must exist"
        cur.close()

    def test_serving_logs_columns(self, db_conn):
        """Verify serving_logs has all required columns for Rule #29."""
        cur = db_conn.cursor()
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'serving_logs'"
        )
        columns = {row[0] for row in cur.fetchall()}
        required = {
            "id", "model_name", "model_version",
            "input_hash", "prediction", "served_at",
        }
        assert required.issubset(columns), f"Missing columns: {required - columns}"
        cur.close()


class TestDatabaseIndexes:
    """Rule #5: Verify performance indexes exist."""

    def test_feature_registry_status_index(self, db_conn):
        """Verify status index exists for Rule #22 pruning queries."""
        cur = db_conn.cursor()
        cur.execute(
            "SELECT indexname FROM pg_indexes "
            "WHERE tablename = 'feature_registry' AND indexname = 'idx_feature_registry_status'"
        )
        assert cur.fetchone() is not None, "Status index must exist"
        cur.close()

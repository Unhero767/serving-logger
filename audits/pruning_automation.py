"""Pruning Automation Module - MLAOS Audits

Rule #22: Clean up features you are no longer using.
Rule #16: Plan to launch and iterate (easy to add/remove features).

Automatically marks DEPRECATED features and prunes unused ones
from the feature_registry on a weekly schedule.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import psycopg2

logger = logging.getLogger(__name__)

# Rule #22: How many days without serving before a feature is considered unused
UNUSED_THRESHOLD_DAYS = 30


class PruningAutomation:
    """Automates feature pruning per Rule #22.

    Rule #22: Clean up features you are no longer using.
    Features not seen in serving_logs for UNUSED_THRESHOLD_DAYS
    are marked DEPRECATED and flagged for removal.
    """

    def __init__(self, db_url: str, dry_run: bool = True) -> None:
        """
        Parameters
        ----------
        db_url : str
            PostgreSQL connection URL.
        dry_run : bool
            If True, report what would be pruned but don't mutate the DB.
            Default True for safety.
        """
        self.db_url = db_url
        self.dry_run = dry_run
        self._pruned_count: int = 0
        self._error_count: int = 0

    def _connect(self):
        return psycopg2.connect(self.db_url)

    def find_unused_features(
        self,
        threshold_days: int = UNUSED_THRESHOLD_DAYS,
    ) -> List[str]:
        """Find ACTIVE features with no serving_logs in the last threshold_days.

        Rule #22: Identify candidates for deprecation.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=threshold_days)
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT fr.feature_name
                FROM feature_registry fr
                WHERE fr.status = 'ACTIVE'
                  AND NOT EXISTS (
                      SELECT 1 FROM serving_logs sl
                      WHERE sl.prediction ? fr.feature_name
                        AND sl.served_at > %s
                  )
                """,
                (cutoff,),
            )
            unused = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return unused
        except Exception as e:
            logger.error("find_unused_features failed (Rule #10): %s", e)
            self._error_count += 1
            return []

    def deprecate_features(self, feature_names: List[str]) -> int:
        """Mark features as DEPRECATED in the feature_registry.

        Rule #22: Mark before deletion to allow review period.

        Returns
        -------
        int
            Number of features deprecated.
        """
        if not feature_names:
            return 0
        if self.dry_run:
            logger.info(
                "[DRY RUN] Would deprecate %d features: %s",
                len(feature_names), feature_names,
            )
            return 0
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE feature_registry
                SET status = 'DEPRECATED', updated_at = NOW()
                WHERE feature_name = ANY(%s)
                  AND status = 'ACTIVE'
                """,
                (feature_names,),
            )
            count = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            self._pruned_count += count
            logger.info("Deprecated %d features (Rule #22): %s", count, feature_names)
            return count
        except Exception as e:
            logger.error("deprecate_features failed (Rule #10): %s", e)
            self._error_count += 1
            return 0

    def run_weekly_prune(self) -> Dict:
        """Run full weekly pruning cycle.

        Rule #22: Weekly automated pruning to reduce technical debt.
        """
        unused = self.find_unused_features()
        deprecated_count = self.deprecate_features(unused)
        report = {
            "unused_features_found": unused,
            "deprecated_count": deprecated_count,
            "dry_run": self.dry_run,
            "threshold_days": UNUSED_THRESHOLD_DAYS,
            "run_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("Weekly prune complete (Rule #22): %s", report)
        return report

    def get_health_status(self) -> Dict:
        """Return pruning automation health (Rule #10)."""
        return {
            "pruned_count": self._pruned_count,
            "error_count": self._error_count,
            "is_healthy": self._error_count < 5,
            "dry_run": self.dry_run,
        }

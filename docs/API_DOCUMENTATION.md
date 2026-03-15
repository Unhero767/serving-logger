# MLAOS Engine API Documentation
**Repository:** `serving-logger` | **Owner:** `Unhero767`

This API documentation integrates standard ML terminology to ensure compliance with Google's Rules of Machine Learning. See `docs/glossary.md` for term definitions.

---

## Core Modules

### `FeatureExtractor`
**Location:** `src/mlaos_features/feature_extractor.py`
**Rule Alignment:** Rule #16 (Launch & Iterate), Rule #32 (Re-use code train/serve)

The `FeatureExtractor` is the **single source of truth** for converting raw data into a **feature vector**. It guarantees identical **preprocessing** across training and serving, eliminating **training-serving skew**.

#### Methods

| Method | Signature | Description |
|---|---|---|
| `extract_features` | `(raw_data: Dict) -> Dict[str, float]` | Main entry: converts raw sensor data to feature vector |
| `_normalize_resonance` | `(raw_value: float) -> float` | Normalizes resonance to 0.0–1.0 (Rule #32) |
| `_compute_chiaroscuro` | `(light: float, dark: float) -> float` | Synthetic feature: abs(l-d)/(l+d) (Rule #20) |
| `_compute_alignment` | `(vec1: list, vec2: list) -> float` | Cosine similarity sigma7 alignment (Rule #32) |
| `get_version` | `() -> str` | Returns extractor version string (Rule #37) |

#### Glossary Integrations
- **Feature Engineering:** Extracts **continuous features** (`impedance_magnitude`) and **discrete features** from raw session data.
- **Feature Vector:** Outputs a standardized array of **feature values** comprising a single **example**.
- **Offline/Online Inference:** Compatible with both **batch inference** (offline) and **online inference** (real-time).
- **Synthetic Feature:** `chiaroscuro_index` assembled from `light_intensity` and `dark_intensity`.

---

### `ServingLogger`
**Location:** `src/mlaos_infra/serving_logger.py`
**Rule Alignment:** Rule #29 (Log features at serving time), Rule #10 (Watch for silent failures)

The `ServingLogger` captures exact **feature values** at **inference** time, preventing **silent failures** caused by **concept drift** or shifting upstream data.

#### Methods

| Method | Signature | Description |
|---|---|---|
| `log` | `(input_hash, prediction, actual_label, latency_ms) -> Optional[str]` | Persists a single serving event; returns row UUID |
| `batch_log` | `(records: List[Dict]) -> int` | Bulk-inserts multiple serving events |
| `recent_predictions` | `() -> List` | Returns predictions from the last 24 hours |
| `get_health_status` | `() -> Dict` | Returns error_count, last_success_time, is_healthy |

#### Glossary Integrations
- **Serving:** Operates strictly during the **serving** phase to log what the model actually sees.
- **Inference:** Captures **unlabeled examples** precisely as fed into the prediction model.
- **Ground Truth:** Creates foundational logs required to reconstruct the **training set** later.
- **Silent Failure:** `get_health_status()` surfaces `error_count` to detect failures (Rule #10).

---

### `SkewAnalysis`
**Location:** `audits/skew_analysis.py`
**Rule Alignment:** Rule #37 (Measure training/serving skew), Rule #10 (Watch for silent failures)

Runs Kolmogorov-Smirnov statistical tests between training and serving **distributions** to detect **training-serving skew**.

#### Methods

| Method | Signature | Description |
|---|---|---|
| `fetch_serving_features` | `(feature_name: str, hours_back: int) -> List[float]` | Fetches recent serving values for a feature |
| `run_ks_test` | `(training_values, serving_values) -> Tuple[float, float]` | Returns (ks_statistic, p_value) |
| `analyze_feature` | `(feature_name: str, training_values: List) -> Dict` | Full skew analysis for one feature |
| `run_full_audit` | `(training_data: Dict) -> List[Dict]` | Runs audit across all features |
| `get_health_status` | `() -> Dict` | Returns error_count, is_healthy |

#### Glossary Integrations
- **Distribution:** Compares feature value distributions between **training set** and **serving** logs.
- **Training-Serving Skew:** Target: KS stat < 0.1 (Rule #37).
- **Generalization:** Skew > threshold signals degraded **generalization** in production.

---

### `PruningAutomation`
**Location:** `audits/pruning_automation.py`
**Rule Alignment:** Rule #22 (Clean up features you are no longer using)

Automates weekly identification and deprecation of unused **features** in `feature_registry`.

#### Methods

| Method | Signature | Description |
|---|---|---|
| `find_unused_features` | `(threshold_days: int) -> List[str]` | Finds ACTIVE features absent from serving logs |
| `deprecate_features` | `(feature_names: List[str]) -> int` | Marks features DEPRECATED in feature_registry |
| `run_weekly_prune` | `() -> Dict` | Full weekly pruning cycle |
| `get_health_status` | `() -> Dict` | Returns pruned_count, error_count, is_healthy |

#### Glossary Integrations
- **Ablation:** Pruning identifies features that contribute nothing (Rule #22).
- **Discrete Feature:** `status` field transitions: ACTIVE → DEPRECATED (Rule #11).
- **Technical Debt:** Regular pruning prevents accumulation of stale feature columns.

---

## Database Schema

### `feature_registry` (Migration: `sql/001_feature_registry.sql`)
Ownership and documentation for all **feature columns** (Rule #11).

| Column | Type | Description |
|---|---|---|
| `feature_name` | TEXT UNIQUE | Canonical feature identifier |
| `feature_type` | TEXT | NUMERIC, CATEGORICAL, or EMBEDDING |
| `status` | TEXT | ACTIVE, EXPERIMENTAL, or DEPRECATED |
| `owner_email` | TEXT | Rule #11: accountable owner |
| `description` | TEXT | Human-readable feature description |
| `expected_coverage_pct` | FLOAT | Minimum expected coverage (0.0–1.0) |

### `serving_logs` (Migration: `sql/002_serving_logs.sql`)
Captures exact feature values at inference time (Rule #29).

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `model_name` | TEXT | Model name |
| `model_version` | TEXT | Version for Rule #37 skew tracking |
| `input_hash` | TEXT | Deduplication hash of model input |
| `prediction` | JSONB | Feature values as logged (Rule #29) |
| `actual_label` | TEXT | Ground truth when available |
| `latency_ms` | FLOAT | Inference latency (Rule #2 metric) |
| `served_at` | TIMESTAMPTZ | Timestamp of prediction |

---

## Rules of ML Quick Reference

| Rule | Implementation |
|---|---|
| #10 Watch for silent failures | `get_health_status()` on all modules |
| #11 Feature column owners | `feature_registry` table with `owner_email` |
| #16 Launch and iterate | `status` field: EXPERIMENTAL → ACTIVE → DEPRECATED |
| #17 Start with observed features | Direct sensor readings as primary features |
| #20 Combine features intuitively | `chiaroscuro_index` synthetic feature |
| #22 Clean up unused features | `PruningAutomation.run_weekly_prune()` |
| #29 Log features at serving time | `ServingLogger.log()` captures all feature values |
| #32 Re-use code train/serve | `FeatureExtractor` shared single source of truth |
| #37 Measure training/serving skew | `SkewAnalysis.run_full_audit()` weekly |

---

**Last Updated:** March 2026
**Maintainer:** Kenneth Dallmier (kennydallmier@gmail.com)

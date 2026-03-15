# Repository Component to Glossary Terms Mapping

## Overview

This document maps each MLAOS repository component to relevant **Google ML Glossary terms** and **Rules of Machine Learning**. This ensures consistent terminology and best practices across the codebase.

---

## Repository Structure

```
serving-logger/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── requirements.txt
├── sql/
│   ├── 001_feature_registry.sql
│   └── 002_serving_logs.sql
├── src/
│   ├── mlaos_infra/
│   │   ├── __init__.py
│   │   ├── serving_logger.py
│   │   └── skew_auditor.py
│   └── mlaos_features/
│       ├── __init__.py
│       └── feature_extractor.py
├── tests/
│   ├── __init__.py
│   ├── test_infrastructure.py
│   ├── test_serving_logger.py
│   └── test_feature_extractor.py
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── glossary.md
│   ├── COMPONENT_GLOSSARY_MAPPING.md
│   └── images/
├── audits/
│   ├── __init__.py
│   ├── skew_analysis.py
│   └── pruning_automation.py
└── mlaos_features/
    ├── __init__.py
    └── config.yaml
```

---

## Component Mappings

### `src/mlaos_features/feature_extractor.py`

| Glossary Term | Application |
|---|---|
| **Feature Engineering** | Core purpose of module: raw data → feature vector |
| **Feature Vector** | Output of `extract_features()` |
| **Continuous Feature** | `resonance_score`, `hrv_score`, `impedance_magnitude` |
| **Synthetic Feature** | `chiaroscuro_index` = abs(light-dark)/(light+dark) |
| **Normalization** | `_normalize_resonance()` maps raw to 0.0–1.0 |
| **Training-Serving Skew** | Eliminated by Rule #32: shared extraction logic |
| **Preprocessing** | Single source of truth for train & serve |

**Rules:** #16, #17, #20, #32, #37

---

### `src/mlaos_infra/serving_logger.py`

| Glossary Term | Application |
|---|---|
| **Serving** | Module operates exclusively in serving phase |
| **Inference** | Captures features at prediction time |
| **Unlabeled Example** | Inference-time data without ground truth label |
| **Ground Truth** | `actual_label` field added post-inference |
| **Silent Failure** | `get_health_status()` surfaces `error_count` |
| **Metric** | `latency_ms` tracked per prediction (Rule #2) |
| **Training-Serving Skew** | Logs enable Rule #37 KS-test audits |

**Rules:** #2, #10, #29, #37

---

### `sql/001_feature_registry.sql`

| Glossary Term | Application |
|---|---|
| **Feature Column** | Each row = one feature column with owner |
| **Discrete Feature** | `status`: ACTIVE, EXPERIMENTAL, DEPRECATED |
| **Categorical Data** | `feature_type`: NUMERIC, CATEGORICAL, EMBEDDING |
| **Feature** | Canonical list of all MLAOS model inputs |
| **Technical Debt** | `DEPRECATED` status tracks cleanup candidates |

**Rules:** #11, #16, #22

---

### `sql/002_serving_logs.sql`

| Glossary Term | Application |
|---|---|
| **Serving** | Table stores all serving-time events |
| **Feature Vector** | `prediction` JSONB stores the feature vector |
| **Labeled Example** | Row with both `prediction` and `actual_label` |
| **Unlabeled Example** | Row with `prediction` but no `actual_label` |
| **Training Set** | Historical serving_logs used as training data |
| **Distribution** | Column data used for KS-test skew analysis |

**Rules:** #29, #37

---

### `audits/skew_analysis.py`

| Glossary Term | Application |
|---|---|
| **Training-Serving Skew** | Core purpose: detect and quantify skew |
| **Distribution** | KS-test compares training vs serving distributions |
| **Generalization** | Skew alert signals degraded generalization |
| **Generalization Curve** | `ks_statistic` over time trends |
| **Silent Failure** | `get_health_status()` catches analysis errors |

**Rules:** #10, #37

---

### `audits/pruning_automation.py`

| Glossary Term | Application |
|---|---|
| **Ablation** | Identifies zero-contribution features |
| **Feature** | Targets unused features in `feature_registry` |
| **Discrete Feature** | `status` transitions: ACTIVE → DEPRECATED |
| **Technical Debt** | Weekly prune prevents accumulation |
| **Silent Failure** | `get_health_status()` monitors prune errors |

**Rules:** #10, #16, #22

---

### `tests/test_infrastructure.py`

| Glossary Term | Application |
|---|---|
| **Pipeline** | Tests that DB infrastructure is correctly set up |
| **Feature Column** | Validates `feature_registry` schema |
| **Silent Failure** | Catches DB setup issues before production |

**Rules:** #5, #10

---

### `tests/test_serving_logger.py`

| Glossary Term | Application |
|---|---|
| **Serving** | Tests serving-time logging behavior |
| **Inference** | Tests feature capture at prediction time |
| **Silent Failure** | Validates `get_health_status()` error surfacing |

**Rules:** #5, #10, #29

---

### `tests/test_feature_extractor.py`

| Glossary Term | Application |
|---|---|
| **Feature Engineering** | Tests feature extraction correctness |
| **Normalization** | Validates resonance normalization bounds |
| **Synthetic Feature** | Tests `chiaroscuro_index` computation |
| **Training-Serving Skew** | Validates version consistency (Rule #37) |

**Rules:** #5, #32, #37

---

### `mlaos_features/config.yaml`

| Glossary Term | Application |
|---|---|
| **Hyperparameter** | Feature config values (min/max ranges) |
| **Configuration** | Initial property values for `FeatureExtractor` |
| **Feature Column** | Defines sigma7_vector, resonance bounds |

**Rules:** #11, #32

---

## Rules of ML Coverage Matrix

| Rule | Components Implementing It |
|---|---|
| #2 Design metrics first | `serving_logger.py` (latency_ms metric) |
| #4 Simple model, right infra | `sql/`, `src/`, `tests/` (infrastructure first) |
| #5 Test infra independently | `tests/test_infrastructure.py` |
| #8 Know freshness requirements | `skew_analysis.py` (7-day lookback) |
| #10 Watch for silent failures | All modules via `get_health_status()` |
| #11 Feature column owners | `sql/001_feature_registry.sql`, `config.yaml` |
| #16 Plan to launch & iterate | `feature_registry.status` field lifecycle |
| #17 Start with observed features | `feature_extractor.py` raw sensor readings |
| #20 Combine features intuitively | `_compute_chiaroscuro()` in `feature_extractor.py` |
| #22 Clean up unused features | `audits/pruning_automation.py` |
| #29 Log features at serving time | `src/mlaos_infra/serving_logger.py` |
| #32 Re-use code train/serve | `src/mlaos_features/feature_extractor.py` |
| #37 Measure training/serving skew | `audits/skew_analysis.py` |

---

**Last Updated:** March 2026
**Maintainer:** Kenneth Dallmier (kennydallmier@gmail.com)

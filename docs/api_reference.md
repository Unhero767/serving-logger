# MLAOS Infrastructure API Documentation

## Overview

This API documentation includes **Google ML Glossary term definitions** integrated directly into each endpoint and function description. This ensures consistent terminology across the MLAOS project and aligns with industry best practices.

---

## Serving Logger API

### `log_inference(request_id, memory_id, features_dict)`

**Purpose:** Log exact **feature** values at **inference** time for **training-serving skew** detection.

**Glossary Terms:**

| Term | Definition (Google ML Glossary) | MLAOS Context |
|------|--------------------------------|---------------|
| **feature** | An input variable to a machine learning model | `resonance_score`, `impedance_magnitude`, `hrv_score` |
| **inference** | Making predictions by applying trained model to unlabeled examples | Online MLAOS cognitive predictions |
| **feature vector** | The array of feature values comprising an example | Input to `FeatureExtractor` for train/serve |
| **example** | The values of one row of features and possibly a label | One MLAOS memory node session |
| **label** | The "answer" or "result" portion of an example | `resonance_score` (0.0-1.0) |

**Parameters:**

| Parameter | Type | Description | Glossary Alignment |
|-----------|------|-------------|-------------------|
| `request_id` | str | Unique identifier for this **inference** request | **inference**: Process of making predictions |
| `memory_id` | str | Identifier for the **instance** being predicted | **instance**: Thing about which you want to make prediction |
| `features_dict` | dict | **Feature vector** as key-value pairs | **feature vector**: Array of feature values |

**Returns:**

| Return | Type | Description |
|--------|------|-------------|
| `log_id` | str | Unique identifier for logged **example** |

**Rule Alignment:** Rule #29 (Log features at serving time)

---

## Feature Registry API

### `register_feature(feature_name, owner_email, description, expected_coverage_pct)`

**Purpose:** Register a new **feature column** with ownership tracking per Rule #11.

**Glossary Terms:**

| Term | Definition (Google ML Glossary) | MLAOS Context |
|------|--------------------------------|---------------|
| **feature column** | A set of related features (Google-specific terminology) | Set of all possible `resonance_score` values |
| **feature engineering** | Determining useful features & converting raw data | `FeatureExtractor` module creates synthetic features |
| **categorical data** | Features having a specific set of possible values | `status`: ACTIVE, EXPERIMENTAL, DEPRECATED |
| **numerical data** | Features represented as integers or real-valued numbers | `resonance_score`, `impedance_magnitude` |

**Parameters:**

| Parameter | Type | Description | Glossary Alignment |
|-----------|------|-------------|-------------------|
| `feature_name` | str | Name of the **feature column** | **feature column**: Set of related features |
| `owner_email` | str | Email of **feature** owner | Rule #11: Give feature columns owners |
| `description` | str | Detailed **feature** description | Rule #11: Documentation requirement |
| `expected_coverage_pct` | float | Expected **feature** coverage percentage | **coverage**: How many examples have this feature |

**Rule Alignment:** Rule #11 (Give feature columns owners and documentation)

---

## Skew Auditor API

### `measure_skew(training_data, serving_data, threshold=0.05)`

**Purpose:** Measure **training-serving skew** between datasets using KS test.

**Glossary Terms:**

| Term | Definition (Google ML Glossary) | MLAOS Context |
|------|--------------------------------|---------------|
| **training-serving skew** | Difference between performance during training and serving | Weekly skew audits (KS test, p<0.05) |
| **training set** | Subset of dataset used to train model | Data until January 5th |
| **test set** | Subset reserved for testing trained model | Data from January 6th and after |
| **generalization** | Model's ability to make correct predictions on new data | Test on held-out temporal data |
| **concept drift** | Shift in relationship between features and label over time | Monitor for freshness degradation |

**Parameters:**

| Parameter | Type | Description | Glossary Alignment |
|-----------|------|-------------|-------------------|
| `training_data` | pd.DataFrame | **Training set** feature distributions | **training set**: Subset used to train model |
| `serving_data` | pd.DataFrame | **Serving** log feature distributions | **serving**: Process of making trained model available |
| `threshold` | float | KS test p-value **threshold** for alert | Alert if p < 0.05 |

**Returns:**

| Return | Type | Description |
|--------|------|-------------|
| `ks_statistic` | float | KS test statistic (0.0-1.0) |
| `p_value` | float | KS test p-value |
| `skew_detected` | bool | True if **training-serving skew** detected |

**Rule Alignment:** Rule #37 (Measure training/serving skew)

---

## Feature Extractor API

### `extract_features(raw_data) -> feature_vector`

**Purpose:** Extract **features** from raw data using shared code for **training** and **serving**.

**Glossary Terms:**

| Term | Definition (Google ML Glossary) | MLAOS Context |
|------|--------------------------------|---------------|
| **feature extraction** | Retrieving intermediate feature representations | `FeatureExtractor` module |
| **synthetic feature** | Feature assembled from one or more input features | `chiaroscuro_index` from light/dark intensity |
| **continuous feature** | Floating-point feature with infinite range | `resonance_score`, `impedance_magnitude` |
| **discrete feature** | Feature with finite set of possible values | `status`: ACTIVE, EXPERIMENTAL, DEPRECATED |
| **normalization** | Converting variable's actual range into standard range | Z-score normalization for numerical features |

**Parameters:**

| Parameter | Type | Description | Glossary Alignment |
|-----------|------|-------------|-------------------|
| `raw_data` | dict | Raw **instance** data from EIS/MLAOS sensors | **instance**: Thing about which you want to make prediction |

**Returns:**

| Return | Type | Description |
|--------|------|-------------|
| `feature_vector` | dict | Array of **feature** values for **model** input |

**Rule Alignment:** Rule #32 (Re-use code between training and serving)

---

## Google ML Rules Alignment Summary

| Rule | Description | API / Module |
|------|-------------|-------------|
| Rule #11 | Give feature columns owners and documentation | `register_feature()` |
| Rule #29 | Log features at serving time | `log_inference()` |
| Rule #32 | Re-use code between training and serving | `extract_features()` |
| Rule #37 | Measure training/serving skew | `measure_skew()` |

---

*MLAOS Infrastructure — serving-logger v1.0 | Last updated: 2026-03-15*

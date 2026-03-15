# MLAOS Engine API Documentation
**Repository:** `mlaos-infra` | **Owner:** `Unhero767`

This API documentation integrates standard ML terminology to ensure compliance with Google's Rules of Machine Learning.

## Core Modules

### `FeatureExtractor`
**Location:** `src/mlaos_features/feature_extractor.py`
**Rule Alignment:** Rule #16 (Launch & Iterate), Rule #32 (Re-use code train/serve)

The `FeatureExtractor` serves as the single source of truth for converting raw data into a **feature vector**. It guarantees that the **preprocessing** logic remains identical across both **training** and **serving** environments, eliminating a primary source of **training-serving skew**.

* **Glossary Integrations:**
    * **Feature Engineering:** Extracts **continuous features** (e.g., `impedance_magnitude`) and **discrete features** from raw session data.
    * **Feature Vector:** Outputs a standardized array of **feature values** comprising a single **example**.
    * **Offline/Online Inference:** Compatible with both **batch inference** (offline) and **online inference** (real-time).

### `ServingLogger`
**Location:** `src/mlaos_infra/serving_logger.py`
**Rule Alignment:** Rule #29 (Log features at serving time)

The `ServingLogger` asynchronously captures exact **feature values** at **inference** time. This prevents **silent failures** caused by **concept drift** or shifting data upstream.

* **Glossary Integrations:**
    * **Serving:** Operates strictly during the **serving** phase to log what the model actually sees.
    * **Inference:** Captures the **unlabeled examples** precisely as they are fed into the prediction model.
    * **Ground Truth:** Creates the foundational logs required to reconstruct the **training set** accurately later.

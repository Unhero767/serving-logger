# MLAOS Glossary

This is the canonical glossary for the MLAOS project, co-located in `docs/` for easy reference during development.
For the full extended version see `GLOSSARY.md` at the repository root.

**Sources:**
- [Google ML Glossary](https://developers.google.com/machine-learning/glossary)
- [Google Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)

---

## Core Terms

| Term | Definition | MLAOS Usage | Rule |
|---|---|---|---|
| **Feature** | Input variable to a ML model | `resonance_score`, `impedance_magnitude`, `hrv_score`, `chiaroscuro_index`, `sigma7_alignment` | #11 |
| **Feature Vector** | Array of feature values comprising an example | Output of `FeatureExtractor.extract_features()` | #32 |
| **Feature Engineering** | Determining useful features & converting raw data | `FeatureExtractor` module | #16 |
| **Synthetic Feature** | Feature assembled from one or more input features | `chiaroscuro_index` from light/dark intensity | #20 |
| **Continuous Feature** | Floating-point feature with infinite range | `resonance_score` (0.0–1.0), `hrv_score` | #17 |
| **Discrete Feature** | Feature with finite set of possible values | `status`: ACTIVE, EXPERIMENTAL, DEPRECATED | #11 |
| **Normalization** | Converting variable's actual range to standard range | `_normalize_resonance()` in `FeatureExtractor` | #32 |
| **Training** | Determining ideal model parameters | MLAOS training pipeline | #4 |
| **Serving** | Making trained model available for predictions | Online inference with `ServingLogger` | #29 |
| **Training-Serving Skew** | Performance difference between training and serving | Measured weekly with KS test | #37 |
| **Inference** | Making predictions by applying a trained model | Online + batch inference modes | #29 |
| **Silent Failure** | Problem that occurs without obvious error | `get_health_status()` on all modules | #10 |
| **Concept Drift** | Shift in relationship between features and label | Monitor for freshness degradation | #8 |
| **Distribution** | Frequency and range of values for a feature | KS test compares train vs serve distributions | #37 |
| **Metric** | A number that you care about | AUC, accuracy, precision, recall, latency_ms | #2 |
| **Label** | Answer portion of a training example | `resonance_score` (0.0–1.0) | #13 |
| **Example** | One row of features and possibly a label | One MLAOS memory node session | #5 |
| **Instance** | The thing you want to make a prediction about | One MLAOS memory node, electrode, or session | #5 |
| **Unlabeled Example** | Example with features but no label | Used during inference | #29 |
| **Ground Truth** | The thing that actually happened | Actual user engagement vs predicted | #9 |
| **Hyperparameter** | Variables adjusted during training runs | Learning rate=0.003, batch size=100 | #21 |
| **Overfitting** | Model too closely matches training data | Avoided with L1/L2 regularization | #9 |
| **Generalization** | Model's ability to predict on unseen data | Test on held-out temporal data | #33 |
| **AUC** | Area under ROC curve (0.0–1.0) | Primary classification metric; target >0.70 | #9 |
| **Loss** | Measure of prediction error during training | L2 loss for regression; target <0.1 | #9 |
| **Pipeline** | Infrastructure surrounding an ML algorithm | data → training → serving → monitoring | #4 |
| **Ablation** | Evaluating feature importance by removal | Evaluate `resonance_score`, `chiaroscuro_index` | #22 |
| **Feature Column** | Set of related features (Google terminology) | Tracked in `feature_registry` with owner | #11 |
| **Embedding** | Lower-dimensional vector space representation | Phase III: narrative text embeddings | #41 |
| **Feedback Loop** | Model predictions influence future training data | Avoid with positional features | #36 |

---

## Key MLAOS Features

| Feature Name | Type | Description | Owner |
|---|---|---|---|
| `resonance_score` | Continuous | Normalized resonance signal (0.0–1.0) | kennydallmier@gmail.com |
| `impedance_magnitude` | Continuous | EIS impedance in Ohms | kennydallmier@gmail.com |
| `hrv_score` | Continuous | Heart rate variability in ms | kennydallmier@gmail.com |
| `chiaroscuro_index` | Continuous (Synthetic) | abs(light-dark)/(light+dark) | kennydallmier@gmail.com |
| `sigma7_alignment` | Continuous | Cosine similarity: sigma7 identity vs memory | kennydallmier@gmail.com |

---

**Last Updated:** March 2026
**Maintainer:** Kenneth Dallmier (kennydallmier@gmail.com)

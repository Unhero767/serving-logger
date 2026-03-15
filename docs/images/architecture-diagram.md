# MLAOS Infrastructure Architecture Diagram

> **Note:** Replace this file with the actual `architecture-diagram.png` image.
> Export from your diagramming tool (Mermaid, draw.io, Lucidchart) and commit as PNG.
> Filename must be: `docs/images/architecture-diagram.png`

---

## Architecture Overview (Text Description)

The MLAOS Serving Logger infrastructure consists of the following components:

```
+---------------------------+
|    MLAOS Inference Layer  |
|  (Online Prediction API)  |
+------------+--------------+
             |
             v
+---------------------------+     +---------------------------+
|      FeatureExtractor     |---->|      Prediction Model     |
|   (src/mlaos_features/)  |     |     (AURELIA-v2.3)        |
|   Rule #32: Shared Code  |     +---------------------------+
+------------+--------------+
             |
             | features_dict (exact values)
             v
+---------------------------+
|      ServingLogger        |
|   (src/mlaos_infra/)     |     +---------------------------+
|   Rule #29: Log features  |---->|    PostgreSQL DB          |
|   Rule #10: Fail silent   |     |    serving_logs table     |
+---------------------------+     +---------------------------+
                                              |
                                             (weekly)
                                              v
+---------------------------+     +---------------------------+
|      SkewAuditor          |<----|   Training Data Baseline  |
|   Rule #37: Measure skew  |     |   (feature distributions) |
|   KS test, p < 0.05       |     +---------------------------+
+------------+--------------+
             |
             v
+---------------------------+
|   audits/run_audit.py     |
|   JSON report output      |
|   CI/CD exit code 1       |
|   if skew detected        |
+---------------------------+
```

## Data Flow

1. Raw sensor data enters `FeatureExtractor.extract_features()`
2. Feature vector is passed to both the model AND `ServingLogger.log_inference()`
3. `ServingLogger` writes each feature to `serving_logs` table (Rule #29)
4. Weekly: `run_audit.py` compares serving distribution vs. training baseline
5. `SkewAuditor.run_audit()` runs KS test on each feature (Rule #37)
6. Alert triggered if `p < 0.05`; CI exits with code 1

## Component Ownership

| Component | File | Owner | Rule |
|-----------|------|-------|------|
| FeatureExtractor | `src/mlaos_features/feature_extractor.py` | kennydallmier@gmail.com | #11, #32 |
| ServingLogger | `src/mlaos_infra/serving_logger.py` | kennydallmier@gmail.com | #29, #10 |
| SkewAuditor | `src/mlaos_infra/skew_auditor.py` | kennydallmier@gmail.com | #37 |
| Audit Runner | `audits/run_audit.py` | kennydallmier@gmail.com | #5, #37 |
| SQL Schema | `sql/schema.sql` | kennydallmier@gmail.com | #29 |

---

*To replace with PNG: `git add docs/images/architecture-diagram.png && git commit`*

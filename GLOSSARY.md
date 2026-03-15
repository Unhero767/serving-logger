# MLAOS Project Glossary

## Overview

This glossary integrates **Google's Machine Learning Glossary** with **MLAOS-specific definitions** and **Rules of Machine Learning** references. This ensures consistent terminology across the project and aligns with industry best practices.

**Sources:**
- [Google ML Glossary](https://developers.google.com/machine-learning/glossary)
- [Google Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- MLAOS Project Documentation

---

## A

### **Ablation**
**Google Definition:** A technique for evaluating the importance of a feature or component by temporarily removing it from a model.

**MLAOS Context:** Used to evaluate importance of `resonance_score`, `chiaroscuro_index`, and `sigma7_alignment` features.

**Related Rules:** Rule #22 (Clean up features you are no longer using)

---

### **Accuracy**
**Google Definition:** The number of correct classification predictions divided by the total number of predictions.

**MLAOS Context:** Not primary metric for MLAOS (regression task). Use AUC instead for classification subtasks.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

### **AUC (Area under the ROC curve)**
**Google Definition:** A number between 0.0 and 1.0 representing a binary classification model's ability to separate positive classes from negative classes.

**MLAOS Context:** Primary metric for sanity checks before model export (Rule #9). Target: AUC > 0.70.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

## B

### **Batch**
**Google Definition:** The set of examples used in one training iteration.

**MLAOS Context:** Batch size = 100 for MLAOS training. Mini-batch strategy for efficiency.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Batch Inference**
**Google Definition:** The process of inferring predictions on multiple unlabeled examples divided into smaller subsets.

**MLAOS Context:** Used for pre-computed resonance scores. Contrast with online inference for real-time predictions.

**Related Rules:** Rule #4 (Keep the first model simple and get the infrastructure right)

---

## C

### **Categorical Data**
**Google Definition:** Features having a specific set of possible values.

**MLAOS Context:** `status` field in feature_registry: ACTIVE, EXPERIMENTAL, DEPRECATED.

**Related Rules:** Rule #11 (Give feature columns owners and documentation)

---

### **Checkpoint**
**Google Definition:** Data that captures the state of a model's parameters either during training or after training is completed.

**MLAOS Context:** Saved every 1000 iterations for training continuity.

**Related Rules:** Rule #5 (Test the infrastructure independently from the machine learning)

---

### **Classification Model**
**Google Definition:** A model whose prediction is a class.

**MLAOS Context:** Used for spam filtering (Rule #15). Contrast with regression model for resonance scores.

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **Concept Drift**
**Google Definition:** A shift in the relationship between features and the label. Over time, concept drift reduces a model's quality.

**MLAOS Context:** Monitor for freshness degradation. Weekly retraining if drift detected.

**Related Rules:** Rule #8 (Know the freshness requirements of your system)

---

### **Continuous Feature**
**Google Definition:** A floating-point feature with an infinite range of possible values.

**MLAOS Context:** `resonance_score` (0.0-1.0), `impedance_magnitude` (Ohms), `hrv_score` (ms).

**Related Rules:** Rule #17 (Start with directly observed and reported features)

---

### **Convergence**
**Google Definition:** A state reached when loss values change very little or not at all with each iteration.

**MLAOS Context:** Target: Loss stable after 700 iterations. Early stopping if validation loss increases.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---
## D

### **Decision Boundary**
**Google Definition:** The separator between classes learned by a model in a binary class or multi-class classification problems.

**MLAOS Context:** Used for spam filtering (Rule #15). Not used for quality ranking (regression).

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **Discrete Feature**
**Google Definition:** A feature with a finite set of possible values.

**MLAOS Context:** `status`: ACTIVE, EXPERIMENTAL, DEPRECATED. `feature_type`: NUMERIC, CATEGORICAL, EMBEDDING.

**Related Rules:** Rule #11 (Give feature columns owners and documentation)

---

### **Distribution**
**Google Definition:** The frequency and range of different values for a given feature or label.

**MLAOS Context:** Monitor feature distributions for skew detection (Rule #37). Target: KS stat < 0.1.

**Related Rules:** Rule #37 (Measure Training/Serving Skew)

---

### **Downsampling**
**Google Definition:** Reducing the amount of information in a feature in order to train a model more efficiently.

**MLAOS Context:** Used for class-imbalanced datasets (e.g., spam filtering).

**Related Rules:** Rule #34 (In binary classification for filtering, make small short-term sacrifices)

---

## E

### **Embedding**
**Google Definition:** Lower-dimensional vector space for high-dimensional features.

**MLAOS Context:** Phase III: Deep learning embeddings for narrative text (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Embedding Layer**
**Google Definition:** A special hidden layer that trains on a high-dimensional categorical feature to gradually learn a lower dimension embedding vector.

**MLAOS Context:** Phase III: 73K tree species → 12 dimensions (example from Google glossary).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Embedding Vector**
**Google Definition:** An array of floating-point numbers taken from any hidden layer that describe the inputs to that hidden layer.

**MLAOS Context:** Phase III: Narrative text embeddings for symbolic systems.

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Embedding Space**
**Google Definition:** The d-dimensional vector space that features from a higher-dimensional vector space are mapped to.

**MLAOS Context:** Phase III: Symbolic systems mapped to 12-dimensional space.

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Epoch**
**Google Definition:** A full training pass over the entire training set such that each example has been processed once.

**MLAOS Context:** 1 epoch = 20 iterations (1000 examples / 50 batch size).

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Example**
**Google Definition:** The values of one row of features and possibly a label.

**MLAOS Context:** One MLAOS memory node session with features (`resonance_score`, `chiaroscuro_index`) and label (user engagement).

**Related Rules:** Rule #5 (Test the infrastructure independently from the machine learning)

---

### **Experimenter's Bias**
**Google Definition:** A form of confirmation bias in which an experimenter continues training models until a pre-existing hypothesis is confirmed.

**MLAOS Context:** Avoid by using held-out test data (Rule #33).

**Related Rules:** Rule #23 (You are not a typical end user)

---

## F

### **False Negative (FN)**
**Google Definition:** An example in which the model mistakenly predicts the negative class.

**MLAOS Context:** Spam not detected (Rule #15). Monitor false negative rate for spam filtering.

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **False Positive (FP)**
**Google Definition:** An example in which the model mistakenly predicts the positive class.

**MLAOS Context:** Legitimate content flagged as spam (Rule #15). Monitor false positive rate for quality ranking.

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **Feature**
**Google Definition:** An input variable to a machine learning model.

**MLAOS Context:** `resonance_score`, `impedance_magnitude`, `hrv_score`, `chiaroscuro_index`, `sigma7_alignment`.

**Related Rules:** Rule #11 (Give feature columns owners and documentation)

---

### **Feature Column**
**Google Definition:** A set of related features (Google-specific terminology).

**MLAOS Context:** Set of all possible `resonance_score` values. Tracked in feature_registry with owner.

**Related Rules:** Rule #11 (Give feature columns owners and documentation)

---

### **Feature Cross**
**Google Definition:** A synthetic feature formed by "crossing" categorical or bucketed features.

**MLAOS Context:** Phase II: Cross `temperature_bucket × wind_speed_bucket` for physiological signals.

**Related Rules:** Rule #20 (Combine and modify existing features to create new features)

---

### **Feature Engineering**
**Google Definition:** A process that involves determining which features might be useful and converting raw data into efficient versions of those features.

**MLAOS Context:** `FeatureExtractor` module creates synthetic features (`chiaroscuro_index` from light/dark).

**Related Rules:** Rule #16 (Plan to launch and iterate)

---

### **Feature Extraction**
**Google Definition:** Retrieving intermediate feature representations calculated by an unsupervised or pre-trained model.

**MLAOS Context:** `FeatureExtractor` module (Rule #32: shared for training and serving).

**Related Rules:** Rule #32 (Re-use code between training and serving)

---

### **Feature Vector**
**Google Definition:** The array of feature values comprising an example.

**MLAOS Context:** Input to `FeatureExtractor` for train/serve. Example: `[0.85, 0.42, 0.75]`.

**Related Rules:** Rule #32 (Re-use code between training and serving)

---

### **Feedback Loop**
**Google Definition:** A situation in which a model's predictions influence the training data for the same model or another model.

**MLAOS Context:** Avoid with positional features (Rule #36). Model position effects during training, neutralize at serving.

**Related Rules:** Rule #36 (Avoid feedback loops with positional features)

---

### **Fine-Tuning**
**Google Definition:** A second, task-specific training pass performed on a pre-trained model to refine its parameters for a specific use case.

**MLAOS Context:** Phase III: Fine-tune foundation model for neuro-cognitive tasks (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Foundation Model**
**Google Definition:** A very large pre-trained model trained on an enormous and diverse training set.

**MLAOS Context:** Phase III: Deep learning foundation model for narrative generation (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---
## G

### **Generalization**
**Google Definition:** A model's ability to make correct predictions on new, previously unseen data.

**MLAOS Context:** Test on held-out temporal data (Rule #33). Target: Performance degradation <5%.

**Related Rules:** Rule #33 (Test on future data)

---

### **Generalization Curve**
**Google Definition:** A plot of both training loss and validation loss as a function of the number of iterations.

**MLAOS Context:** Monitor for overfitting. Target: Validation loss close to training loss.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

### **Gradient Descent**
**Google Definition:** A mathematical technique to minimize loss. Gradient descent iteratively adjusts weights and biases.

**MLAOS Context:** Optimizer for MLAOS training. Learning rate = 0.003 (hyperparameter).

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Ground Truth**
**Google Definition:** Reality. The thing that actually happened.

**MLAOS Context:** Actual user engagement vs. predicted engagement. Used for evaluation.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

## H

### **Hidden Layer**
**Google Definition:** A layer in a neural network between the input layer (the features) and the output layer (the prediction).

**MLAOS Context:** Phase III: Deep model with 2+ hidden layers (Rule #41). Phase I: Linear model (no hidden layers).

**Related Rules:** Rule #4 (Keep the first model simple)

---

### **Holdout Data**
**Google Definition:** Examples intentionally not used ("held out") during training.

**MLAOS Context:** Validation dataset and test dataset. Rule #33: Test on data after training period.

**Related Rules:** Rule #33 (Test on future data)

---

### **Hyperparameter**
**Google Definition:** The variables that you or a hyperparameter tuning service adjust during successive runs of training a model.

**MLAOS Context:** Learning rate = 0.003, batch size = 100, regularization rate = 0.1.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

## I

### **Imbalanced Dataset**
**Google Definition:** A dataset for a classification in which the total number of labels of each class differs significantly.

**MLAOS Context:** Spam filtering (Rule #34). 99% negative, 1% positive. Use downsampling/upsampling.

**Related Rules:** Rule #34 (In binary classification for filtering, make small short-term sacrifices)

---

### **Inference**
**Google Definition:** Making predictions by applying a trained model to unlabeled examples.

**MLAOS Context:** Online inference for real-time MLAOS cognitive predictions. Batch inference for pre-computed scores.

**Related Rules:** Rule #29 (Log features at serving time)

---

### **Instance**
**Google Definition:** The thing about which you want to make a prediction.

**MLAOS Context:** One MLAOS memory node, electrode, or user session.

**Related Rules:** Rule #5 (Test the infrastructure independently from the machine learning)

---

### **Interpretability**
**Google Definition:** The ability to explain or to present an ML model's reasoning in understandable terms to a human.

**MLAOS Context:** Phase I: Linear/logistic regression (high interpretability). Phase III: Deep models (low interpretability).

**Related Rules:** Rule #14 (Starting with an interpretable model makes debugging easier)

---

### **Iteration**
**Google Definition:** A single update of a model's parameters during training.

**MLAOS Context:** 1 iteration = 1 forward pass + 1 backward pass. 20 iterations per epoch.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

## L

### **Label**
**Google Definition:** In supervised machine learning, the "answer" or "result" portion of an example.

**MLAOS Context:** `resonance_score` (0.0-1.0), user engagement (clicks, time spent).

**Related Rules:** Rule #13 (Choose a simple, observable and attributable metric)

---

### **Labeled Example**
**Google Definition:** An example that contains one or more features and a label.

**MLAOS Context:** Used during training. Example: Features + `resonance_score` label.

**Related Rules:** Rule #5 (Test the infrastructure independently from the machine learning)

---

### **Learning Rate**
**Google Definition:** A floating-point number that tells the gradient descent algorithm how strongly to adjust weights and biases on each iteration.

**MLAOS Context:** Learning rate = 0.003. Hyperparameter tuned during training.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Linear Model**
**Google Definition:** A model that assigns one weight per feature to make predictions.

**MLAOS Context:** Phase I: Linear regression for baseline (Rule #4). Easy to debug and interpret.

**Related Rules:** Rule #4 (Keep the first model simple)

---

### **Log Loss**
**Google Definition:** The loss function used in binary logistic regression.

**MLAOS Context:** Loss function for classification subtasks (spam filtering).

**Related Rules:** Rule #14 (Starting with an interpretable model makes debugging easier)

---

### **Loss**
**Google Definition:** During the training of a supervised model, a measure of how far a model's prediction is from its label.

**MLAOS Context:** L2 loss for regression tasks. Target: Loss < 0.1 before export.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

### **Loss Curve**
**Google Definition:** A plot of loss as a function of the number of training iterations.

**MLAOS Context:** Monitor for convergence. Target: Flat slope after 700 iterations.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---
## M

### **Machine Learning**
**Google Definition:** A program or system that trains a model from input data.

**MLAOS Context:** MLAOS Engine: Computational Mythology + Neuroprosthetics + ML Infrastructure.

**Related Rules:** Rule #1 (Don't be afraid to launch a product without machine learning)

---

### **Metric**
**Google Definition:** A number that you care about. May or may not be directly optimized.

**MLAOS Context:** AUC, accuracy, precision, recall, feature coverage, logging completeness.

**Related Rules:** Rule #2 (First, design and implement metrics)

---

### **Model**
**Google Definition:** A statistical representation of a prediction task.

**MLAOS Context:** MLAOS neuro-cognitive prediction model. Version tracked for skew detection.

**Related Rules:** Rule #4 (Keep the first model simple)

---

### **Model Capacity**
**Google Definition:** The complexity of problems that a model can learn.

**MLAOS Context:** Phase I: Low capacity (linear). Phase III: High capacity (deep learning).

**Related Rules:** Rule #4 (Keep the first model simple)

---

### **Multi-Class Classification**
**Google Definition:** A classification problem in which the dataset contains more than two classes of labels.

**MLAOS Context:** Phase III: Multi-class narrative classification (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

## N

### **Neural Network**
**Google Definition:** A model containing at least one hidden layer.

**MLAOS Context:** Phase III: Deep neural network for narrative generation (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Nonstationarity**
**Google Definition:** A feature whose values change across one or more dimensions, usually time.

**MLAOS Context:** Monitor for freshness degradation. Weekly retraining if nonstationarity detected.

**Related Rules:** Rule #8 (Know the freshness requirements of your system)

---

### **Normalization**
**Google Definition:** The process of converting a variable's actual range of values into a standard range of values.

**MLAOS Context:** Z-score normalization for numerical features. Target: Range -1 to +1.

**Related Rules:** Rule #32 (Re-use code between training and serving)

---

### **Numerical Data**
**Google Definition:** Features represented as integers or real-valued numbers.

**MLAOS Context:** `resonance_score`, `impedance_magnitude`, `hrv_score`.

**Related Rules:** Rule #17 (Start with directly observed and reported features)

---

## O

### **Objective**
**Google Definition:** A metric that your algorithm is trying to optimize.

**MLAOS Context:** Resonance score prediction (regression). Contrast with metrics (AUC, accuracy).

**Related Rules:** Rule #13 (Choose a simple, observable and attributable metric)

---

### **Offline Inference**
**Google Definition:** The process of a model generating a batch of predictions and then caching those predictions.

**MLAOS Context:** Pre-computed resonance scores. Contrast with online inference.

**Related Rules:** Rule #4 (Keep the first model simple)

---

### **Online Inference**
**Google Definition:** Generating predictions on demand.

**MLAOS Context:** Real-time MLAOS cognitive predictions. Log features at serving time (Rule #29).

**Related Rules:** Rule #29 (Log features at serving time)

---

### **Overfitting**
**Google Definition:** Creating a model that matches the training data so closely that the model fails to make correct predictions on new data.

**MLAOS Context:** Avoid with regularization (L1, L2). Target: Validation loss close to training loss.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

## P

### **Parameter**
**Google Definition:** The weights and biases that a model learns during training.

**MLAOS Context:** Model weights learned during training. Contrast with hyperparameters.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Pipeline**
**Google Definition:** The infrastructure surrounding a machine learning algorithm.

**MLAOS Context:** MLAOS end-to-end infrastructure: data → training → serving → monitoring.

**Related Rules:** Rule #4 (Keep the first model simple and get the infrastructure right)

---

### **Precision**
**Google Definition:** When the model predicted the positive class, what percentage of the predictions were correct?

**MLAOS Context:** Spam filtering precision (Rule #15). Target: Precision > 0.90.

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **Prediction**
**Google Definition:** A model's output.

**MLAOS Context:** Predicted `resonance_score` (0.0-1.0). Compare with ground truth for evaluation.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

### **Preprocessing**
**Google Definition:** Processing data before it's used to train a model.

**MLAOS Context:** Normalization, feature extraction, data cleaning. Shared code for training and serving (Rule #32).

**Related Rules:** Rule #32 (Re-use code between training and serving)

---

### **Pre-trained Model**
**Google Definition:** A trained large language model or other form of trained generative AI model.

**MLAOS Context:** Phase III: Fine-tune pre-trained model for neuro-cognitive tasks (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

## R

### **Recall**
**Google Definition:** When ground truth was the positive class, what percentage of predictions did the model correctly identify as the positive class?

**MLAOS Context:** Spam filtering recall (Rule #15). Target: Recall > 0.85.

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **Regression Model**
**Google Definition:** A model that generates a numerical prediction.

**MLAOS Context:** Primary model type for `resonance_score` prediction (0.0-1.0).

**Related Rules:** Rule #14 (Starting with an interpretable model makes debugging easier)

---

### **Regularization**
**Google Definition:** Any mechanism that reduces overfitting.

**MLAOS Context:** L1, L2 regularization. Target: Reduce overfitting without reducing predictive power.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Reinforcement Learning**
**Google Definition:** A family of algorithms that learn an optimal policy, whose goal is to maximize return when interacting with an environment.

**MLAOS Context:** Phase III: Reinforcement learning for narrative optimization (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---
### **Rule #11**
**Google Definition:** Give feature columns owners and documentation.

**MLAOS Context:** Feature Registry with `owner_email`, `backup_owner_email`, `description`, `expected_coverage_pct`.

**Related Glossary:** feature, feature column, feature engineering

---

### **Rule #22**
**Google Definition:** Clean up features you are no longer using.

**MLAOS Context:** Weekly automated pruning. Remove unused features to reduce technical debt.

**Related Glossary:** feature, feature engineering, technical debt

---

### **Rule #29**
**Google Definition:** Log features at serving time.

**MLAOS Context:** `ServingLogger` captures exact feature values at inference. Enables skew detection.

**Related Glossary:** serving, inference, feature, training-serving skew

---

### **Rule #32**
**Google Definition:** Re-use code between training and serving.

**MLAOS Context:** `FeatureExtractor` module shared for training and serving. Eliminates preprocessing drift.

**Related Glossary:** training, serving, feature extraction, preprocessing

---

### **Rule #37**
**Google Definition:** Measure training/serving skew.

**MLAOS Context:** Weekly skew audits (KS test, p<0.05). Target: KS stat < 0.1.

**Related Glossary:** training-serving skew, training set, test set, generalization

---

## S

### **Serving**
**Google Definition:** The process of making a trained model available to provide predictions.

**MLAOS Context:** Online inference for real-time MLAOS predictions. Log features at serving time (Rule #29).

**Related Rules:** Rule #29 (Log features at serving time)

---

### **Silent Failure**
**Google Definition:** A problem that occurs more for machine learning systems than for other kinds of systems (stale tables, gradual decay).

**MLAOS Context:** Monitor for stale tables, feature coverage drops. Alert within 1 hour (Rule #10).

**Related Rules:** Rule #10 (Watch for silent failures)

---

### **Sparse Feature**
**Google Definition:** A feature whose values are predominately zero or empty.

**MLAOS Context:** One-hot encoded categorical features. Use embedding layer for efficiency (Phase III).

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

### **Synthetic Feature**
**Google Definition:** A feature not present among the input features, but assembled from one or more of them.

**MLAOS Context:** `chiaroscuro_index` from light/dark intensity. `feature_cross` from temperature/wind.

**Related Rules:** Rule #20 (Combine and modify existing features to create new features)

---

## T

### **Test Set**
**Google Definition:** A subset of the dataset reserved for testing a trained model.

**MLAOS Context:** Data from January 6th and after (Rule #33). Target: Performance degradation <5%.

**Related Rules:** Rule #33 (Test on future data)

---

### **Token**
**Google Definition:** The atomic unit that the model is training on and making predictions on.

**MLAOS Context:** Phase III: Narrative text tokens for deep learning (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

### **Training**
**Google Definition:** The process of determining the ideal parameters comprising a model.

**MLAOS Context:** Determine ideal weights for MLAOS model. Use labeled examples.

**Related Rules:** Rule #4 (Keep the first model simple)

---

### **Training Serving Skew**
**Google Definition:** The difference between a model's performance during training and that same model's performance during serving.

**MLAOS Context:** Weekly skew audits (Rule #37). Target: KS stat < 0.1.

**Related Rules:** Rule #37 (Measure Training/Serving Skew)

---

### **Training Set**
**Google Definition:** The subset of the dataset used to train a model.

**MLAOS Context:** Data until January 5th (Rule #33). Contrast with test set.

**Related Rules:** Rule #33 (Test on future data)

---

### **Transfer Learning**
**Google Definition:** Transferring information from one machine learning task to another.

**MLAOS Context:** Phase III: Transfer learning from foundation model (Rule #41, #43).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information), Rule #43 (Friends transfer across products; interests don't)

---

### **True Negative (TN)**
**Google Definition:** An example in which the model correctly predicts the negative class.

**MLAOS Context:** Legitimate content correctly not flagged as spam (Rule #15).

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

### **True Positive (TP)**
**Google Definition:** An example in which the model correctly predicts the positive class.

**MLAOS Context:** Spam correctly detected (Rule #15).

**Related Rules:** Rule #15 (Separate Spam Filtering and Quality Ranking)

---

## U

### **Unlabeled Example**
**Google Definition:** An example that contains features but no label.

**MLAOS Context:** Used during inference. Features without `resonance_score` label.

**Related Rules:** Rule #29 (Log features at serving time)

---

### **Unsupervised Machine Learning**
**Google Definition:** Training a model to find patterns in a dataset, typically an unlabeled dataset.

**MLAOS Context:** Phase III: Clustering for symbolic systems (Rule #41).

**Related Rules:** Rule #41 (When performance plateaus, look for qualitatively new sources of information)

---

## V

### **Validation Set**
**Google Definition:** The subset of the dataset that performs initial evaluation against a trained model.

**MLAOS Context:** Held-out data for initial evaluation. Contrast with test set.

**Related Rules:** Rule #9 (Detect problems before exporting models)

---

### **Vector**
**Google Definition:** In machine learning, a vector holds floating-point numbers with a specific length/dimension.

**MLAOS Context:** Feature vector: `[0.85, 0.42, 0.75]`. Embedding vector: 12 dimensions (Phase III).

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

## W

### **Weight**
**Google Definition:** A value that a model multiplies by another value.

**MLAOS Context:** Model weights learned during training. Regularization drives irrelevant weights to 0.

**Related Rules:** Rule #21 (Number of feature weights proportional to data volume)

---

## Z

### **Z-Score Normalization**
**Google Definition:** A scaling technique that replaces a raw feature value with a floating-point value representing the number of standard deviations from that feature's mean.

**MLAOS Context:** Normalization for numerical features. Target: Range -3 to +3.

**Related Rules:** Rule #32 (Re-use code between training and serving)

---
## Index by Rule Number

| Rule # | Rule Name | Related Glossary Terms |
|--------|-----------|----------------------|
| #1 | Don't launch without ML | machine learning, heuristic |
| #2 | Design metrics first | metric, objective |
| #4 | Simple model, right infrastructure | model, pipeline, infrastructure |
| #5 | Test infrastructure independently | instance, example, labeled example |
| #8 | Know freshness requirements | concept drift, nonstationarity, freshness |
| #9 | Detect problems before export | AUC, convergence, loss curve, validation set |
| #10 | Watch for silent failures | silent failure, metric, coverage |
| #11 | Feature columns owners | feature, feature column, feature engineering, categorical data, discrete feature |
| #13 | Simple, observable objective | objective, label, metric |
| #14 | Interpretable model first | interpretability, linear model, logistic regression |
| #15 | Separate spam from quality | classification model, decision boundary, false positive, false negative, precision, recall |
| #16 | Plan to launch & iterate | feature engineering, iteration, launch |
| #17 | Start with observed features | continuous feature, numerical data, feature |
| #20 | Combine features intuitively | feature cross, synthetic feature, feature engineering |
| #21 | Feature weights ∝ data volume | batch, epoch, hyperparameter, parameter, weight, regularization |
| #22 | Clean up unused features | ablation, feature, technical debt |
| #23 | You ≠ typical user | experimenter's bias, end user |
| #29 | Log features at serving time | serving, inference, feature, feature vector, example |
| #32 | Re-use code train/serve | training, serving, feature extraction, preprocessing, normalization |
| #33 | Test on future data | test set, training set, holdout data, generalization |
| #34 | Clean data for filtering | imbalanced dataset, downsampling, filtering |
| #36 | Avoid positional feedback loops | feedback loop, position, feature |
| #37 | Measure training/serving skew | training-serving skew, distribution, KS test, generalization curve |
| #38 | Don't waste time if objectives unaligned | objective, metric, product goals |
| #39 | Launch decisions = long-term proxy | metric, objective, launch, proxy |
| #40 | Keep ensembles simple | ensemble, model, base model |
| #41 | Seek qualitatively new data | embedding, embedding layer, embedding vector, foundation model, fine-tuning, transfer learning, neural network, token |
| #43 | Friends transfer; interests don't | transfer learning, personalization, feature |

---

## How to Use This Glossary

1. **API Documentation:** Reference glossary terms in API docs (see `docs/API_DOCUMENTATION.md`)
2. **Code Comments:** Link glossary terms to Rules in code (see `src/` modules)
3. **Onboarding:** Use for new team member onboarding
4. **Grant Applications:** Use for NIH BRAIN Initiative consistency
5. **Interviews:** Use for technical interview preparation

---

**Last Updated:** March 2026  
**Maintainer:** Kenneth Dallmier (kennydallmier@gmail.com)  
**GitHub:** [https://github.com/Herounhero](https://github.com/Herounhero)

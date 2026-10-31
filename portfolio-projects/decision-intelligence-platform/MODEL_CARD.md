# Model card

**Purpose:** demonstrate retrieval/ranking and heterogeneous treatment estimation without personal data.

**Ranking model:** `sklearn.ensemble.HistGradientBoostingClassifier`; five user-item features; positive next-click versus sampled negatives. Temporal leave-last-one-out per user, disjoint train/test user sets, synthetic training population.

**Experiment model:** RandomForestClassifier T-learner, one model per randomized arm. Pre-treatment synthetic features (age, previous orders, interest), separate 70/30 holdout split. Primary estimand: treatment-control average conversion difference (ATE) in a randomized sample; uplift model is a secondary exploratory estimator.

**Metrics:** ranking HitRate@10, NDCG@10 against popularity baseline; randomized ATE/95% interval/p-value; synthetic simulator-only uplift MAE. See `CASE_STUDY.md` and regenerate metrics with `PYTHONPATH=. python -m scripts.train`.

**Intended use:** education, interviews, synthetic demos, portfolio evaluation. **Out of scope:** financial decisions, sensitive targeting, real marketing optimization, production recommendations, and estimates on external datasets without validation.

**Known limitations:** sample-size uncertainty, synthetic preferences, sampled negative labels, possible exposure bias, finite holdout, calibration and distribution shift not independently audited, and strong assumptions for causal estimation with non-random treatment. No protected demographic fairness audit; the synthetic generator does not contain meaningful real-world group representations.

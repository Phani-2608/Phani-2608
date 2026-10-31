# Personalized Decision Intelligence & ML Experimentation Platform

A **runnable, reproducible** end-to-end portfolio prototype combining a learned personalized recommendation ranking model, a popularity baseline, leakage-safe offline evaluation, randomized A/B test analysis and a heterogeneous uplift T-learner. All data are **synthetic**; no marketing performance claims should be inferred from the results.

## Quick start

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m scripts.train
uvicorn backend.api:app --reload --port 8001
# Visit http://127.0.0.1:8001
```

A cached model artifact is generated locally. `joblib`/pickle artifacts should **never** be loaded from untrusted sources. If no model file is available, the server builds deterministic demo models on startup.

## Docker

```bash
docker build -t decision-intelligence .
docker run --rm -p 127.0.0.1:8001:8001 decision-intelligence
```

## How it works

**Recommendation:** A synthetic clickstream includes per-user category preference and item attractiveness. For each user we keep their final chronologically last click as holdout; a disjoint subset of users trains a HistGradientBoosting relevance classifier on positive next-item candidates and sampled negatives. For test users, only their *past* interactions contribute to user features. Popularity features derive from training-user histories only. Evaluate learned ranking vs popularity using HitRate@10 and NDCG@10. Cold-start users fall back to popularity. This is an offline learning-to-rank approximation, not a personalized production recommender.

**Experiments:** Generate a separately randomized synthetic experiment with known treatment heterogeneity. Estimate average treatment effect with a difference in sample means, Welch standard error, normal-approximation confidence interval, and p-value. Train treated/control random forests on a training subset and measure predicted uplift against synthetic known individual uplift on a disjoint test set. The known unit-level effect exists **only in simulation**. Observed segment comparisons are exploratory and noisy.

## Evaluation

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python -m scripts.train
```

The dashboard and `/metrics`, `/recommend/{user_id}`, `/uplift` endpoints return only synthetic data. The platform does not ingest PII or issue automated marketing actions.

## Future real datasets and production work

- Dataset adapters for independently sourced RetailRocket (ranking) and Hillstrom (randomized email experiment), after checking their licensing and schemas. Never join these unrelated customer populations.
- Exposure-bias / negative-sampling diagnostics, time-forward global split, hyperparameter tuning and cold-start evaluation.
- Proper causal uplift evaluation (Qini/AUUC/policy value with uncertainty), doubly robust estimates and propensity diagnostics where appropriate.
- MLflow tracking, batch feature pipelines, drift monitoring, secured service auth, real deployment and CI benchmarks.

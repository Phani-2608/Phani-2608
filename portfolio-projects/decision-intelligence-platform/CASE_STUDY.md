# Case study: Personalized ranking and randomized experimentation

## Questions

1. Can past customer interactions improve the ranking of candidate products over a popularity-only baseline?
2. Which marketing interventions cause incremental conversions, rather than merely correlate with conversion propensity?

These are demonstrated using **two separate synthetic datasets**. Their customers must not be joined or described as belonging to one real business.

## Ranking system

A reproducible generator produces users with latent category preference and items with heterogeneous attractiveness. Interactions are ordered by time, and the final unique item interaction for each user is held out. A disjoint group of users is used to train a HistGradientBoostingClassifier on positive holdout candidates and sampled negatives. The test group contributes only its **earlier** interactions to user-level features; item popularity comes only from training-user histories.

Features are category affinity, recent category affinity, normalized item popularity, history length, and last-category match. A cold-start request returns a popularity list. A FastAPI endpoint serves ranked items and a browser dashboard visualizes held-out metrics.

| Metric | Learned ranker | Popularity baseline |
|---|---:|---:|
| HitRate@10 | 0.3636 | 0.2000 |
| NDCG@10 | 0.1323 | 0.1143 |

Values were generated with seed 42 from **synthetic data** and evaluated on **55 synthetic test users**. A test sample this small cannot establish real-world performance.

## Randomized experiment

A **separate** synthetic generator assigns 12,000 records randomly to treatment/control and samples a binary conversion response. Treatment effects vary with prior customer attributes, and simulator-generated counterfactual probabilities provide a diagnostic unavailable in real observed data.

The experiment estimator reports an unadjusted difference in randomized group means, a Welch standard error, normal-approximation 95% confidence interval and p-value. On the held-out 30% sample (3,600 simulated records), the observed difference was **+0.03612** in conversion probability (95% CI **[0.01663, 0.05562]**). This is a property of the **simulator**, not a campaign result.

Treated/control random forests are fit separately on the 70% training sample. The out-of-sample T-learner has an individual-uplift mean absolute error of **0.02012** against the simulator's true probability effect. With real data, individual uplift is unobservable, so this error metric cannot be computed directly.

## Real-data evaluation adapters

The CLI accepts user-supplied **RetailRocket event data** and **Hillstrom's randomized email challenge**. RetailRocket events support ranking experiments; Hillstrom only compares a selected email variant against the randomized no-email group and excludes post-treatment outcomes from features. Raw third-party datasets are not bundled or automatically downloaded. These adapters are tested with small fixture files; the synthetic metrics above do **not** claim results on these datasets.

## Limits / responsible claims

Offline HitRate and NDCG depend on candidate sampling, item exposure and the evaluation population. Randomly sampled negatives differ from real production impressions; causal lift should be evaluated on truly randomized assignments, not non-random marketing data. The dashboard is a read-only portfolio simulation, not an optimization engine for actual customers. Before production: privacy review, data contracts, bias analysis, feature store, monitoring, cross-validation, measured infrastructure costs, and live experiments.

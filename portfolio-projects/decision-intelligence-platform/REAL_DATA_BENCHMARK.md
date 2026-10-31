# Verified real-data benchmark: Hillstrom randomized email experiment

**CI run:** https://github.com/Phani-2608/Phani-2608/actions/runs/41206429413

- Dataset: original MineThatData/Hillstrom 2008 randomized experiment, publicly mirrored; 64,000 rows validated.
- Comparison: Mens E-Mail versus No E-Mail, one treatment arm only.
- Estimation: randomized difference in conversion proportions on a disjoint 30% holdout, normal-approximation 95% CI.
- Held-out rows: **12,784** (6,392 treatment, 6,392 control).
- Treatment conversion: **1.314%**.
- Control conversion: **0.641%**.
- Difference: **+0.673 percentage points**.
- 95% confidence interval: **[+0.332, +1.014] percentage points**.
- Two-sided p-value: **0.00011**.
- Train rows for exploratory T-learner: **29,829**.
- Full results and input SHA-256: **hillstrom-heldout-results** artifact attached to the CI run.

These are measured outcomes from a historical public randomized dataset, **not**
results from this project's demo recommendation app, live experimentation,
or any commercial deployment. Treatment uplift model metrics on real data
have not been independently validated beyond the holdout ATE.

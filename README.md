<h1 align="center">Hi, I'm Phanindra 👋</h1>
<p align="center">I build and ship systems that sit at the intersection of <b>causal inference</b>, <b>applied ML</b>, and <b>production engineering</b>.</p>

---

### 🧠 What I work with

| Area | Tools / Concepts |
|---|---|
| **Causal Inference & Experimentation** | Double Machine Learning, ATE/CATE/ITE estimation, uplift modeling, policy evaluation, fairness auditing |
| **Fraud & Risk Systems** | Point-in-time feature engineering, leakage detection, identity graphs, cost-aligned evaluation, drift vs. decay monitoring |
| **LLM / Agentic Systems** | Multi-agent orchestration, RAG, knowledge graphs, sleep-time / offline compute patterns, grounded/verified LLM outputs |
| **Data Engineering** | Databricks medallion architecture (Bronze/Silver/Gold), idempotent pipelines, data-quality quarantine handling, large-scale EDA |
| **Production ML** | FastAPI services, Streamlit dashboards, Docker/Docker Compose, GitHub Actions CI, pytest test suites, MLflow tracking |
| **Languages** | Python, SQL |

---

### 🔬 Featured work — Case Studies

<br>

#### 🧠 [SleepMind AI](https://github.com/Phani-2608/sleepmind-ai) — Sleep-Time Compute Research Assistant

**Driving question:** *Most RAG systems do all their work at query time. What if the expensive reasoning happened while the system was "asleep," before anyone asked anything?*

**Approach**
- Built four autonomous agents — **Summary, FAQ Generator, Future Query Predictor, Concept Extractor** — that pre-process a document offline, ahead of any user query
- Structured the pre-processed output into a retrieval layer backed by a **knowledge graph**, not just flat vector chunks
- Benchmarked this "sleep-time compute" approach against a traditional RAG baseline on **latency, token usage, and a cost break-even model** to quantify exactly when the offline investment pays for itself
- Tracked every experiment run with **MLflow** rather than comparing numbers by hand

**Engineering & hardening**
- Rebuilt from a single notebook into a modular package (`ingestion / agents / retrieval / knowledge_graph / storage / evaluation / api / dashboard / monitoring`)
- 27 pytest tests, fully mocked so CI runs green with **no API key required**
- The original notebook had a live API key hardcoded and pushed to the repo — the rebuild resolves secrets via environment variables only, with `.env` git-ignored and zero hardcoded secrets anywhere in the new code
- FastAPI service, Streamlit dashboard, Docker + docker-compose, GitHub Actions CI

**What this demonstrates:** agentic system design beyond a single LLM call, quantitative reasoning about the cost/latency tradeoffs of an architecture (not just "does it work"), and treating a security issue as something to fix and document rather than quietly patch.

🔗 [Live API](https://sleepmind-ai-api.onrender.com/docs) · [Live Dashboard](https://sleepmind-ai-dashboard.onrender.com) *(free-tier hosting — first request after idle may take ~30-60s to cold-start)*

<br>

#### 🕵️ [Boomerang](https://github.com/Phani-2608/Boomerang) — Retail Return-Fraud Detection, Built the Right Way

**Driving question:** *A fraud classifier that scores well on paper and does nothing useful in production is the norm, not the exception — usually because of leaked training data, a metric that doesn't match the real use case, or drift nobody's watching. Can a fraud system be built to prove it avoids all three?*

**Building trustworthy synthetic data**
- No public dataset has honest return-fraud labels, so the data itself was generated deliberately to avoid the trap of a model just learning to recover the rule that generated its own labels
- Fraudulent customers also make ordinary returns; a slice of fraud is driven by a factor never present in any feature (capping the ceiling any model can reach); investigator labels are deliberately noisy (~10% of real fraud goes uncaught); realistic mess injected (wrong-sign refunds, clock-skew timestamps, duplicate records, late corrections)

**A pipeline that can't silently lose or duplicate rows**
- Medallion architecture (raw → cleaned → published) with a hard invariant enforced at build time: **rows in = rows published + rows quarantined**, or the pipeline refuses to finish
- Deduplication via business-key merge ordered by source-system assertion time, not arrival time — prevents late corrections from double-counting revenue

**Point-in-time correct features + a relational signal most models miss**
- Every feature is built using only events strictly before the transaction being scored — tested by brute-force recomputation against the fast production version, plus an automated check that flags any feature that predicts the label suspiciously well (a leak signature)
- An **identity graph** links customers via shared devices, addresses, and payment methods — "how much confirmed fraud already exists in this account's cluster" improved every model tried

**Honest model comparison — with a genuine surprise**
| Model | Ranking quality | Fraud $ caught | Net $ saved |
|---|---|---|---|
| Logistic regression (+ graph features) | 0.304 | $2,185 | $937 |
| XGBoost (+ graph features) | 0.301 | $1,663 | $437 |
| Plain logistic regression | 0.266 | $2,293 | **$1,049** |
| Hand-written rule (baseline) | 0.087 | $859 | **-$391** |

Evaluated on a temporal train/test split (never random) and never on accuracy — at this fraud rate a model that predicts nothing is >95% accurate. The model with the best ranking metric (graph-augmented XGBoost) is **not** the one that saves the most money; plain logistic regression wins on net dollars saved by a wide margin. Reporting that mismatch — instead of only the metric that looks best — is the point of building a full model ladder rather than training one model and calling it done.

**From score to action, and knowing when *not* to retrain**
- Cases are ranked by **expected loss** (probability × dollar exposure), not raw probability, so a moderate-risk high-value case outranks a near-certain low-value one
- Net savings peak at ~5% of cases reviewed and turn negative past ~15% — a direct, data-driven answer to "how big should the investigation team be"
- A monitor distinguishes **drift** (the world changing) from **decay** (the model going wrong) — in one run a feature showed heavy drift while performance held steady, and the system correctly recommended watching rather than retraining

**A grounded LLM explainer that cannot make decisions**
- A local LLM turns a case's evidence into a plain-English explanation for investigators — but never decides risk, only narrates evidence it's handed
- Every number the LLM writes is checked against the actual evidence packet; an unverifiable number gets the explanation discarded and replaced with a template — the same fallback used whenever the LLM isn't running, so the system never depends on one being up

**What this demonstrates:** fraud/ML systems thinking that goes past the model — synthetic-data honesty, leakage-proof feature engineering, evaluation aligned to the real cost function, drift-vs-decay monitoring, and constraining an LLM to narration rather than decision-making.

**Engineering:** modular package (`lakehouse / features / ml / ai / serving / monitoring / orchestration`), 34 tests covering leakage checks, data quality, evaluation logic, the API contract, and LLM-explanation grounding — FastAPI service, an operations console, Docker + docker-compose, a parallel Databricks/Spark implementation, and a GitHub Actions pipeline that rebuilds the whole thing from nothing in under a minute. Runs entirely locally, no cloud account required.

🔗 [Data card](https://github.com/Phani-2608/Boomerang/blob/main/docs/DATA_CARD.md) · [Evaluation notes](https://github.com/Phani-2608/Boomerang/blob/main/docs/EVALUATION.md) · [Architecture notes](https://github.com/Phani-2608/Boomerang/blob/main/docs/ARCHITECTURE.md)

<br>

#### 🎯 [Pricing Heterogeneity](https://github.com/Phani-2608/Pricing-heterogeneity) — Causal Inference for Customer Pricing Strategy

**Driving question:** *A price change doesn't affect every customer the same way — how do you estimate that heterogeneity credibly, then act on it without a controlled experiment?*

**Approach**
- Simulated 12,000 customers with a known ground-truth treatment effect, so estimator quality could be checked against reality rather than assumed
- Used cross-fitted **Double Machine Learning (DML)** to separate nuisance-function estimation (outcome and propensity models) from the causal parameter, avoiding regularization bias
- Estimated the full hierarchy: **ATE → CATE → ITE**, then converted individual-level effects into a targeting *policy* rather than stopping at estimation
- Ran a **fairness audit** on the resulting policy rather than assuming a profit-maximizing model is neutral

**Results (verified against the known ground truth)**
| Metric | Value |
|---|---|
| True ATE vs. DR-estimated ATE | 6.0% vs. 7.3% |
| CATE-vs-truth correlation | 0.715 |
| Validation checks passed | 17 / 17 |
| ITE-targeted policy vs. treat-all | **+32.5% profit** |
| Treat-all vs. treat-none | -21.2% profit |
| Fairness audit (disparity ratio) | 0.373 — fails the four-fifths rule, reported openly rather than hidden |

**What this demonstrates:** causal inference beyond correlational ML, honest model evaluation against ground truth, and the willingness to surface a model's fairness failure instead of only reporting the metric that looks good.

**Engineering:** rebuilt from a single notebook into a modular package (`data / sql / features / causal / models / evaluation / optimization / api / dashboard / monitoring`) — 33 pytest tests, FastAPI service, Streamlit dashboard, Docker + docker-compose, GitHub Actions CI (lint + tests + Docker build across Python 3.10/3.11).

🔗 [Live API](https://pricing-heterogeneity-api.onrender.com/docs) · [Live Dashboard](https://pricing-heterogeneity-dashboard.onrender.com) *(free-tier hosting — first request after idle may take ~30-60s to cold-start)*

---

### 📌 A note on how I work
I try to treat every project like something that has to survive contact with production: tests, CI, containerization, and an honest accounting of where a model's assumptions break down — rather than a notebook that only has to run once.

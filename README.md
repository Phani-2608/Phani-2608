<h1 align="center">Hi, I'm Phanindra 👋</h1>
<p align="center">I build and ship systems that sit at the intersection of <b>causal inference</b>, <b>applied ML</b>, and <b>production engineering</b>.</p>

---

### 🧠 Core Expertise

| Area | Depth |
|---|---|
| **Causal Inference & Experimentation** | Double Machine Learning, ATE/CATE/ITE estimation, uplift modeling, policy evaluation, fairness auditing |
| **Fraud & Risk Systems** | Point in time feature engineering, leakage detection, identity graph construction, cost aligned evaluation, drift versus decay monitoring |
| **LLM & Agentic Systems** | Multi agent orchestration, RAG, knowledge graphs, sleep time / offline compute patterns, grounded and verified LLM outputs |
| **Data Engineering** | Medallion architecture (Bronze/Silver/Gold) on Databricks, idempotent pipelines, data quality quarantine handling, large scale EDA |
| **Production ML** | FastAPI services, Streamlit dashboards, Docker / Docker Compose, GitHub Actions CI, pytest suites, MLflow experiment tracking |
| **Languages** | Python, SQL |

---

## 📁 Case Studies

Three systems, each rebuilt from an initial research notebook into a tested, containerized, CI backed production package. Each case study below covers the problem, the technical approach, the engineering behind it, and the measured results.

<br>

## Case Study 1: SleepMind AI
### Sleep Time Compute Research Assistant

**Repository:** [Phani-2608/sleepmind-ai](https://github.com/Phani-2608/sleepmind-ai)
**Live API:** [sleepmind-ai-api.onrender.com/docs](https://sleepmind-ai-api.onrender.com/docs)
**Live Dashboard:** [sleepmind-ai-dashboard.onrender.com](https://sleepmind-ai-dashboard.onrender.com)

#### Overview
SleepMind AI is a research assistant built around a simple but underexplored idea: most retrieval augmented generation (RAG) systems spend all of their compute at query time, when a user is actively waiting on a response. SleepMind instead performs the expensive reasoning offline, before any query arrives, using the interval when the system is otherwise idle.

#### The Problem
Traditional RAG pipelines chunk a document, embed it, and reason over it only once a question is asked. This means every query pays the full cost of retrieval plus generation, and repeated queries against the same document repeat that cost with no compounding benefit. The question driving this project was whether a system could instead do its reasoning ahead of time, amortizing the cost of understanding a document across every future query against it.

#### Technical Approach
Four autonomous agents run against a document as soon as it's ingested, well before any user interacts with it:

- **Summary Agent** produces a structured summary of the document's content
- **FAQ Generator** anticipates likely questions and pre computes answers
- **Future Query Predictor** models what a user is likely to ask next, extending beyond simple FAQ generation
- **Concept Extractor** pulls out the key entities and relationships in the document

The output of these agents feeds a retrieval layer backed by a **knowledge graph** rather than flat vector chunks, so retrieval can follow relationships between concepts, not just semantic similarity between text fragments.

To validate the approach empirically rather than by intuition, this sleep time compute pipeline was benchmarked head to head against a traditional RAG baseline across three dimensions: response latency, token consumption, and a cost break even model that identifies the query volume at which the upfront offline investment starts paying for itself. Every experiment run was tracked in **MLflow**, so comparisons across pipeline versions are reproducible rather than eyeballed.

#### Engineering & Production Readiness
The project was rebuilt from a single research notebook into a modular Python package: `ingestion / agents / retrieval / knowledge_graph / storage / evaluation / api / dashboard / monitoring`. It ships with 27 pytest tests, all fully mocked so the CI suite runs green without requiring a live API key. A FastAPI service exposes the system programmatically, a Streamlit dashboard exposes it interactively, and both are containerized with Docker and Docker Compose behind a GitHub Actions CI pipeline.

One engineering detail worth calling out directly: the original research notebook had a live API key hardcoded and pushed to a public repository. The rebuild treats that as a defect to be fixed and documented, not quietly patched. Secrets are now resolved exclusively through environment variables, `.env` is git ignored, and there are zero hardcoded credentials anywhere in the rebuilt codebase.

#### What This Demonstrates
Agentic system design that goes beyond a single LLM call, quantitative reasoning about the cost and latency tradeoffs of an architecture rather than a qualitative "does it work," and the discipline to treat a security issue found in earlier work as something to fix and document openly.

<br>

## Case Study 2: Boomerang
### Retail Return Fraud Detection, Built the Right Way

**Repository:** [Phani-2608/Boomerang](https://github.com/Phani-2608/Boomerang)
**Documentation:** [Data Card](https://github.com/Phani-2608/Boomerang/blob/main/docs/DATA_CARD.md) · [Evaluation Notes](https://github.com/Phani-2608/Boomerang/blob/main/docs/EVALUATION.md) · [Architecture Notes](https://github.com/Phani-2608/Boomerang/blob/main/docs/ARCHITECTURE.md)

#### Overview
Retail return fraud costs the industry well over a hundred billion dollars a year, and most attempts to catch it start and end with a classifier. Boomerang is a complete system built around a different premise: the classifier is the easy part. What determines whether a fraud model actually works in production is whether the data can be trusted, whether the features are honest, whether the resulting score helps someone do their job, and whether the whole system keeps working once the world underneath it changes.

#### The Problem
Fraud models commonly fail in production for one of three reasons: the training data leaked information from the future into features that shouldn't have had it, the evaluation metric didn't match how the model would actually be used, or nobody built a way to notice when the model started drifting from reality after deployment. Boomerang was built specifically to demonstrate that all three failure modes could be designed around and proven absent, end to end.

#### Technical Approach

**Building trustworthy synthetic data.** No public dataset carries honest return fraud labels, so the training data was generated deliberately rather than conveniently. A simplistic approach (label anyone who returns more than N times a month as fraudulent) would only teach a model to recover the labeling rule itself, producing a suspiciously perfect and practically useless result. Instead: fraudulent customers also make ordinary returns, so fraud is never a clean function of who someone is; a portion of fraud is driven by a factor deliberately excluded from every feature, capping the ceiling any model can reach; investigator labels are intentionally noisy, with roughly 10% of real fraud going uncaught; and realistic operational mess is injected throughout, including wrong sign refunds, clock skew timestamps, duplicate records, and late arriving corrections.

**A pipeline that cannot silently lose or duplicate a row.** Data flows through a medallion architecture: raw events land untouched, a cleaning stage deduplicates and validates them, and a final stage builds the tables every downstream consumer depends on. A hard invariant is enforced before the pipeline is allowed to finish: rows in must equal rows published plus rows quarantined, with every quarantined row carrying a documented reason. Deduplication uses a business key merge ordered by when the source system asserted a version of a record, not by when it happened to arrive, which prevents a late correction from silently double counting revenue.

**Leakage proof, point in time correct features, plus a relational signal most models miss.** Every feature describing a customer's history is built using only events strictly before the return being scored. This is enforced with a test suite that recomputes a sample of features by brute force, using nothing but a timestamp filter, and fails the build if the fast production version disagrees. A second automated check flags any single feature that predicts the fraud label suspiciously well on its own, since that is the signature of a leak. On top of this, an **identity graph** connects customers through shared devices, addresses, and payment methods, and a feature capturing how much confirmed fraud already exists elsewhere in a customer's cluster improved every model tried, evidence that relational structure carries real signal a row by row model cannot see.

**Honest model comparison, including a genuine surprise.** A full ladder of approaches was trained, from a hand written baseline rule up through XGBoost with graph features, and every model was evaluated on a temporal train and test split so that no model could see the future during training.

| Model | Ranking Quality | Fraud $ Caught | Net $ Saved |
|---|---|---|---|
| Logistic regression + graph features | 0.304 | $2,185 | $937 |
| XGBoost + graph features | 0.301 | $1,663 | $437 |
| Plain logistic regression | 0.266 | $2,293 | **$1,049** |
| Hand written rule (baseline) | 0.087 | $859 | **negative $391** |

Accuracy was deliberately never used as the evaluation metric, since at this fraud rate a model that predicts nothing at all would still be over 95% accurate. The two columns above disagree with each other: the graph augmented XGBoost model has the best ranking quality, but plain logistic regression, the simplest model on the list, saves the most money by a wide margin. That mismatch is reported directly rather than hidden behind whichever metric looks most impressive, because the entire point of building a model ladder instead of training one model is to let the economics choose the champion.

**Turning a probability into an action, and knowing when not to retrain.** Cases are ranked by expected loss, meaning probability of fraud multiplied by dollar exposure, rather than raw probability, so a moderate risk high value case correctly outranks a near certain low value one. Net savings were found to peak at roughly 5% of cases reviewed and turn negative past roughly 15%, giving a direct, data grounded answer to how large an investigation team should be. A monitoring layer distinguishes drift, meaning the world changing, from decay, meaning the model itself going wrong, since conflating the two leads teams to retrain constantly on harmless seasonal wobble. In one monitored run, a customer tenure feature showed heavy drift while performance held steady, and the system correctly recommended watching the situation rather than triggering a retrain.

**A grounded LLM explainer that cannot make a decision.** A local LLM translates a case's evidence into a plain English explanation an investigator can read without parsing the underlying math. The rule that was never compromised: the model decides risk, and the LLM only narrates evidence it has been handed. Every number the LLM writes into its explanation is checked against the actual evidence packet; a number that cannot be verified causes the explanation to be discarded and replaced with a template built from the same evidence, which is the same fallback path used whenever the LLM is unavailable at all, so the system's core function never depends on an LLM being up.

#### Engineering & Production Readiness
The system was rebuilt into a modular package: `lakehouse / features / ml / ai / serving / monitoring / orchestration`. Thirty four tests cover leakage checks, data quality rules, evaluation logic, the API contract, and LLM explanation grounding, all running through GitHub Actions. It ships with a FastAPI scoring service, an operations console for investigators, Docker and Docker Compose, and a parallel implementation of the same pipeline written for Databricks and Spark. The entire system runs locally with no cloud account required, and rebuilds itself from nothing in under a minute.

#### What This Demonstrates
Fraud and risk systems thinking that extends well past the model itself: synthetic data honesty, leakage proof feature engineering, evaluation aligned to the real cost function rather than a proxy metric, drift versus decay monitoring, and constraining a language model to narration rather than decision making.

<br>

## Case Study 3: Pricing Heterogeneity
### Causal Inference for Customer Pricing Strategy

**Repository:** [Phani-2608/Pricing-heterogeneity](https://github.com/Phani-2608/Pricing-heterogeneity)
**Live API:** [pricing-heterogeneity-api.onrender.com/docs](https://pricing-heterogeneity-api.onrender.com/docs)
**Live Dashboard:** [pricing-heterogeneity-dashboard.onrender.com](https://pricing-heterogeneity-dashboard.onrender.com)

#### Overview
A price change does not affect every customer the same way. Some customers are highly price sensitive, others barely notice, and treating a population as if it has one uniform response leaves money on the table in both directions. This project estimates that heterogeneity credibly, using causal inference rather than correlational modeling, and then converts the estimates into a pricing policy that can be evaluated on real business outcomes.

#### The Problem
Estimating how a treatment (in this case, a price change) affects different individuals differently, without the benefit of a live randomized experiment, is a classic causal inference challenge. A naive regression of outcome on price and customer features will confound the causal effect of price with every other reason a given customer's outcome happens to correlate with price. The goal here was to estimate individual level treatment effects credibly, and prove that the estimates were credible by checking them against a known ground truth.

#### Technical Approach
Twelve thousand synthetic customers were simulated with a known, ground truth treatment effect baked in, specifically so that the quality of every downstream estimator could be verified against reality instead of merely assumed. **Cross fitted Double Machine Learning (DML)** was used to separate the estimation of nuisance functions (the outcome model and the propensity model) from the estimation of the causal parameter itself, which avoids the regularization bias that plagues naive plug in estimators.

The analysis was built as a hierarchy rather than a single number: **Average Treatment Effect (ATE)** first, then **Conditional Average Treatment Effect (CATE)** across customer segments, then **Individual Treatment Effect (ITE)** at the level of a single customer. Those individual level estimates were then converted into an actual targeting *policy*, rather than stopping at estimation and calling the project finished. Finally, a **fairness audit** was run against that policy, rather than assuming a model built to maximize profit is automatically neutral across customer groups.

#### Results, Verified Against Ground Truth
| Metric | Value |
|---|---|
| True ATE versus DR estimated ATE | 6.0% versus 7.3% |
| CATE versus truth correlation | 0.715 |
| Validation checks passed | 17 of 17 |
| ITE targeted policy versus treat all | **+32.5% profit** |
| Treat all versus treat none | negative 21.2% profit |
| Fairness audit (disparity ratio) | 0.373, fails the four fifths rule, reported openly rather than hidden |

#### Engineering & Production Readiness
The project was rebuilt from a single notebook into a modular package covering `data / sql / features / causal / models / evaluation / optimization / api / dashboard / monitoring`, backed by 33 pytest tests. It ships as a FastAPI service and a Streamlit dashboard, both containerized with Docker and Docker Compose, with GitHub Actions CI running lint, tests, and a Docker build across Python 3.10 and 3.11.

#### What This Demonstrates
Causal inference that goes beyond correlational machine learning, honest evaluation of model quality against a known ground truth rather than a proxy, and the willingness to surface a model's fairness failure in the open rather than reporting only the metric that looks favorable.

---

### 📌 A Note on How I Work
I try to treat every project like something that has to survive contact with production: tests, CI, containerization, and an honest accounting of where a model's assumptions break down, rather than a notebook that only has to run once.

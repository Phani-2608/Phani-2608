# Phanindra Reddy Mathireddy

### AI/ML Systems · Causal Inference · Data Engineering · Agentic AI

I build end-to-end machine learning and AI systems with an emphasis on a part of the work that is often harder than training the model itself:

**making the system trustworthy, measurable, reproducible, deployable, and useful for an actual decision.**

My projects span causal machine learning, fraud intelligence, data engineering, graph-based modeling, agentic RAG, knowledge graphs, experimentation, model evaluation, APIs, monitoring, and MLOps.

Rather than treating projects as isolated notebooks, I build them as **technical case studies** around a real question:

> What would have to be true for this system to be trusted in production?

---

## What I Build

| Area | What I Work On |
|---|---|
| **Machine Learning** | classification, anomaly detection, tree models, ensemble methods, feature engineering, model calibration, explainability |
| **Causal ML** | ATE, CATE, ITE, Double ML, uplift modeling, treatment-effect estimation, policy optimization |
| **Experimentation** | hypothesis testing, power analysis, MDE, segment analysis, placebo tests, sensitivity analysis |
| **Data Engineering** | PySpark, medallion architecture, data-quality gates, quarantine workflows, incremental processing, late-arriving data |
| **Graph Systems** | identity graphs, relationship-based features, knowledge graphs, PageRank |
| **Generative AI** | agentic workflows, RAG, retrieval systems, structured generation, context engineering, grounded LLM outputs |
| **ML Systems** | train/serve consistency, model APIs, monitoring, drift detection, reproducibility, versioning |
| **Production Engineering** | FastAPI, Docker, CI/CD, automated testing, configuration management, structured logging |
| **Decision Systems** | cost-sensitive optimization, expected value, operational thresholds, policy evaluation, business-aware model selection |

---

# Case Studies

## 01 · Heterogeneous Treatment Effects in Customer Pricing

### Causal ML · Experimentation · Decision Science · MLOps

**Repository:** [Pricing-heterogeneity](https://github.com/Phani-2608/Pricing-heterogeneity)

This project started with a deceptively simple business question:

> **Should a company offer a pricing intervention to every customer?**

A traditional predictive model cannot answer that question.

It may predict who will purchase, but it does not tell us whether the intervention **caused** the purchase or whether the customer would have converted anyway.

So I approached the problem as a **causal decision system rather than a prediction problem**.

---

### The Core Problem

Average treatment effects can hide substantial variation between customers.

An intervention can appear beneficial on average while:

- reducing profitability for part of the population
- unnecessarily treating customers who would convert anyway
- missing customers who respond strongly
- creating fairness concerns
- producing a policy that looks statistically sound but is economically poor

The objective therefore became:

**Estimate individual treatment effects, validate that those estimates are credible, and translate them into a deployable pricing policy.**

---

### Causal Architecture

I built the system around **cross-fitted Double Machine Learning**.

The pipeline estimates:

- **ATE** — Average Treatment Effect
- **CATE** — Conditional Average Treatment Effect
- **ITE** — Individual Treatment Effect

Cross-fitting separates nuisance-model estimation from treatment-effect estimation to reduce overfitting bias.

Instead of relying on a single causal estimate, I built a validation framework around it.

The system evaluates:

- propensity-score overlap
- positivity
- covariate balance
- inverse-probability weighting
- GATES calibration
- Qini performance
- subgroup stability
- placebo treatment tests
- placebo outcome tests
- unmeasured-confounder sensitivity

The complete validation suite contains **17 causal and statistical checks**.

---

### From Causal Estimates to Decisions

Estimating an ITE is not the final product.

The system converts treatment effects into per-customer recommendations by combining:

`Expected Treatment Lift`

×

`Customer Value`

×

`Incremental Revenue`

−

`Treatment Cost`

This enables direct comparison between multiple strategies:

- Treat nobody
- Treat everybody
- Random targeting
- Segment-based targeting
- Individual treatment-effect targeting

That distinction matters.

In the experiment, the average intervention looked positive when viewed only through conversion lift.

But treating everyone would have reduced profit by roughly **21%** compared with treating nobody.

The individualized treatment policy produced approximately **32% higher profit than the treat-all strategy**.

The lesson was more important than the metric:

> **A statistically positive treatment effect does not automatically imply a profitable policy.**

---

### Fairness as a Shipping Constraint

I also evaluated the proposed targeting policy for disparate treatment across protected age groups.

The resulting disparity ratio was approximately **0.37**, below the conventional four-fifths threshold.

Instead of hiding an inconvenient result because the economic policy performed well, the system explicitly reports that the policy **should not be deployed unchanged**.

That is intentional.

A production decision system should be capable of saying:

> The model works technically, but the policy is not ready to ship.

---

### Predictive Modeling Layer

The project also includes a predictive model ladder:

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM

evaluated with:

- ROC-AUC
- PR-AUC
- precision
- recall
- F1
- Brier score
- calibration

SHAP-based explanations are supported, with a permutation-importance fallback when needed.

---

### Production System

The causal work is wrapped inside a complete ML application rather than being left inside a notebook.

The project includes:

**Data**
- multi-table customer data
- transaction data
- treatment history
- pricing experiments
- SQL joins
- CTEs
- window functions
- validation and leakage checks

**Serving**
- FastAPI
- single-customer treatment prediction
- batch prediction
- health endpoints
- model metadata

**Monitoring**
- feature drift
- prediction drift
- treatment-effect drift
- calibration drift

**MLOps**
- versioned model registry
- YAML configuration
- reproducible training
- structured logging
- Docker
- Docker Compose
- GitHub Actions

**Quality**
- 33 automated tests
- unit tests
- integration tests
- data tests
- model tests
- API tests
- linting and CI

---

### What This Case Study Demonstrates

This project reflects how I think about applied data science:

**Prediction → Causality → Validation → Policy → Economics → Fairness → Deployment**

The model is only one component.

The real output is a **defensible decision system**.

---

### Tech Stack

`Python` `SQL` `Pandas` `Scikit-learn` `XGBoost` `LightGBM` `Double ML` `SHAP` `FastAPI` `Streamlit` `MLflow` `Docker` `GitHub Actions`

[View Repository →](https://github.com/Phani-2608/Pricing-heterogeneity)

---

# 02 · Boomerang

## Retail Return Fraud Intelligence System

### Data Engineering · Fraud ML · Graph Analytics · MLOps · Responsible GenAI

**Repository:** [Boomerang](https://github.com/Phani-2608/Boomerang)

Boomerang started from another question that sounds easier than it actually is:

> **How do you build a fraud model that still works once it leaves the notebook?**

Fraud detection is not only a classification problem.

A production system must deal with:

- unreliable source data
- duplicate events
- late corrections
- temporal leakage
- extreme class imbalance
- changing behavior
- limited investigation capacity
- fraud networks
- investigation cost
- model drift
- delayed feedback
- explainability requirements

Boomerang was designed around the entire lifecycle.

---

### Building Difficult Data Instead of Convenient Data

Public retail datasets rarely contain realistic return-fraud labels.

Instead of generating synthetic data using a simple deterministic fraud rule, I deliberately introduced uncertainty.

The data generator includes:

- legitimate activity from fraudulent customers
- hidden fraud drivers unavailable to the model
- missed fraud labels
- false-positive investigator labels
- duplicate events
- malformed refund values
- timestamp inconsistencies
- late-arriving corrections

This prevents the model from simply reverse-engineering the synthetic labeling rule.

The goal was to create data that behaves like something an engineering team would actually need to reason about.

---

### Medallion Data Architecture

The pipeline follows a layered architecture:

`Raw Events`

↓

`Bronze`

↓

`Validation + Deduplication`

↓

`Quarantine`

↓

`Silver`

↓

`Business Features`

↓

`Gold`

↓

`Model Scoring`

Invalid records are never silently discarded.

Every rejected event is written to quarantine with a reason, and the pipeline performs reconciliation:

`Input Rows = Valid Rows + Quarantined Rows`

If the equation fails, downstream publication stops.

---

### Incrementality and Late Data

Duplicate elimination alone is not enough for event systems.

A corrected return can arrive after an earlier version has already been processed.

A naïve `DISTINCT` operation can preserve both versions and corrupt downstream calculations.

Boomerang therefore handles changes using business-key-aware merge logic and source assertion time.

That allows the system to process:

- retries
- duplicates
- corrections
- late-arriving records

without silently double counting transactions.

---

### Point-in-Time Correct Features

Fraud models are especially vulnerable to temporal leakage.

A feature such as:

`customer_return_rate`

looks harmless.

But if it is calculated using a customer's entire history, it may include returns that occurred **after the transaction being predicted**.

The resulting model can perform extremely well offline while being impossible to reproduce in production.

Boomerang therefore constructs behavioral features using only information available before each scoring timestamp.

I also built leakage tests that independently recompute historical features and compare them against the optimized implementation.

The build fails when those values disagree.

---

### Identity Graph

Fraud is relational.

A customer may appear completely normal individually while sharing:

- a payment method
- a device
- an address

with multiple previously suspicious accounts.

Boomerang builds an **identity graph** connecting those entities.

Graph-derived signals capture information such as:

- accounts sharing a device
- connected fraudulent identities
- suspicious cluster exposure
- shared payment relationships
- network-level fraud behavior

This gives the model visibility into fraud patterns that cannot be represented by customer-level rows alone.

---

### Model Ladder

Instead of beginning with the most complex algorithm, I built a progression:

`Rules`

→ `Logistic Regression`

→ `Random Forest`

→ `Isolation Forest`

→ `XGBoost`

→ `Graph-enhanced Models`

Models are evaluated on a **temporal split** rather than a random split.

Earlier events train the model.

Later events evaluate it.

That better approximates what happens when a production system encounters future behavior.

---

### Accuracy Is the Wrong Objective

For rare-event fraud problems, accuracy can be actively misleading.

A model predicting every transaction as legitimate can achieve extremely high accuracy while preventing zero fraud.

Boomerang therefore evaluates models using operational metrics such as:

- ranking quality
- precision at review capacity
- recall at review capacity
- fraud dollars captured
- investigation cost
- net dollars saved

One of the most useful findings was that the model with the strongest ranking metric was **not necessarily the model with the greatest economic value**.

That changes model selection.

The champion is selected according to the objective the system actually cares about rather than whichever model produces the most impressive headline ML metric.

---

### Risk Is Not the Same as Priority

A fraud probability still does not tell an investigator which case deserves attention first.

Consider:

`95% probability × $20 transaction`

versus

`60% probability × $900 transaction`

The second case may represent far greater expected financial exposure.

So Boomerang converts model probabilities into **expected-loss scores**:

`Probability of Fraud × Financial Exposure`

This creates an investigation queue optimized around expected impact rather than model confidence alone.

---

### Review Capacity as an Optimization Problem

Investigation capacity is finite.

Reviewing more cases does not automatically create more value.

As the threshold decreases:

- more fraud is captured
- more false positives enter the queue
- investigation costs increase

Boomerang evaluates that tradeoff directly to determine where additional review capacity stops being economically useful.

This moves the system beyond:

> “What threshold gives the best F1 score?”

toward:

> **“How much investigation capacity should this system actually consume?”**

---

### Monitoring Drift vs Decay

After deployment, two different problems can occur.

**Drift**

The incoming population changes.

**Decay**

The model stops predicting accurately.

Those situations do not necessarily require the same response.

Boomerang monitors both feature distributions and predictive performance so routine population changes do not automatically trigger unnecessary retraining.

---

### Grounded Generative AI

I added an LLM layer for investigator assistance, but deliberately kept it outside the decision boundary.

The fraud model decides risk.

The LLM explains the evidence.

The language model never determines whether a transaction is fraudulent.

Every numerical claim in the generated explanation is checked against the structured evidence packet.

If the model introduces unsupported numerical information, the response is rejected and replaced with a deterministic explanation.

The application also continues functioning when the LLM is unavailable.

This keeps generative AI useful without making it a hidden source of decision risk.

---

### End-to-End Application

Boomerang connects the components into a complete workflow:

`Retail Events`

↓

`Data Quality + Quarantine`

↓

`Medallion Pipeline`

↓

`Point-in-Time Features`

↓

`Identity Graph`

↓

`Fraud Models`

↓

`Economic Evaluation`

↓

`Expected-Loss Ranking`

↓

`FastAPI Scoring`

↓

`Investigator Console`

↓

`Monitoring + Feedback`

The repository includes:

- synthetic data generation
- local data pipeline
- Spark/Databricks implementation
- feature engineering
- graph construction
- model training
- evaluation
- scoring service
- monitoring
- orchestration
- investigator UI
- grounded AI explanations
- Docker deployment
- CI/CD
- 34 automated tests

---

### What This Case Study Demonstrates

Boomerang represents the way I approach production ML:

> **Trust the data before trusting the model.**  
> **Protect the evaluation from leakage.**  
> **Optimize for the operational objective.**  
> **Design for what happens after deployment.**

---

### Tech Stack

`Python` `PySpark` `Pandas` `Delta Lake` `Scikit-learn` `XGBoost` `NetworkX` `FastAPI` `Docker` `GitHub Actions` `LLMs`

[View Repository →](https://github.com/Phani-2608/Boomerang)

---

# 03 · SleepMind AI

## Moving Intelligence From Query Time to Sleep Time

### Agentic AI · RAG · Knowledge Graphs · LLM Evaluation · Cost Engineering

**Repository:** [sleepmind-ai](https://github.com/Phani-2608/sleepmind-ai)

**Live Application:** [sleepmind-ai-dashboard.onrender.com](https://sleepmind-ai-dashboard.onrender.com)

SleepMind explores a different architectural question:

> **Why should an AI application wait until the user asks a question before doing all of its expensive reasoning?**

Traditional RAG performs most of its work after a request arrives:

`Question → Retrieval → Context → LLM → Answer`

SleepMind moves part of that intelligence offline.

When a research paper is uploaded, autonomous agents analyze it **before any user query exists**.

Their outputs are stored as reusable artifacts that can later participate in retrieval.

The resulting architecture becomes:

`Document`

↓

`Sleep-Time Intelligence`

↓

`Reusable Artifacts`

↓

`Fast Retrieval`

↓

`Query-Time Reasoning`

---

### Four Autonomous Agents

The preprocessing pipeline contains four specialized agents.

#### Summary Agent

Extracts:

- core contributions
- findings
- methodology
- limitations
- important conclusions

#### FAQ Generator

Generates likely question-answer pairs spanning multiple difficulty levels.

These become additional retrieval artifacts rather than disappearing after generation.

#### Future Query Predictor

Attempts to predict questions that a reader is likely to ask later.

Answers can therefore be partially precomputed before the actual user request arrives.

#### Concept Extractor

Identifies:

- concepts
- entities
- relationships

which are transformed into a knowledge graph.

Each agent includes:

- retry handling
- configurable timeouts
- structured outputs
- failure recovery
- isolated testing

A failed agent does not crash the entire pipeline.

---

### Multi-Source Retrieval

Traditional RAG retrieves primarily from document chunks.

SleepMind can retrieve from several representations of the same document:

- original source chunks
- generated FAQs
- predicted future questions
- precomputed answers
- document summary
- knowledge-graph context

The goal is not merely adding more context.

It is creating **different semantic views of the same information before query time**.

---

### Vector Retrieval

Documents are:

1. extracted
2. cleaned
3. chunked
4. embedded
5. indexed in FAISS

Separate semantic indexes can represent source material and generated artifacts.

Persisting those indexes allows the application to warm-start without recomputing embeddings each time.

---

### Knowledge Graph

The Concept Extractor produces entities and relationships that are converted into a directed **NetworkX knowledge graph**.

PageRank is used to prioritize structurally important concepts.

The graph is serializable and exposed to both the API and interactive dashboard.

This creates a retrieval signal fundamentally different from pure embedding similarity:

**semantic similarity + explicit relationships**

---

### Traditional RAG vs Sleep-Time RAG

I did not want SleepMind to exist only as an architectural idea.

So the system includes a controlled benchmark that runs the same questions against:

**Traditional RAG**

and

**Sleep-Time RAG**

while measuring:

- query latency
- token consumption
- estimated cost
- retrieval-source usage
- source coverage

The experiments are logged through MLflow for comparison and regression tracking.

---

### Cost Break-Even Analysis

Moving computation offline introduces a new tradeoff.

Sleep-time preprocessing costs money upfront.

That only makes sense if enough later queries reuse the generated intelligence.

So the system explicitly models:

`Upfront Preprocessing Cost`

versus

`Per-Query Savings × Query Volume`

to estimate the query volume at which sleep-time computation becomes economically favorable.

That makes cost part of the architecture rather than something evaluated after the system is already built.

---

### Artifact Persistence and Reproducibility

Generated intelligence is stored as persistent artifacts.

Artifacts are content-hashed so outputs can be connected back to:

- source document
- configuration
- preprocessing run

FAISS indexes are persisted as well, avoiding unnecessary re-embedding during restart.

---

### API Layer

FastAPI exposes the system through endpoints for:

- document upload
- preprocessing
- querying
- pipeline comparison
- artifact inspection
- knowledge-graph retrieval
- health monitoring

This keeps the AI components accessible independently from the front-end application.

---

### Interactive Research Interface

The Streamlit application provides a visual interface for:

- uploading papers
- running preprocessing
- asking questions
- comparing retrieval modes
- inspecting generated artifacts
- exploring the knowledge graph
- reviewing benchmark results

---

### Production Engineering

SleepMind includes the engineering around the AI model as well:

- modular package architecture
- configuration management
- environment-based secret handling
- structured logging
- Docker
- Docker Compose
- GitHub Actions
- linting
- automated Docker builds
- MLflow tracking
- regression monitoring
- 27 automated tests

The LLM calls are mocked during testing, allowing CI to validate system logic without requiring external API credentials.

---

### What This Case Study Demonstrates

SleepMind is less about calling an LLM and more about **designing computation around an LLM**.

It explores:

**Where should reasoning happen?**

**Which outputs should become reusable state?**

**How should different retrieval representations interact?**

**How do we measure whether architectural complexity actually improves latency or cost?**

**How do we make agentic systems testable rather than treating agents as opaque prompts?**

The core idea is:

> **Inference-time intelligence does not have to begin at inference time.**

---

### Tech Stack

`Python` `OpenAI` `LangChain` `FAISS` `NetworkX` `PyMuPDF` `FastAPI` `Streamlit` `MLflow` `Docker` `GitHub Actions`

[View Repository →](https://github.com/Phani-2608/sleepmind-ai)

[Launch Application →](https://sleepmind-ai-dashboard.onrender.com)

---

# Engineering Principles

Across these projects, I tend to follow the same principles.

### 1. Start with the decision, not the algorithm

The best predictive model is irrelevant if its output does not improve the decision the system exists to support.

### 2. Evaluation should resemble deployment

Temporal data gets temporal splits.

Causal claims get falsification tests.

Fraud systems get cost-sensitive metrics.

AI systems get latency and cost benchmarks.

### 3. Data quality is part of the model

Schema failures, duplicates, leakage, corrections, missingness, and invalid records should be handled explicitly rather than hidden inside preprocessing.

### 4. Simple models deserve to win

Complexity is justified only when it creates measurable value.

A simpler model with better operational economics is a better model.

### 5. Production constraints belong in the experiment

Latency, investigation capacity, fairness, cost, deployment architecture, monitoring, and failure modes should influence design before the model ships.

### 6. Generative AI should have boundaries

LLMs are powerful components, but probabilistic generation should not silently control deterministic business decisions.

Grounding, validation, fallbacks, and observability matter.

### 7. Systems should explain when they should not be trusted

A failed fairness audit, poor overlap, deteriorating model performance, invalid data, or unsupported LLM output should be surfaced rather than hidden.

### 8. Reproducibility is an engineering feature

Configuration, seeds, versioned models, persistent artifacts, automated tests, CI and containerization make experimental results far more valuable.

---

# Technical Depth

### Machine Learning & Statistics

`Scikit-learn` · `XGBoost` · `LightGBM` · `Random Forest` · `Logistic Regression` · `Isolation Forest` · `SHAP` · `Calibration` · `Statistical Testing`

### Causal Inference & Experimentation

`Double Machine Learning` · `ATE` · `CATE` · `ITE` · `Uplift Modeling` · `Propensity Scores` · `IPW` · `GATES` · `Qini` · `Sensitivity Analysis` · `Power Analysis` · `MDE`

### Generative AI

`Agentic AI` · `RAG` · `Semantic Retrieval` · `FAISS` · `Knowledge Graphs` · `Structured Generation` · `Context Engineering` · `LLM Evaluation` · `Grounded Generation`

### Data Engineering

`SQL` · `PySpark` · `Pandas` · `Medallion Architecture` · `Data Quality Gates` · `Quarantine` · `Incremental Processing` · `MERGE/Upserts` · `Point-in-Time Features`

### Graph Analytics

`NetworkX` · `Identity Graphs` · `Knowledge Graphs` · `Graph Features` · `PageRank`

### APIs & Applications

`FastAPI` · `REST APIs` · `Streamlit` · `Pydantic`

### MLOps & Production

`MLflow` · `Docker` · `Docker Compose` · `GitHub Actions` · `CI/CD` · `Model Monitoring` · `Drift Detection` · `Model Registry` · `Automated Testing`

### Core

`Python` · `SQL` · `Git` · `Linux` · `YAML` · `JSON`

---

# The Common Thread

The three projects solve different problems:

**Pricing Heterogeneity** asks:

> Who should receive an intervention?

**Boomerang** asks:

> Which events deserve investigation?

**SleepMind AI** asks:

> When should expensive AI reasoning happen?

But the engineering approach is consistent:

`Problem`

→ `Data`

→ `Validation`

→ `Modeling`

→ `Evaluation`

→ `Decision Logic`

→ `API`

→ `Monitoring`

→ `Testing`

→ `Deployment`

That end-to-end layer is the part of machine learning and AI engineering I find most interesting.

---

## Explore the Projects

### 📈 Causal ML & Decision Science
[**Pricing Heterogeneity →**](https://github.com/Phani-2608/Pricing-heterogeneity)

Cross-fitted Double ML, heterogeneous treatment effects, experimentation, policy optimization, fairness auditing and production deployment.

### 🔄 Fraud Intelligence & ML Systems
[**Boomerang →**](https://github.com/Phani-2608/Boomerang)

Medallion data architecture, point-in-time features, identity graphs, fraud ML, economic optimization, monitoring and grounded AI explanations.

### 🧠 Agentic AI & Retrieval
[**SleepMind AI →**](https://github.com/Phani-2608/sleepmind-ai)

Autonomous agents, sleep-time compute, RAG, FAISS, knowledge graphs, controlled LLM benchmarking and cost engineering.

---

### Build systems that can answer three questions:

**Does it work?**

**Can I prove it works?**

**Would I trust it in production?**

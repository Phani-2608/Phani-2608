<h1 align="center">Phanindra Reddy Mathireddy</h1>
<h3 align="center">AI/ML Engineer &amp; Data Scientist</h3>

<p align="center">
I build AI and ML systems end to end — from problem framing through deployment — for organizations that need results measured in business outcomes, not benchmark scores. My work spans agentic and retrieval-based generative AI, causal inference and experimentation, and the production infrastructure that keeps a system reliable once it's live: APIs, containers, CI/CD, and monitoring.
</p>

<p align="center">
<a href="https://www.linkedin.com/in/phanindram26/"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white"></a>
<a href="mailto:phanindra2608@gmail.com"><img src="https://img.shields.io/badge/Email-Contact-D14836?style=flat&logo=gmail&logoColor=white"></a>
<a href="https://phanindra26.netlify.app/"><img src="https://img.shields.io/badge/Portfolio-Visit-000000?style=flat&logo=vercel&logoColor=white"></a>
</p>

<p align="center">
<em>Generative AI Engineer at PayPal (Payments &amp; Risk Intelligence) · Former ML Engineer at Cigna (Healthcare AI) · MS Computer Science, UMBC</em>
</p>

---

### What I Build

I work at the intersection of applied ML and product engineering, where the model is one component of the system rather than the whole deliverable. Concretely: retrieval and agentic architectures for generative AI, causal inference and experimentation for decision systems, and the surrounding infrastructure — APIs, containers, CI, monitoring — that makes any of it dependable in production. My recent work centers on transaction-risk intelligence and agentic customer support at PayPal, and clinical prediction systems at Cigna, both operating against real production data volumes.

---

## Featured Work

### SleepMind AI — Sleep-Time Compute Research Assistant

**Problem.** Most RAG systems do all their reasoning at query time, which caps how much context or agentic depth you can afford before latency and cost become the constraint.

**What I Built.** A document intelligence system that shifts reasoning to *before* the query arrives. Four autonomous agents — Summary, FAQ Generator, Future Query Predictor, and Concept Extractor — pre-process a document offline, populating a semantic retrieval layer and a knowledge graph so that the online path becomes a lookup rather than a fresh reasoning pass.

**Engineering Depth.** Modular Python package (ingestion, agents, retrieval, knowledge graph, storage, evaluation, API, dashboard, monitoring) — not a single notebook. FastAPI service, Streamlit dashboard, Docker + docker-compose, GitHub Actions CI with 27 fully mocked tests (no API key required to run the pipeline in CI). Secrets are resolved from environment variables only, with no keys committed to the repository.

**Evaluation.** Benchmarked head-to-head against traditional query-time RAG across latency, token usage, retrieval quality, and a cost break-even model, with experiment tracking in MLflow.

**Business Impact.** Demonstrates a concrete pattern for cutting inference-time cost and latency in document-heavy AI products by moving computation off the critical path — directly relevant to any system serving high query volume against a fixed knowledge base.

**Live Demo.** [Try the App](https://sleepmind-ai-dashboard.onrender.com/) · [API Docs](https://sleepmind-ai-api.onrender.com/docs) · [Repository](https://github.com/Phani-2608/sleepmind-ai)

> Hosted on a free tier — the first request after idle may take 30–60s to spin up.

---

### Heterogeneous Treatment Effects in Customer Pricing Strategy

**Problem.** A pricing intervention with a positive *average* effect can still be the wrong call — if the effect is concentrated in a subset of customers, a blanket rollout can destroy value even while the topline number looks good.

**What I Built.** A causal decision system that estimates *individual*, not average, treatment effects using cross-fitted Double Machine Learning across 12,000 customers, then turns those estimates into an actual targeting policy rather than stopping at "the average effect is positive."

**Engineering Depth.** Production-structured Python package (data, features, causal, models, evaluation, optimization, API, dashboard, monitoring) with FastAPI serving, a Streamlit decision simulator for stakeholders, Docker + docker-compose, GitHub Actions CI (lint, tests, Docker build across Python 3.10/3.11), and 33 automated tests.

**Evaluation.** 17 causal-validity diagnostics covering propensity overlap, GATES calibration, Qini ranking, placebo and falsification testing, and sensitivity analysis — all 17 passing. CATE estimates correlate at 0.715 with known ground truth. SHAP explainability and a fairness audit are included and reported as-is, including where the model falls short of the four-fifths rule, rather than hidden. Findings are packaged into a confirmatory A/B test design rather than presented as a final answer.

**Business Impact.** A blanket rollout to every customer — despite a positive average treatment effect (~6–7%) — would destroy **21.2% of profit**. Targeting by individual treatment effect instead of treating everyone improves profit by **32.5%** relative to the blanket-rollout policy.

**Live Demo.** [Explore the Decision Simulator](https://pricing-heterogeneity-dashboard.onrender.com) · [API Docs](https://pricing-heterogeneity-api.onrender.com/docs) · [Repository](https://github.com/Phani-2608/Pricing-heterogeneity)

> Hosted on a free tier — the first request after idle may take 30–60s, as the model retrains fresh on deploy/cold start.

---

### Professional Focus

**Generative AI Engineer — Payments & Risk Intelligence, PayPal** — building agentic and retrieval-based systems over transaction data at scale, aimed at reducing false-positive fraud alerts and automating multilingual customer support workflows.

**Machine Learning Engineer — Healthcare AI & Clinical Informatics, Cigna** — predictive models and clinical decision support built over large-scale patient and clinical-note datasets, including medical-imaging validation pipelines.

Across both, the common thread is the same: define the metric that actually matters to the business, build the system that moves it, and prove — with evaluation, not assertion — that it works.

---

### Technical Toolkit

**Languages & Data** — Python · SQL

**Generative AI & Agentic Systems** — LLMs · RAG · Agentic AI · LangChain · LangGraph · CrewAI · FAISS · Knowledge Graphs

**ML & Causal Inference** — Machine Learning · Deep Learning · Double Machine Learning · Causal Inference · Model Explainability (SHAP) · Experimentation & A/B Testing

**Engineering & MLOps** — FastAPI · Docker · CI/CD (GitHub Actions) · MLflow · Automated Testing · Cloud-Deployed ML Systems

---

### Contact

Open to AI Engineer, Machine Learning Engineer, Applied AI Engineer, Data Scientist, and Forward Deployed Engineer roles.

[LinkedIn](https://www.linkedin.com/in/phanindram26/) · [phanindra2608@gmail.com](mailto:phanindra2608@gmail.com) · [Portfolio](https://phanindra26.netlify.app/)

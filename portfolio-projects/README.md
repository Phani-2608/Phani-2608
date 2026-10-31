# Two applied AI portfolio platforms

These two independently runnable projects were built as new work and are presented as **synthetic-data prototypes**. They are not representations of production experience at PayPal or Cigna.

- [Enterprise AI Agent & Investigation Platform](./enterprise-agent-platform): audited investigation workflows, local evidence retrieval, reviewer authorization, tenant isolation, FastAPI and a browser console, optional local MCP and LangGraph integration, plus an auditable case study.
- [Personalized Decision Intelligence & ML Experimentation Platform](./decision-intelligence-platform): trained recommendation ranking, temporal user holdouts, randomized experiment analysis and uplift estimation with a browser dashboard, optional RetailRocket and Hillstrom adapters, and a reproducible model card.

## Quick start

```bash
docker compose up --build
```

Then visit **http://localhost:8000** and **http://localhost:8001**. These are local demos. Demo keys are not safe to expose to the internet.

## Reproducibility

```bash
cd enterprise-agent-platform && python -m pip install -r requirements.txt && PYTHONPATH=. pytest -q
cd ../decision-intelligence-platform && python -m pip install -r requirements.txt && PYTHONPATH=. pytest -q
```

See the project READMEs for validation, architecture, limitations, and further research directions. CI runs on pull requests and commits affecting the portfolio directories.


## Optional public deployment

A Render infrastructure blueprint is provided at [`render.yaml`](render.yaml).
Connect this GitHub repository to Render and supply a private `API_KEYS_JSON`
for the investigation service. Demo keys are intentionally disabled on public
deployments. Its SQLite database requires persistent disk storage, so select a
Render plan that supports disks. The ML dashboard uses synthetic data by default.
No public service has been provisioned or verified by this repository alone.

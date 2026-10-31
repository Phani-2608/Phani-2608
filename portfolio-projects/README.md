# Two applied AI portfolio platforms

These two independently runnable projects were built as new work and are presented as **synthetic-data prototypes**. They are not representations of production experience at PayPal or Cigna.

- [Enterprise AI Agent & Investigation Platform](./enterprise-agent-platform): audited investigation workflows, local evidence retrieval, reviewer authorization, tenant isolation, FastAPI and a browser console.
- [Personalized Decision Intelligence & ML Experimentation Platform](./decision-intelligence-platform): trained recommendation ranking, temporal user holdouts, randomized experiment analysis and uplift estimation with a browser dashboard.

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

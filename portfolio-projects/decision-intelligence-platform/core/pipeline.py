"""Reproducible training and evaluation; artifacts can be regenerated."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import joblib
from .synthetic import make_interactions,make_randomized_experiment
from .ranking import train_ranker,RankingArtifacts
from .experimentation import train_experiment,ExperimentArtifacts

@dataclass
class PortfolioArtifacts:
    ranking: RankingArtifacts
    experiment: ExperimentArtifacts


def train_all(seed=42):
    events,items=make_interactions(seed=seed)
    experiment=make_randomized_experiment(seed=seed+2)
    return PortfolioArtifacts(train_ranker(events,items,seed=seed),train_experiment(experiment,seed=seed))

def metrics(data:PortfolioArtifacts):
    return {'ranking':data.ranking.metrics,'experiment':data.experiment.metrics,'uplift_segments':data.experiment.bins}

def save(data:PortfolioArtifacts,folder='artifacts'):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    joblib.dump(data,folder/'demo_models.joblib')
    (folder/'metrics.json').write_text(json.dumps(metrics(data),indent=2))

def load(folder='artifacts'):
    # Only load locally generated trusted artifacts. NEVER joblib.load untrusted user files.
    return joblib.load(Path(folder)/'demo_models.joblib')

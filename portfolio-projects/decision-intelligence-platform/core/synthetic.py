"""Synthetic interactions + randomized treatment data (never real users)."""
from __future__ import annotations
import numpy as np
import pandas as pd

CATEGORIES = ['books','electronics','home','fitness','fashion','outdoors']

def make_interactions(n_users=180, n_items=72, visits_per_user=14, seed=42):
    if n_items <= visits_per_user or n_items < 6:
        raise ValueError('Need more items than interactions per user')
    rng = np.random.default_rng(seed)
    items = pd.DataFrame({'item_id':[f'item-{i:03d}' for i in range(n_items)],
                          'category':[CATEGORIES[i%len(CATEGORIES)] for i in range(n_items)]})
    # Synthetic category affinity and item attractiveness create signal to learn.
    base = rng.lognormal(mean=0, sigma=.7, size=n_items)
    records = []
    for u in range(n_users):
        preferred = int(rng.integers(len(CATEGORIES)))
        incl = np.array([3.5 if i % len(CATEGORIES) == preferred else 1.0 for i in range(n_items)])
        probs = base * incl
        probs /= probs.sum()
        sampled = rng.choice(n_items, size=visits_per_user, replace=False, p=probs)
        for t, index in enumerate(sampled):
            records.append({'user_id':f'user-{u:03d}','item_id':f'item-{index:03d}',
                            'timestamp':t,'category':CATEGORIES[index%len(CATEGORIES)]})
    return pd.DataFrame.from_records(records), items

def make_randomized_experiment(n=12000, seed=24):
    rng = np.random.default_rng(seed)
    age = rng.integers(19, 75, size=n)
    prior_orders = rng.poisson(2, size=n)
    interest = rng.uniform(0, 1, size=n)
    assigned = rng.integers(0, 2, size=n)  # randomized assignment
    # Known unit-level probability effect; measured trial outcomes are Bernoulli.
    base = .07 + .002 * np.minimum(prior_orders, 10) + .02*interest
    uplift = .012 + .055*(interest > .65) - .012*(age > 60)
    p0 = np.clip(base, .001, .90)
    p1 = np.clip(base + uplift, .001, .95)
    outcome = rng.binomial(1, np.where(assigned==1,p1,p0))
    return pd.DataFrame({'age':age, 'prior_orders':prior_orders, 'interest':interest,
                         'treatment':assigned, 'conversion':outcome,
                         'true_uplift':p1-p0})

import os
os.environ['PORTFOLIO_SKIP_APP']='1'
import pytest
from fastapi.testclient import TestClient
from core.synthetic import make_interactions,make_randomized_experiment
from core.ranking import split_temporal,train_ranker,recommend
from core.experimentation import estimate_ate,train_experiment,predict_uplift
from core.pipeline import train_all,metrics,save,load
from backend.api import create_app

@pytest.fixture(scope='module')
def data():
    return train_all(42)

@pytest.fixture(scope='module')
def client(data):
    return TestClient(create_app(data))

def test_synthetic_generation_reproducible():
    a,_=make_interactions(n_users=4,n_items=30,seed=100)
    b,_=make_interactions(n_users=4,n_items=30,seed=100)
    assert a.equals(b)

def test_temporal_holdout_never_in_history():
    events,_=make_interactions(n_users=20,n_items=30,seed=8)
    hist,target=split_temporal(events)
    assert all(target[u] not in hist[u] for u in target)

def test_ranker_has_heldout_metrics(data):
    m=data.ranking.metrics
    assert 0<=m['model_hit_rate_at_10']<=1
    assert 0<=m['model_ndcg_at_10']<=1
    assert m['test_users']>0 and m['train_users']>0

def test_cold_start_fallback(data):
    results=recommend(data.ranking,'user-never-seen',5)
    assert len(results)==5 and all(x['source']=='cold_start_popularity' for x in results)

def test_recommendation_excludes_history(data):
    u=next(iter(data.ranking.user_history))
    out=recommend(data.ranking,u,10)
    assert all(i['item_id'] not in data.ranking.user_history[u] for i in out)

def test_ranking_invalid_k(data):
    with pytest.raises(ValueError):recommend(data.ranking,'user-never-seen',0)

def test_randomized_assignment_is_reproducible():
    a=make_randomized_experiment(n=100,seed=21)
    b=make_randomized_experiment(n=100,seed=21)
    assert a.equals(b)
    assert set(a.treatment)=={0,1}

def test_randomized_ate_has_interval():
    m=estimate_ate(make_randomized_experiment())
    assert m['ci95'][0]<=m['ate']<=m['ci95'][1]
    assert m['n_control']>0 and m['n_treatment']>0

def test_uplift_predict_probability(data):
    m=predict_uplift(data.experiment,35,3,.6)
    assert -1<=m['estimated_conversion_uplift']<=1
    assert 0<=m['treated_conversion_probability']<=1

def test_invalid_uplift_features(data):
    with pytest.raises(ValueError):predict_uplift(data.experiment,3,3,.6)

def test_model_persistence_round_trip(data,tmp_path):
    save(data,tmp_path)
    reopened=load(tmp_path)
    assert reopened.ranking.metrics==data.ranking.metrics
    assert recommend(reopened.ranking,'new-user',5)==recommend(data.ranking,'new-user',5)

def test_api_health_metrics_recommend_and_uplift(client):
    assert client.get('/health').json()['status']=='ok'
    assert client.get('/metrics').json()['ranking']['dataset']=='synthetic'
    assert len(client.get('/recommend/user-001?k=5').json()['items'])==5
    assert 'estimated_conversion_uplift' in client.get('/uplift?age=40&prior_orders=3&interest=0.7').json()
    assert client.get('/recommend/user-001?k=100').status_code==422
    assert client.get('/uplift?age=2').status_code==422

def test_unknown_user_recommendations_api(client):
    payload=client.get('/recommend/a-brand-new-user?k=3').json()
    assert len(payload['items'])==3
    assert all(x['score'] is None and x['source']=='cold_start_popularity' for x in payload['items'])

def test_metrics_are_reproducible():
    a=metrics(train_all(42))
    b=metrics(train_all(42))
    assert a==b

def test_experiment_requires_two_groups():
    from core.experimentation import estimate_ate
    import pandas as pd
    with pytest.raises(ValueError):estimate_ate(pd.DataFrame({'treatment':[1,1,1],'conversion':[0,1,0]}))

def test_experiment_rejects_nonbinary_treatment():
    from core.experimentation import estimate_ate
    import pandas as pd
    with pytest.raises(ValueError):estimate_ate(pd.DataFrame({'treatment':[0,1,2,1],'conversion':[0,1,0,1]}))

def test_dashboard_is_accessible(client):
    result=client.get('/')
    assert result.status_code==200
    assert 'Decision Intelligence Lab' in result.text


def test_ndcg_uses_same_deterministic_top_k_as_hit_rate():
    import numpy as np
    from core.ranking import evaluate_ranker
    class FlatModel:
        def predict_proba(self, features):
            return np.tile([.5, .5], (len(features), 1))
    candidates = [f'item-{i:03}' for i in range(25)]
    categories = {item: 'unknown' for item in candidates}
    result = evaluate_ranker(FlatModel(), ['u'], {'u': []},
                             {'u': candidates[-1]}, categories, {}, candidates, k=10)
    assert result['model_hit_rate_at_10'] == 0
    assert result['model_ndcg_at_10'] == 0
    assert result['popularity_ndcg_at_10'] == 0

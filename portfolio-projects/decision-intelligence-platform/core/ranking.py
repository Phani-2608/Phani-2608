"""Per-user temporal holdout ranking with trained item relevance model."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

@dataclass
class RankingArtifacts:
    model: HistGradientBoostingClassifier
    user_history: dict[str, list[str]]
    item_categories: dict[str, str]
    popularity: dict[str, int]
    candidates: list[str]
    metrics: dict


def split_temporal(events: pd.DataFrame):
    """Use only events strictly before each user's final interaction as history."""
    ordered = events.sort_values(['user_id','timestamp'], kind='stable')
    history, heldout = {}, {}
    for user, frame in ordered.groupby('user_id',sort=True):
        if len(frame)<2:
            continue
        history[user] = frame['item_id'].iloc[:-1].tolist()
        heldout[user] = frame['item_id'].iloc[-1]
    return history, heldout


def item_features(user: str, item: str, history, category, popularity, max_pop: int) -> list[float]:
    seen = history.get(user, [])
    cats = [category[x] for x in seen]
    thiscat = category[item]
    frac = cats.count(thiscat)/max(1,len(cats))
    recent = cats[-5:].count(thiscat)/max(1,min(5,len(cats)))
    return [frac, recent, popularity.get(item,0)/max(1,max_pop),len(seen)/25,
            float(thiscat == cats[-1]) if cats else 0.0]


def evaluate_ranker(model, test_users, history, target, categories, popularity, candidates, k=10):
    hit_model=[]; hit_pop=[]; ndcg_model=[]; ndcg_pop=[]
    max_pop=max(popularity.values(),default=1)
    for user in test_users:
        pool=[item for item in candidates if item not in set(history[user])]
        if target[user] not in pool:
            raise AssertionError('held-out item leaked into training history')
        features=np.asarray([item_features(user,item,history,categories,popularity,max_pop) for item in pool])
        ml_scores=model.predict_proba(features)[:,1]
        baseline=np.asarray([popularity.get(item,0) for item in pool],dtype=float)
        truth=np.asarray([1 if x==target[user] else 0 for x in pool])
        for scores, hits, ndcgs in [(ml_scores,hit_model,ndcg_model),(baseline,hit_pop,ndcg_pop)]:
            order=sorted(range(len(pool)), key=lambda i:(-float(scores[i]),pool[i]))
            top_items=[pool[i] for i in order[:k]]
            hit=target[user] in top_items
            hits.append(int(hit))
            # Use the same deterministic tie-break for HitRate and NDCG.
            # Tie-averaged ndcg_score otherwise credits items outside top K.
            ndcgs.append(float(1/np.log2(top_items.index(target[user])+2)) if hit else 0.0)
    return {
        'model_hit_rate_at_10':round(float(np.mean(hit_model)),4),
        'popularity_hit_rate_at_10':round(float(np.mean(hit_pop)),4),
        'model_ndcg_at_10':round(float(np.mean(ndcg_model)),4),
        'popularity_ndcg_at_10':round(float(np.mean(ndcg_pop)),4),
        'test_users':len(test_users),
        'split':'temporal leave-last-one-out within users; disjoint train/test user groups',
    }


def train_ranker(events: pd.DataFrame, items: pd.DataFrame, seed=42, k=10) -> RankingArtifacts:
    history, heldout = split_temporal(events)
    users=sorted(heldout)
    rng=np.random.default_rng(seed)
    users_perm=rng.permutation(users).tolist()
    cutoff=max(2,int(.7*len(users_perm)))
    train_users=users_perm[:cutoff];test_users=users_perm[cutoff:]
    if len(test_users)<1:
        raise ValueError('Not enough test users')
    category=dict(zip(items.item_id,items.category))
    candidates=sorted(category)
    # Popularity derived from training-group histories only, never from test targets.
    popularity=dict(Counter(item for user in train_users for item in history[user]))
    max_pop=max(popularity.values(),default=1)
    X=[];y=[]
    for user in train_users:
        positive=heldout[user]
        X.append(item_features(user,positive,history,category,popularity,max_pop));y.append(1)
        negatives=[i for i in candidates if i!=positive and i not in set(history[user])]
        for negative in rng.choice(negatives,size=min(12,len(negatives)),replace=False):
            X.append(item_features(user,str(negative),history,category,popularity,max_pop));y.append(0)
    model=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=10,learning_rate=.06,l2_regularization=1,random_state=seed)
    model.fit(np.asarray(X),np.asarray(y))
    metrics=evaluate_ranker(model,test_users,history,heldout,category,popularity,candidates,k)
    metrics['train_users']=len(train_users)
    metrics['training_samples']=len(X)
    metrics['dataset']='synthetic'
    return RankingArtifacts(model,history,category,popularity,candidates,metrics)


def recommend(artifacts: RankingArtifacts, user_id: str, k=10):
    if k<1 or k>50:
        raise ValueError('k must be between 1 and 50')
    history=artifacts.user_history
    pool=[i for i in artifacts.candidates if i not in set(history.get(user_id,[]))]
    if not pool:
        return []
    if user_id not in history:  # transparent cold start
        ranked=sorted(pool,key=lambda i:(-artifacts.popularity.get(i,0),i))
        return [{'item_id':i,'category':artifacts.item_categories[i],'score':None,'source':'cold_start_popularity'} for i in ranked[:k]]
    max_pop=max(artifacts.popularity.values(),default=1)
    X=np.asarray([item_features(user_id,i,history,artifacts.item_categories,artifacts.popularity,max_pop) for i in pool])
    scores=artifacts.model.predict_proba(X)[:,1]
    ranked=sorted(zip(pool,scores),key=lambda entry:(-float(entry[1]),entry[0]))
    return [{'item_id':i,'category':artifacts.item_categories[i],'score':round(float(score),4),'source':'learned_ranker'} for i,score in ranked[:k]]

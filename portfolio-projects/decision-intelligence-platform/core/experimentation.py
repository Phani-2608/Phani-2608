"""Randomized A/B test and T-learner with disjoint evaluation holdout."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

COVARIATES=['age','prior_orders','interest']

@dataclass
class ExperimentArtifacts:
    treatment: RandomForestClassifier
    control: RandomForestClassifier
    metrics: dict
    bins: list[dict]
    covariates: tuple[str, ...]


def estimate_ate(df: pd.DataFrame):
    """Welch standard error for a difference in randomized group means."""
    if not set(df.treatment.unique()).issubset({0,1}):
        raise ValueError('treatment must be binary')
    t=df.loc[df.treatment==1,'conversion'].astype(float)
    c=df.loc[df.treatment==0,'conversion'].astype(float)
    if len(t)<2 or len(c)<2:
        raise ValueError('need at least two people per arm')
    diff=float(t.mean()-c.mean())
    se=float(np.sqrt(t.var(ddof=1)/len(t)+c.var(ddof=1)/len(c)))
    pvalue=float(2*norm.sf(abs(diff/se))) if se>0 else (0.0 if diff else 1.0)
    return {'treatment_rate':round(float(t.mean()),5),'control_rate':round(float(c.mean()),5),
            'ate':round(diff,5),'ci95':[round(diff-1.96*se,5),round(diff+1.96*se,5)],
            'p_value':round(pvalue,5),'n_treatment':len(t),'n_control':len(c),
            'method':'randomized difference in means with normal 95% CI'}


def train_experiment(df:pd.DataFrame,seed=42,covariates=None,dataset_name='synthetic'):
    columns = tuple(covariates or COVARIATES)
    if not columns or any(col not in df.columns for col in columns):
        raise ValueError('missing pre-treatment covariates')
    train,test=train_test_split(df,test_size=.3,random_state=seed,stratify=df.treatment)
    def fit_arm(arm):
        subset=train[train.treatment==arm]
        model=RandomForestClassifier(n_estimators=90,max_depth=5,min_samples_leaf=10,random_state=seed+arm,n_jobs=-1)
        model.fit(subset[list(columns)],subset['conversion'])
        return model
    control=fit_arm(0);treatment=fit_arm(1)
    predicted=treatment.predict_proba(test[list(columns)])[:,1]-control.predict_proba(test[list(columns)])[:,1]
    # A synthetic ground truth is known from the generation process: diagnostic only.
    mae=float(np.mean(np.abs(predicted-test['true_uplift'].to_numpy()))) if 'true_uplift' in test else None
    result=estimate_ate(test)
    result.update({'test_rows':len(test),'train_rows':len(train),'uplift_mae_vs_synthetic_truth':round(mae,5) if mae is not None else None,
                   'dataset':dataset_name})
    if 'true_uplift' in test:
        result['synthetic_true_average_uplift']=round(float(test['true_uplift'].mean()),5)
    # Descriptive bins only. Do not confuse observed bin differences with causal validation.
    ranked=test.copy();ranked['predicted_uplift']=predicted
    ranked['segment']=pd.qcut(ranked['predicted_uplift'].rank(method='first'),q=5,labels=False)
    bins=[]
    for bin_id,frame in ranked.groupby('segment',sort=False):
        treated=frame.loc[frame.treatment==1,'conversion']
        controls=frame.loc[frame.treatment==0,'conversion']
        observed=float(treated.mean()-controls.mean()) if len(treated)>1 and len(controls)>1 else None
        bins.append({'segment':int(bin_id)+1,'count':int(len(frame)),
                     'predicted_uplift':round(float(frame.predicted_uplift.mean()),4),
                     'observed_treatment_minus_control':round(observed,4) if observed is not None else None})
    bins.sort(key=lambda x:-x['predicted_uplift'])
    return ExperimentArtifacts(treatment,control,result,bins,columns)


def predict_uplift(artifacts:ExperimentArtifacts,age:int,prior_orders:int,interest:float):
    if not 18<=age<=100 or not 0<=prior_orders<=1000 or not 0<=interest<=1:
        raise ValueError('features outside synthetic data bounds')
    if artifacts.covariates != tuple(COVARIATES):
        raise ValueError('This endpoint only supports the synthetic demo feature schema')
    frame=pd.DataFrame([{'age':age,'prior_orders':prior_orders,'interest':interest}])
    p1=float(artifacts.treatment.predict_proba(frame)[:,1][0])
    p0=float(artifacts.control.predict_proba(frame)[:,1][0])
    return {'estimated_conversion_uplift':round(p1-p0,5),'treated_conversion_probability':round(p1,5),'untreated_conversion_probability':round(p0,5),
            'warning':'Synthetic-data estimate, not a real-world treatment recommendation'}

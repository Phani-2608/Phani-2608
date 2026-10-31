"""Read-only synthetic-model APIs and a local interactive dashboard."""
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from core.pipeline import load,train_all,metrics
from core.ranking import recommend
from core.experimentation import predict_uplift


def create_app(data=None):
    app=FastAPI(title='Personalized Decision Intelligence Platform',version='1.0.0',
                description='Synthetic recommendations and randomized experimentation demonstration')
    models=data or (load(os.getenv('ARTIFACTS_DIR','artifacts')) if Path(os.getenv('ARTIFACTS_DIR','artifacts'),'demo_models.joblib').exists() else train_all())
    app.state.models=models

    @app.get('/health')
    def health():
        return {'status':'ok','dataset':'synthetic','trained':True}

    @app.get('/')
    def homepage():
        return FileResponse(Path(__file__).parent.parent/'frontend'/'index.html')

    @app.get('/metrics')
    def model_metrics():
        return metrics(models)

    @app.get('/users')
    def users():
        return sorted(models.ranking.user_history)[:100]

    @app.get('/recommend/{user_id}')
    def recommend_api(user_id:str,k:int=Query(default=10,ge=1,le=50)):
        return {'user_id':user_id,'items':recommend(models.ranking,user_id,k),'dataset':'synthetic'}

    @app.get('/uplift')
    def uplift(age:int=Query(default=35,ge=18,le=100),prior_orders:int=Query(default=2,ge=0,le=1000),
               interest:float=Query(default=.8,ge=0,le=1)):
        try:
            return predict_uplift(models.experiment,age,prior_orders,interest)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
    return app

app=create_app() if os.getenv('PORTFOLIO_SKIP_APP')!='1' else None

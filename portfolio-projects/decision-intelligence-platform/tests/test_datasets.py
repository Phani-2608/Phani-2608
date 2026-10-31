from core.datasets import load_retailrocket,load_hillstrom
from core.experimentation import train_experiment
import pytest
import pandas as pd


def test_retailrocket_adapter(tmp_path):
    rows=[]
    for user in range(6):
        for item in range(7):
            rows.append({'timestamp':1000000+item,'visitorid':user,'itemid':item+user*2,'event':'view'})
    source=tmp_path/'events.csv';pd.DataFrame(rows).to_csv(source,index=False)
    events,items=load_retailrocket(source,max_users=20)
    assert len(events)==42
    assert len(items)>=7
    assert set(['user_id','item_id','timestamp','category']).issubset(events)


def test_hillstrom_adapter_uses_pretreatment_only(tmp_path):
    rows=[]
    for i in range(80):
        rows.append({'segment':('Mens E-Mail' if i%2 else 'No E-Mail'),'conversion':int(i%5==0),
                     'recency':1+i%12,'history':i*20,'mens':i%2,'womens':(i+1)%2,'newbie':i%3==0,
                     'zip_code':'Urban' if i%2 else 'Rural','channel':'Web' if i%3 else 'Phone',
                     'visit':1,'spend':123.45})
    path=tmp_path/'hillstrom.csv';pd.DataFrame(rows).to_csv(path,index=False)
    df,columns=load_hillstrom(path)
    assert 'visit' not in df and 'spend' not in df
    assert not any(x in columns for x in ['visit','spend','conversion','treatment'])
    model=train_experiment(df,seed=4,covariates=columns,dataset_name='fixture')
    assert model.metrics['uplift_mae_vs_synthetic_truth'] is None
    assert model.metrics['dataset']=='fixture'


def test_hillstrom_rejects_invalid_variant(tmp_path):
    with pytest.raises(ValueError):
        load_hillstrom(tmp_path/'anything.csv',treatment_variant='All E-Mail')

def test_retailrocket_invalid_input_schema(tmp_path):
    path=tmp_path/'bad.csv'
    pd.DataFrame({'not_timestamp':[1]}).to_csv(path,index=False)
    with pytest.raises(ValueError):
        load_retailrocket(path,max_users=20)

def test_hillstrom_missing_pretreatment_fields(tmp_path):
    path=tmp_path/'bad.csv'
    pd.DataFrame({'segment':['No E-Mail'],'conversion':[0]}).to_csv(path,index=False)
    with pytest.raises(ValueError,match='missing Hillstrom columns'):
        load_hillstrom(path)


def test_hillstrom_suburban_source_spelling(tmp_path):
    # The publisher's original CSV actually spells the category "Surburban".
    rows = []
    for i in range(30):
        rows.append({
            'segment': 'Mens E-Mail' if i % 2 else 'No E-Mail',
            'conversion': int(i % 5 == 0), 'recency': i % 12 + 1,
            'history': i * 12, 'mens': i % 2, 'womens': (i + 1) % 2,
            'newbie': i % 3 == 0,
            'zip_code': 'Surburban' if i % 3 == 0 else 'Rural',
            'channel': 'Web'
        })
    path = tmp_path / 'hillstrom.csv'
    pd.DataFrame(rows).to_csv(path, index=False)
    frame, _ = load_hillstrom(path)
    assert frame['zip_suburban'].sum() == 10

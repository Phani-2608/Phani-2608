"""Optional adapters for user-provided public RetailRocket and Hillstrom datasets.

Raw datasets are NEVER downloaded automatically or committed into this repository.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd


def load_retailrocket(events_csv: str | Path, property_csvs=(), max_users=5000, minimum_interactions=3):
    """Normalize views/add-to-cart/transactions to the event schema used by ranking.

    Dataset is large; sampling users changes the evaluated population. Distinct
    (user,item) interactions are kept once to permit unseen-item holdout.
    Item category is static first-observed metadata when properties are supplied.
    """
    if not 3 <= minimum_interactions <= 50 or not 10 <= max_users <= 50000:
        raise ValueError('invalid sampling constraints')
    raw=pd.read_csv(events_csv,usecols=['timestamp','visitorid','event','itemid'])
    raw=raw[raw['event'].isin(['view','addtocart','transaction'])].copy()
    if raw.empty:
        raise ValueError('no supported events')
    raw['timestamp']=pd.to_numeric(raw['timestamp'],errors='coerce')
    raw=raw.dropna(subset=['timestamp','visitorid','itemid'])
    raw=raw.sort_values('timestamp',kind='stable').drop_duplicates(['visitorid','itemid'],keep='first')
    user_counts=raw.groupby('visitorid').size()
    eligible=user_counts[user_counts>=minimum_interactions].index
    if len(eligible)<4:
        raise ValueError('at least four users with sufficient interactions required')
    # Reproducible user selection; cap RAM and training time.
    selected=sorted(eligible.tolist())[:max_users]
    raw=raw[raw.visitorid.isin(selected)].copy()
    raw['user_id']=raw.visitorid.map(lambda x:'user-'+str(x))
    raw['item_id']=raw.itemid.map(lambda x:'item-'+str(x))
    categories={}
    for path in property_csvs:
        props=pd.read_csv(path,usecols=['timestamp','itemid','property','value'])
        props=props[props['property']=='categoryid']
        props=props.sort_values('timestamp').drop_duplicates('itemid',keep='first')
        # Never silently infer categories from anonymous numeric IDs.
        categories.update({'item-'+str(x):'category-'+str(v) for x,v in zip(props.itemid,props.value) if pd.notna(v)})
    raw['category']=raw.item_id.map(lambda x:categories.get(x,'unknown'))
    events=raw[['user_id','item_id','timestamp','category']].reset_index(drop=True)
    items=events[['item_id','category']].drop_duplicates('item_id').reset_index(drop=True)
    return events,items


def load_hillstrom(csv_path: str | Path, treatment_variant='Mens E-Mail'):
    """Compare ONE randomized email variant with no-email control.

    Causal features are strictly PRE-treatment (never include visit/spend/conversion).
    """
    if treatment_variant not in ('Mens E-Mail','Womens E-Mail'):
        raise ValueError('choose Mens E-Mail or Womens E-Mail')
    raw=pd.read_csv(csv_path)
    raw.columns=[str(col).strip().lower() for col in raw.columns]
    required={'segment','conversion','recency','history','mens','womens','newbie','zip_code','channel'}
    missing=required-set(raw.columns)
    if missing:
        raise ValueError('missing Hillstrom columns: '+', '.join(sorted(missing)))
    raw=raw[raw.segment.isin(['No E-Mail',treatment_variant])].copy()
    raw['treatment']=(raw.segment==treatment_variant).astype(int)
    fields=['recency','history','mens','womens','newbie','conversion']
    for field in fields:
        raw[field]=pd.to_numeric(raw[field],errors='raise')
    raw['zip_urban']=(raw.zip_code.astype(str).str.lower()=='urban').astype(int)
    raw['zip_suburban']=(raw.zip_code.astype(str).str.lower().isin(['suburban','surburban'])).astype(int)
    raw['channel_web']=(raw.channel.astype(str).str.lower()=='web').astype(int)
    raw['channel_multichannel']=(raw.channel.astype(str).str.lower()=='multichannel').astype(int)
    covariates=['recency','history','mens','womens','newbie','zip_urban','zip_suburban','channel_web','channel_multichannel']
    if len(raw.loc[raw.treatment==1])<10 or len(raw.loc[raw.treatment==0])<10:
        raise ValueError('need at least 10 observations per randomized arm')
    if raw[covariates+['conversion']].isna().any().any():
        raise ValueError('input has missing values in required model fields')
    if not set(raw.conversion.unique()).issubset({0,1}):
        raise ValueError('conversion outcome must be binary')
    return raw[covariates+['treatment','conversion']].reset_index(drop=True),covariates

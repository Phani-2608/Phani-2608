"""Evaluate locally supplied third-party datasets separately.

This script never downloads customer data or combines dataset populations.
"""
from __future__ import annotations
import argparse
import json
from core.datasets import load_retailrocket,load_hillstrom
from core.ranking import train_ranker
from core.experimentation import train_experiment


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='dataset',required=True)
    rr=sub.add_parser('retailrocket')
    rr.add_argument('events_csv')
    rr.add_argument('--properties',action='append',default=[],help='item_properties CSV file, may be repeated')
    rr.add_argument('--max-users',type=int,default=5000)
    hs=sub.add_parser('hillstrom')
    hs.add_argument('csv_file')
    hs.add_argument('--variant',choices=['Mens E-Mail','Womens E-Mail'],default='Mens E-Mail')
    args=parser.parse_args()
    if args.dataset=='retailrocket':
        events,items=load_retailrocket(args.events_csv,args.properties,args.max_users)
        result=train_ranker(events,items).metrics
        result['dataset']='RetailRocket (user-supplied third-party CSV)'
        result['interactions']=len(events)
    else:
        df,covariates=load_hillstrom(args.csv_file,args.variant)
        result=train_experiment(df,covariates=covariates,dataset_name='Hillstrom ('+args.variant+' vs No E-Mail)').metrics
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':
    main()

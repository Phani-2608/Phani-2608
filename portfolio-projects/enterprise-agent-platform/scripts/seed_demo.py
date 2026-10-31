"""Seed explicitly local demo-only SQLite database with invented cases."""
from __future__ import annotations
import json
from pathlib import Path
import os
from backend.store import CaseStore,ConflictError


def main():
    if os.getenv('DEMO_MODE')!='1':
        raise RuntimeError('Set DEMO_MODE=1 to seed synthetic cases; never run against production')
    db=CaseStore(os.getenv('DB_PATH','./runtime/cases.sqlite3'))
    cases=json.loads((Path(__file__).parent.parent/'data/demo_cases.json').read_text())
    for item in cases:
        try:
            record=db.create('alpha',item['case_id'],item['customer_id'],item['amount'],item['description'],'demo_seeder')
            for doc in item['evidence']:
                record=db.append_evidence('alpha',item['case_id'],doc['id'],doc['text'],'demo_seeder',record['revision'])
            print('Seeded',item['case_id'])
        except ConflictError:
            print('Already exists',item['case_id'])

if __name__=='__main__':
    main()

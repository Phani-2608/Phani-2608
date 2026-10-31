"""Recreate synthetic training artifacts and metrics with fixed seeds."""
import json
from core.pipeline import train_all,save,metrics
if __name__=='__main__':
    data=train_all(seed=42)
    save(data)
    print(json.dumps(metrics(data),indent=2))

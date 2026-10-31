"""Leakage-aware, abstaining land valuation training and prediction.

Accepts only caller-provided, lawfully sourced historical transactions. No fabricated data.
"""
from __future__ import annotations
from datetime import date
from typing import Any
import math

FEATURES=("latitude","longitude","acreage","distance_to_nairobi_km","distance_to_nearest_city_km","road_access_km","schools_3km","hospitals_5km")
MIN_TRAIN=40
MIN_TEST=10

def _number(value:Any)->float:
    v=float(value)
    if not math.isfinite(v): raise ValueError("Non-finite number")
    return v

def prepare(records:list[dict],cutoff:str):
    """Chronological split, with embargo at cutoff; never use future sale information as features."""
    date.fromisoformat(cutoff)
    train=[]; test=[]
    for row in records:
        try:
            sold=date.fromisoformat(str(row["sale_date"]))
            price=_number(row["sale_price_kes"])
            features=[_number(row[k]) for k in FEATURES]
            if price<=0 or features[2]<=0 or not -5<=features[0]<=5 or not 33<=features[1]<=42:continue
            if any(x<0 for x in features[3:]):continue
        except (KeyError,TypeError,ValueError,OverflowError):
            continue
        target=math.log(price/features[2])
        (train if sold<date.fromisoformat(cutoff) else test).append((features,target,row.get("parcel_id")))
    return train,test

def train_and_evaluate(records:list[dict],cutoff:str)->dict:
    """Train on past sales; hold out future sales and previously unseen parcel IDs."""
    try:
        import numpy as np
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.metrics import mean_absolute_error
    except ImportError as e:
        raise RuntimeError("Install the optional ML dependencies") from e
    train,test=prepare(records,cutoff)
    if len(train)<MIN_TRAIN or len(test)<MIN_TEST:
        return {"status":"insufficient_data","train_count":len(train),"test_count":len(test),
                "required_train":MIN_TRAIN,"required_test":MIN_TEST}
    train_ids={r[2] for r in train if r[2] is not None}
    test=[r for r in test if r[2] is None or r[2] not in train_ids]
    if len(test)<MIN_TEST:
        return {"status":"insufficient_independent_test_data","test_count":len(test)}
    x=np.asarray([r[0] for r in train]); y=np.asarray([r[1] for r in train])
    xt=np.asarray([r[0] for r in test]); yt=np.asarray([r[1] for r in test])
    model=HistGradientBoostingRegressor(max_iter=120,max_leaf_nodes=12,l2_regularization=2,random_state=42)
    model.fit(x,y)
    predictions=model.predict(xt)
    baseline=np.full(len(yt),np.median(y))
    mae=float(mean_absolute_error(np.exp(yt),np.exp(predictions)))
    baseline_mae=float(mean_absolute_error(np.exp(yt),np.exp(baseline)))
    return {"status":"evaluated_not_deployed","train_count":len(train),"test_count":len(test),
            "metric":"MAE_KES_per_acre","mae":round(mae,2),"baseline_mae":round(baseline_mae,2),
            "beats_baseline":mae<baseline_mae,
            "warning":"Temporal test alone is insufficient. Spatial holdout, calibration and provenance audits required before deployment."}

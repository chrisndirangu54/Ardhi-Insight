"""Strict provenance and spatial-temporal holdout diagnostics for land transactions."""
from __future__ import annotations
from collections import Counter
from datetime import date
from math import floor, isfinite
from typing import Any

REQUIRED=("sale_date","sale_price_kes","acreage","latitude","longitude","source_url","source_type","license","parcel_id")
def validate_transactions(records:list[dict])->dict:
    accepted=[];rejected=[]
    seen=set()
    for i,r in enumerate(records):
        try:
            missing=[k for k in REQUIRED if not r.get(k)]
            if missing:raise ValueError("missing "+",".join(missing))
            d=date.fromisoformat(str(r["sale_date"]))
            price=float(r["sale_price_kes"]); acres=float(r["acreage"])
            lat=float(r["latitude"]);lon=float(r["longitude"])
            if not all(map(isfinite,(price,acres,lat,lon))) or price<=0 or acres<=0 or not -5<=lat<=5 or not 33<=lon<=42:
                raise ValueError("invalid numeric values or geographic bounds")
            if r["source_type"] not in ("registered_transaction","documented_sale"):
                raise ValueError("asking prices are not confirmed sales")
            if not str(r["source_url"]).startswith("https://"):
                raise ValueError("source_url must be HTTPS")
            key=(r["parcel_id"],d.isoformat(),price)
            if key in seen:raise ValueError("duplicate sale")
            seen.add(key)
            accepted.append(r)
        except (ValueError,TypeError,KeyError,OverflowError) as exc:
            rejected.append({"row":i,"reason":str(exc)})
    return {"accepted":accepted,"rejected":rejected,"accepted_count":len(accepted),"rejected_count":len(rejected)}
def spatial_cell(latitude:float,longitude:float,cell_degrees:float=0.25)->str:
    return f"{floor(latitude/cell_degrees)}:{floor(longitude/cell_degrees)}"
def holdout_diagnostics(records:list[dict],cutoff:str)->dict:
    date.fromisoformat(cutoff)
    valid=validate_transactions(records)["accepted"]
    train=[r for r in valid if str(r["sale_date"])<cutoff]
    test=[r for r in valid if str(r["sale_date"])>=cutoff]
    train_cells={spatial_cell(float(r["latitude"]),float(r["longitude"])) for r in train}
    spatial_test=[r for r in test if spatial_cell(float(r["latitude"]),float(r["longitude"])) not in train_cells]
    return {"train_count":len(train),"future_test_count":len(test),
            "spatially_unseen_future_test_count":len(spatial_test),
            "distinct_training_cells":len(train_cells),
            "warning":"Spatial cell holdout is diagnostic; an operational evaluation needs enough independent regions and time periods."}

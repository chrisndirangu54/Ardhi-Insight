"""Transparent investment readiness, without invented hazard or title scores."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(prefix="/api/risk",tags=["risk"])
class Evidence(BaseModel):
    status:Literal["verified","unverified","unavailable"]
    source:str|None=None
    observed_at:str|None=None
    description:str|None=None
class RiskInput(BaseModel):
    title:Evidence
    survey:Evidence
    environmental:Evidence
    comparable_sales:Evidence
    zoning:Evidence
    road_access:Evidence
def _fresh(e:Evidence,days:int=365)->bool:
    if e.status!="verified" or not e.observed_at or not e.source:return False
    try:
        dt=datetime.fromisoformat(e.observed_at.replace("Z","+00:00"))
        if dt.tzinfo is None:return False
        age=(datetime.now(timezone.utc)-dt.astimezone(timezone.utc)).total_seconds()/86400
        return 0<=age<=days
    except ValueError:return False
@router.post("/readiness")
def readiness(r:RiskInput):
    evidence=r.model_dump()
    stale=[name for name in ("environmental","comparable_sales","zoning","road_access") if evidence[name]["status"]=="verified" and not _fresh(getattr(r,name))]
    missing=[name for name in evidence if evidence[name]["status"]!="verified"]
    critical=[name for name in ("title","survey","environmental") if name in missing or name in stale]
    return {"status":"insufficient_evidence" if critical else ("review_required" if missing or stale else "evidence_submitted"),
            "missing_or_unverified":missing,"stale_or_undated":stale,"critical_gaps":critical,
            "warning":"User-supplied evidence is not independently authenticated. Evidence readiness is not an investment recommendation, hazard classification or legal clearance."}

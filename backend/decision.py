"""Explainable, user-weighted multi-criteria parcel comparison.

Not a valuation, safety score, investment recommendation or legal clearance.
All criteria must be independently supplied and evidence gaps are explicit.
"""
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel,Field
from typing import Literal
router=APIRouter(prefix="/api/decision",tags=["decision"])
CRITERIA=("affordability","amenity_access","road_access","development_readiness","environmental_evidence")
class EvidenceScore(BaseModel):
    value:float|None=Field(default=None,ge=0,le=100)
    source:str|None=None
    verified:bool=False
class Candidate(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    criteria:dict[str,EvidenceScore]
    title_verified:bool=False
    survey_verified:bool=False
class DecisionRequest(BaseModel):
    first:Candidate
    second:Candidate
    weights:dict[str,float]
def evaluate(r:DecisionRequest)->dict:
    if set(r.weights)!=set(CRITERIA):return {"status":"invalid_weights","reason":"Weights must cover exactly: "+", ".join(CRITERIA)}
    if any(v<0 or v>1 for v in r.weights.values()) or abs(sum(r.weights.values())-1)>1e-6:
        return {"status":"invalid_weights","reason":"Weights must be nonnegative and sum to 1"}
    output=[]
    for c in (r.first,r.second):
        missing=[k for k in CRITERIA if k not in c.criteria or c.criteria[k].value is None or not c.criteria[k].verified or not c.criteria[k].source]
        critical=[]
        if not c.title_verified:critical.append("official_title_verification")
        if not c.survey_verified:critical.append("survey_verification")
        if missing:critical.append("incomplete_criteria_evidence")
        score=None if critical else round(sum(r.weights[k]*c.criteria[k].value for k in CRITERIA),2)
        output.append({"name":c.name,"score":score,"critical_gaps":critical,"missing_or_unverified_criteria":missing})
    if any(o["score"] is None for o in output):
        return {"status":"abstained","candidates":output,
                "note":"No ranking because one or both parcels lack verified critical evidence."}
    difference=round(output[0]["score"]-output[1]["score"],2)
    contributions={k:round(r.weights[k]*(r.first.criteria[k].value-r.second.criteria[k].value),2) for k in CRITERIA}
    return {"status":"scored","candidates":output,"score_difference_first_minus_second":difference,
            "weighted_contributions":contributions,
            "note":"Scores are user-provided preferences and verified-input indicators, not objective property quality, price forecasts or investment advice."}
@router.post("/compare")
def compare(r:DecisionRequest):
    return evaluate(r)
@router.post("/sensitivity")
def sensitivity(r:DecisionRequest):
    base=evaluate(r)
    if base["status"]!="scored":return {"status":"abstained","base":base}
    # One-at-a-time perturbation; redistribute remaining weights proportionally.
    scenarios=[]
    for key in CRITERIA:
        for change in (-0.1,0.1):
            new=max(0,min(1,r.weights[key]+change))
            other_sum=sum(v for k,v in r.weights.items() if k!=key)
            if other_sum==0:continue
            weights={k:(new if k==key else v*(1-new)/other_sum) for k,v in r.weights.items()}
            rr=DecisionRequest(first=r.first,second=r.second,weights=weights)
            result=evaluate(rr)
            scenarios.append({"criterion":key,"weight":round(new,3),
                              "difference":result.get("score_difference_first_minus_second")})
    values=[s["difference"] for s in scenarios if s["difference"] is not None]
    return {"status":"computed","base":base,"scenarios":scenarios,
            "rank_reversal_observed":bool(values and min(values)<0<max(values)),
            "warning":"Sensitivity explores preference uncertainty only, not missing evidence, measurement error or future market changes."}

"""Property decision support. Explainable outputs; no invented title, hazards or valuation."""
from __future__ import annotations
import math
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
router=APIRouter(prefix="/api/intelligence",tags=["intelligence"])
class Property(BaseModel):
    price_kes:float=Field(gt=0)
    acreage:float=Field(gt=0)
    latitude:float=Field(ge=-5,le=5)
    longitude:float=Field(ge=33,le=42)
    title_search_confirmed:bool=False
    survey_confirmed:bool=False
    seller_identity_confirmed:bool=False
    access_confirmed:bool=False
    zoning_confirmed:bool=False
    environmental_report_confirmed:bool=False
    description:str=""
class Comparable(BaseModel):
    price_kes:float=Field(gt=0)
    acreage:float=Field(gt=0)
    latitude:float=Field(ge=-5,le=5)
    longitude:float=Field(ge=33,le=42)
    verified_transaction:bool=False
    transaction_date:str|None=None
class CompareRequest(BaseModel):
    target:Property
    comparables:list[Comparable]=Field(default_factory=list,max_length=100)
@router.post("/due-diligence")
def due_diligence(p:Property):
    checks={
        "official_title_search":p.title_search_confirmed,
        "survey_and_boundaries":p.survey_confirmed,
        "seller_identity":p.seller_identity_confirmed,
        "legal_access":p.access_confirmed,
        "zoning_and_permitted_use":p.zoning_confirmed,
        "environmental_screening":p.environmental_report_confirmed
    }
    return {"status":"checklist_only","completed":sum(checks.values()),"total":len(checks),
            "outstanding":[k for k,v in checks.items() if not v],
            "warning":"User-reported checks are not independently authenticated. Obtain official evidence."}
@router.post("/listing-quality")
def listing_quality(p:Property):
    warnings=[]
    if len(p.description.strip())<80:warnings.append("Listing description is brief; request location, boundaries, tenure and permitted use.")
    if not p.title_search_confirmed:warnings.append("Official title search not confirmed.")
    if not p.survey_confirmed:warnings.append("Survey and boundary evidence not confirmed.")
    if not p.seller_identity_confirmed:warnings.append("Seller identity not confirmed.")
    for term in ("guaranteed return","risk free","double your money","guaranteed appreciation"):
        if term in p.description.lower():warnings.append("Promotional claim requires independent substantiation: "+term)
    return {"flags":warnings,"price_per_acre_kes":round(p.price_kes/p.acreage,2),
            "note":"Flags are heuristics, not evidence of fraud or authenticity."}
@router.post("/comparables")
def comparables(r:CompareRequest):
    from backend.geospatial import km
    verified=[c for c in r.comparables if c.verified_transaction and c.transaction_date]
    ranked=sorted(verified,key=lambda c:km(r.target.latitude,r.target.longitude,c.latitude,c.longitude))[:20]
    if len(ranked)<3:
        return {"status":"insufficient_verified_comparables","count":len(ranked),
                "note":"Do not infer a market valuation from unverified asking prices."}
    prices=sorted(c.price_kes/c.acreage for c in ranked)
    median=(prices[(len(prices)-1)//2]+prices[len(prices)//2])/2
    return {"status":"descriptive_only","count":len(ranked),"median_verified_price_per_acre_kes":round(median,2),
            "target_asking_price_per_acre_kes":round(r.target.price_kes/r.target.acreage,2),
            "note":"Unadjusted comparable median, not a professional appraisal; date, tenure and property differences matter."}
@router.get("/forecast/readiness")
def forecast_readiness():
    return {"status":"not_available","horizons_years":[1,3,5,10],
            "required":["Licensed transaction history","Spatial and temporal holdout tests",
                        "Calibrated predictive intervals","Monitoring for geographic drift"],
            "message":"No credible forecast can be generated until a validated trained model is deployed."}
@router.get("/imagery/readiness")
def imagery_readiness():
    return {"status":"not_configured","capabilities":["Sentinel-2/Landsat change detection",
             "land-use classification","built-up expansion","vegetation change"],
            "requirements":["Licensed imagery or open EO imagery access","Cloud masking",
             "Time-aligned observations","Independent ground truth and validation"],
            "message":"Satellite change detection has not been run; no land-use inference is claimed."}

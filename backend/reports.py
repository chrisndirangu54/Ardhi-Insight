"""Safe property report assembled from independently disclosed inputs."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.intelligence import Property, due_diligence, listing_quality
from backend.geospatial import proximity
router=APIRouter(prefix="/api/reports",tags=["reports"])
class ReportRequest(BaseModel):
    property:Property
    reference:str=Field(default="Unspecified",max_length=120)
@router.post("/property")
def property_report(r:ReportRequest):
    p=r.property
    return {"reference":r.reference,"price_per_acre_kes":round(p.price_kes/p.acreage,2),
            "nearest_cities":proximity(p.latitude,p.longitude)["centres"][:3],
            "due_diligence":due_diligence(p),"listing_quality":listing_quality(p),
            "environment":{"status":"not_assessed","action":"Request Regen Insight screening and inspect source methodology"},
            "forecast":{"status":"unavailable","reason":"No validated historical price model is deployed"},
            "ownership":{"status":"not_independently_verified","action":"Authorized official Ardhisasa search"},
            "disclaimer":"Research aid only, not a title certificate, survey, valuation or investment recommendation."}

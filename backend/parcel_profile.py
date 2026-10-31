"""Land-use, amenity, security-evidence and two-parcel comparison.

Indicators are descriptive. No crime risk, legal zoning or safety determination
is inferred from absence of records or nearby facilities.
"""
from __future__ import annotations
from math import asin,cos,radians,sin,sqrt
from fastapi import APIRouter
from pydantic import BaseModel,Field
router=APIRouter(prefix="/api/parcel-profile",tags=["parcel-profile"])
class Amenity(BaseModel):
    name:str
    category:str
    latitude:float=Field(ge=-90,le=90)
    longitude:float=Field(ge=-180,le=180)
    source:str="user_supplied"
class LandUse(BaseModel):
    observed_class:str|None=None
    classification_source:str|None=None
    classification_date:str|None=None
    permitted_use:str|None=None
    zoning_source:str|None=None
    zoning_verified:bool=False
    constraints:list[str]=Field(default_factory=list)
class SecurityEvidence(BaseModel):
    police_station_verified:bool=False
    street_lighting_verified:bool=False
    gated_access_verified:bool=False
    emergency_access_verified:bool=False
    incident_dataset_source:str|None=None
    incident_dataset_period:str|None=None
    incident_count:int|None=Field(default=None,ge=0)
class Parcel(BaseModel):
    label:str=Field(min_length=1,max_length=100)
    latitude:float=Field(ge=-5,le=5)
    longitude:float=Field(ge=33,le=42)
    acreage:float=Field(gt=0)
    asking_price_kes:float=Field(gt=0)
    amenities:list[Amenity]=Field(default_factory=list,max_length=500)
    land_use:LandUse=Field(default_factory=LandUse)
    security:SecurityEvidence=Field(default_factory=SecurityEvidence)
class Compare(BaseModel):
    first:Parcel
    second:Parcel
def distance_km(a:float,b:float,c:float,d:float)->float:
    x=radians(c-a);y=radians(d-b)
    h=sin(x/2)**2+cos(radians(a))*cos(radians(c))*sin(y/2)**2
    return 6371.0088*2*asin(min(1,sqrt(h)))
def profile(p:Parcel)->dict:
    grouped={}
    for item in p.amenities:
        d=distance_km(p.latitude,p.longitude,item.latitude,item.longitude)
        key=item.category.strip().lower()
        if not key:continue
        grouped.setdefault(key,[]).append({"name":item.name,"distance_km":round(d,3),"source":item.source})
    amenities={}
    for key,items in grouped.items():
        ordered=sorted(items,key=lambda x:x["distance_km"])
        amenities[key]={"within_1km":sum(x["distance_km"]<=1 for x in ordered),
                        "within_3km":sum(x["distance_km"]<=3 for x in ordered),
                        "within_5km":sum(x["distance_km"]<=5 for x in ordered),
                        "nearest":ordered[:3]}
    land=p.land_use
    security=p.security
    return {"label":p.label,"coordinates":{"latitude":p.latitude,"longitude":p.longitude},
            "acreage":p.acreage,"asking_price_kes":p.asking_price_kes,
            "asking_price_per_acre_kes":round(p.asking_price_kes/p.acreage,2),
            "amenity_profile":{"categories":amenities,"status":"supplied_observations_only",
                               "warning":"Counts are incomplete unless a complete amenity dataset was supplied; straight-line distances are not travel times."},
            "land_use_profile":{"observed_class":land.observed_class,"classification_source":land.classification_source,
                "classification_date":land.classification_date,"permitted_use":land.permitted_use,
                "zoning_verified":land.zoning_verified,"zoning_source":land.zoning_source,
                "constraints":land.constraints,"warning":"Observed land cover does not establish legal zoning or permitted use."},
            "security_profile":{"police_station_verified":security.police_station_verified,
                "street_lighting_verified":security.street_lighting_verified,
                "gated_access_verified":security.gated_access_verified,
                "emergency_access_verified":security.emergency_access_verified,
                "incident_count":security.incident_count,"incident_dataset_source":security.incident_dataset_source,
                "incident_dataset_period":security.incident_dataset_period,
                "status":"evidence_inventory_only",
                "warning":"No crime probability, neighborhood safety rating or comparative crime risk can be inferred without representative, geocoded, time-aligned incident data."}}
@router.post("/analyze")
def analyze(p:Parcel):
    return profile(p)
@router.post("/compare")
def compare(r:Compare):
    a=profile(r.first);b=profile(r.second)
    categories=sorted(set(a["amenity_profile"]["categories"])|set(b["amenity_profile"]["categories"]))
    amenity_comparison={}
    for category in categories:
        left=a["amenity_profile"]["categories"].get(category,{})
        right=b["amenity_profile"]["categories"].get(category,{})
        amenity_comparison[category]={"first_within_3km":left.get("within_3km",0),
                                     "second_within_3km":right.get("within_3km",0)}
    return {"first":a,"second":b,
            "differences":{"asking_price_kes":round(r.first.asking_price_kes-r.second.asking_price_kes,2),
                           "asking_price_per_acre_kes":round(a["asking_price_per_acre_kes"]-b["asking_price_per_acre_kes"],2),
                           "area_acres":round(r.first.acreage-r.second.acreage,4),
                           "distance_between_parcels_km":round(distance_km(r.first.latitude,r.first.longitude,r.second.latitude,r.second.longitude),3),
                           "amenities":amenity_comparison},
            "conclusion":"Descriptive comparison only. Neither parcel is automatically ranked safer, more valuable, or legally developable.",
            "limitations":["Asking prices are not completed sale prices.","Amenity inputs may be incomplete or biased.",
                           "Crime and zoning cannot be inferred from unverified indicators."]}

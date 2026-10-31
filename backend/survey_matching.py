"""Compare provisional boundary against explicitly supplied authorized survey geometries.

Geometry matching is not legal title verification, survey authentication or
evidence of ownership. No private cadastral service is accessed.
"""
from __future__ import annotations
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from typing import Any
router=APIRouter(prefix="/api/boundaries",tags=["boundaries"])
class SurveyCandidate(BaseModel):
    parcel_reference:str=Field(min_length=1,max_length=120)
    geometry:dict[str,Any]
    source_name:str=Field(min_length=1)
    source_reference:str=Field(min_length=1)
    authorization_confirmed:bool=False
class MatchRequest(BaseModel):
    provisional_geometry:dict[str,Any]
    candidates:list[SurveyCandidate]=Field(max_length=100)
def match(request:MatchRequest)->dict:
    try:
        from shapely.geometry import shape
        from shapely.ops import transform
        from pyproj import Transformer,CRS
    except ImportError:raise HTTPException(503,"Install shapely and pyproj for cadastral geometry matching")
    def parse(geom):
        if geom.get("type") not in ("Polygon","MultiPolygon"):raise ValueError("Polygon geometry required")
        obj=shape(geom)
        if not obj.is_valid or obj.is_empty or obj.area<=0:raise ValueError("Invalid or self-intersecting polygon")
        minx,miny,maxx,maxy=obj.bounds
        if not (33<=minx<=maxx<=42 and -5<=miny<=maxy<=5):raise ValueError("Coordinates outside configured Kenya bounds")
        return obj
    try:
        provisional=parse(request.provisional_geometry)
        center=provisional.centroid
        zone=int((center.x+180)//6)+1
        epsg=(32700 if center.y<0 else 32600)+zone
        transformer=Transformer.from_crs("EPSG:4326",CRS.from_epsg(epsg),always_xy=True).transform
        projected=transform(transformer,provisional)
        rows=[]
        for candidate in request.candidates:
            if not candidate.authorization_confirmed:
                rows.append({"parcel_reference":candidate.parcel_reference,"status":"authorization_not_confirmed"})
                continue
            try:
                other=transform(transformer,parse(candidate.geometry))
                intersection=projected.intersection(other).area
                union=projected.union(other).area
                iou=intersection/union if union else 0
                coverage=intersection/projected.area
                centroid_distance=projected.centroid.distance(other.centroid)
                area_ratio=min(projected.area,other.area)/max(projected.area,other.area)
                rows.append({"parcel_reference":candidate.parcel_reference,"source_name":candidate.source_name,
                             "source_reference":candidate.source_reference,"status":"candidate_geometry_compared",
                             "intersection_over_union":round(iou,4),
                             "provisional_coverage":round(coverage,4),
                             "area_similarity":round(area_ratio,4),
                             "centroid_distance_m":round(centroid_distance,2),
                             "review_priority":round(.65*iou+.25*area_ratio+.10*max(0,1-centroid_distance/200),4)})
            except (ValueError,TypeError,KeyError):
                rows.append({"parcel_reference":candidate.parcel_reference,"status":"invalid_candidate_geometry"})
        rows.sort(key=lambda x:x.get("review_priority",-1),reverse=True)
        return {"status":"candidate_search_only","matches":rows,
                "warning":"Scores only prioritize human review. No cadastral registry was queried and no ownership, title, survey authenticity or legal boundary was verified."}
    except (ValueError,TypeError,KeyError) as e:raise HTTPException(422,str(e))
@router.post("/match-survey-records")
def match_survey_records(request:MatchRequest):
    return match(request)

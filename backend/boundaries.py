"""Provisional boundary from walking GPS observations; never cadastral proof."""
from __future__ import annotations
from math import radians,cos,sin,asin,sqrt
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
router=APIRouter(prefix="/api/boundaries",tags=["boundaries"])
class Fix(BaseModel):
    latitude:float=Field(ge=-90,le=90)
    longitude:float=Field(ge=-180,le=180)
    accuracy_m:float=Field(gt=0,le=10000)
    timestamp:str|None=None
class Track(BaseModel):
    points:list[Fix]=Field(min_length=3,max_length=10000)
    maximum_accuracy_m:float=Field(default=25,gt=0,le=100)
def meters(a:Fix,b:Fix)->float:
    x=radians(b.latitude-a.latitude);y=radians(b.longitude-a.longitude)
    h=sin(x/2)**2+cos(radians(a.latitude))*cos(radians(b.latitude))*sin(y/2)**2
    return 12742017.6*asin(min(1,sqrt(h)))
def build(track:Track)->dict:
    accepted=[p for p in track.points if p.accuracy_m<=track.maximum_accuracy_m]
    if len(accepted)<3:raise ValueError("At least three sufficiently accurate GPS points required")
    # Reject implausible long jumps and preserve order: no automatic convex hull.
    jumps=[meters(a,b) for a,b in zip(accepted,accepted[1:])]
    if any(d>500 for d in jumps):raise ValueError("GPS jump above 500m; review or split track")
    if meters(accepted[0],accepted[-1])>max(30,track.maximum_accuracy_m*2):
        raise ValueError("Walk must end near its starting point")
    ring=[[p.longitude,p.latitude] for p in accepted]
    if ring[0]!=ring[-1]:ring.append(ring[0])
    # Shoelace in local metric projection for an approximate size.
    lat0=sum(p.latitude for p in accepted)/len(accepted)
    lon0=sum(p.longitude for p in accepted)/len(accepted)
    xy=[((p.longitude-lon0)*111320*cos(radians(lat0)),(p.latitude-lat0)*110574) for p in accepted]
    area=abs(sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy))))/2
    if area<1:raise ValueError("Degenerate or near-zero polygon")
    return {"type":"Feature","geometry":{"type":"Polygon","coordinates":[ring]},
            "properties":{"verification_status":"unverified_gps_walk","area_estimate_sqm":round(area,1),
                          "area_estimate_acres":round(area/4046.8564224,4),
                          "accepted_points":len(accepted),"rejected_points":len(track.points)-len(accepted),
                          "max_reported_accuracy_m":max(p.accuracy_m for p in accepted),
                          "warning":"Approximate boundary only; not proof of title, cadastral position, legal area or survey accuracy. Review for self-intersections and obtain licensed survey verification."}}
@router.post("/from-gps")
def from_gps(track:Track):
    try:return build(track)
    except ValueError as e:raise HTTPException(422,str(e))

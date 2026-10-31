"""Location features using documented public OSM Overpass endpoints.

Calls are opt-in; no geospatial features are silently replaced with zero on failure.
"""
from __future__ import annotations
import math
import httpx
from fastapi import APIRouter, HTTPException, Query
router=APIRouter(prefix="/api/geospatial",tags=["geospatial"])
CENTRES={"Nairobi":(-1.286389,36.817223),"Mombasa":(-4.0435,39.6682),
         "Kisumu":(-0.0917,34.768),"Nakuru":(-0.3031,36.08),
         "Eldoret":(0.5143,35.2698),"Thika":(-1.0333,37.0693)}
def km(a,b,c,d):
    p1,p2=math.radians(a),math.radians(c)
    h=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(d-b)/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(h)))
@router.get("/urban-proximity")
def proximity(latitude:float=Query(ge=-5,le=5),longitude:float=Query(ge=33,le=42)):
    ordered=sorted(({"city":n,"straight_line_km":round(km(latitude,longitude,*p),2)} for n,p in CENTRES.items()),key=lambda x:x["straight_line_km"])
    return {"centres":ordered,"method":"haversine","note":"Not driving distance; access depends on road network and conditions."}
@router.get("/amenities")
async def amenities(latitude:float=Query(ge=-5,le=5),longitude:float=Query(ge=33,le=42),radius_m:int=Query(default=2000,ge=100,le=5000)):
    query=f'[out:json][timeout:15];(nwr(around:{radius_m},{latitude},{longitude})["amenity"~"^(school|hospital|clinic)$"];);out center;'
    try:
        async with httpx.AsyncClient(timeout=20,follow_redirects=False) as client:
            resp=await client.post("https://overpass.kumi.systems/api/interpreter",data={"data":query})
            resp.raise_for_status()
            elements=resp.json()["elements"]
    except (httpx.HTTPError,KeyError,ValueError,TypeError):
        raise HTTPException(503,"OpenStreetMap amenity data currently unavailable")
    counts={"school":0,"hospital":0,"clinic":0}
    for item in elements:
        kind=item.get("tags",{}).get("amenity")
        if kind in counts:counts[kind]+=1
    return {"counts":counts,"radius_m":radius_m,"source":"OpenStreetMap contributors via Overpass",
            "note":"Incomplete mapping is possible. Counts are not a guarantee of service availability."}

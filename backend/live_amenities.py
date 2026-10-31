"""Live OSM amenity discovery with bounded query and explicit provenance."""
from __future__ import annotations
import httpx
from fastapi import APIRouter,HTTPException,Query
from backend.parcel_profile import distance_km
router=APIRouter(prefix="/api/parcel-profile",tags=["parcel-profile"])
CATEGORIES=("school","college","university","hospital","clinic","pharmacy","police","bank","marketplace","fuel","bus_station")
OVERPASS="https://overpass.kumi.systems/api/interpreter"
@router.get("/live-amenities")
async def live_amenities(latitude:float=Query(ge=-5,le=5),longitude:float=Query(ge=33,le=42),radius_m:int=Query(default=3000,ge=250,le=5000)):
    query=f'[out:json][timeout:20];nwr(around:{radius_m},{latitude},{longitude})["amenity"~"^({"|".join(CATEGORIES)})$"];out center 500;'
    try:
        async with httpx.AsyncClient(timeout=25,follow_redirects=False) as client:
            resp=await client.post(OVERPASS,data={"data":query})
            resp.raise_for_status()
            elements=resp.json().get("elements",[])
    except (httpx.HTTPError,ValueError,TypeError):
        raise HTTPException(503,"Live OpenStreetMap discovery unavailable; no counts inferred.")
    seen=set();amenities=[]
    for item in elements:
        tags=item.get("tags") or {}
        kind=tags.get("amenity")
        point=item.get("center") or item
        lat=point.get("lat");lon=point.get("lon")
        if kind not in CATEGORIES or not isinstance(lat,(float,int)) or not isinstance(lon,(float,int)):continue
        identity=(item.get("type"),item.get("id"))
        if identity in seen:continue
        seen.add(identity)
        amenities.append({"name":tags.get("name") or kind.replace("_"," ").title(),
                          "category":kind,"latitude":lat,"longitude":lon,
                          "distance_km":round(distance_km(latitude,longitude,lat,lon),3),
                          "source":"OpenStreetMap","osm_type":item.get("type"),"osm_id":item.get("id")})
    amenities.sort(key=lambda a:a["distance_km"])
    return {"status":"available","amenities":amenities,"radius_m":radius_m,
            "source":"OpenStreetMap contributors via Overpass",
            "truncated":len(elements)>=500,
            "note":"Coverage is incomplete and may be outdated; distances are straight-line, not travel times. Police proximity does not measure crime or safety."}

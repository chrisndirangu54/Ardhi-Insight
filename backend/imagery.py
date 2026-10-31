"""Open geospatial image catalog discovery (STAC), not unvalidated image inference."""
from __future__ import annotations
from fastapi import APIRouter,HTTPException,Query
import httpx
router=APIRouter(prefix="/api/imagery",tags=["imagery"])
STAC_URL="https://earth-search.aws.element84.com/v1/search"
@router.get("/sentinel-scenes")
async def sentinel_scenes(latitude:float=Query(ge=-5,le=5),longitude:float=Query(ge=33,le=42),year:int=Query(ge=2017,le=2100),limit:int=Query(default=10,ge=1,le=30)):
    # Public Earth Search STAC catalog. Search only; imagery not downloaded or classified.
    delta=0.015
    body={"collections":["sentinel-2-l2a"],"bbox":[longitude-delta,latitude-delta,longitude+delta,latitude+delta],
          "datetime":f"{year}-01-01T00:00:00Z/{year}-12-31T23:59:59Z","limit":limit,
          "query":{"eo:cloud_cover":{"lt":35}}}
    try:
        async with httpx.AsyncClient(timeout=18,follow_redirects=False) as client:
            response=await client.post(STAC_URL,json=body)
            response.raise_for_status()
            data=response.json()
    except (httpx.HTTPError,ValueError):
        raise HTTPException(503,"Satellite catalog temporarily unavailable")
    items=[]
    for f in data.get("features",[]):
        props=f.get("properties",{})
        items.append({"id":f.get("id"),"datetime":props.get("datetime"),
                      "cloud_cover_pct":props.get("eo:cloud_cover"),
                      "collection":f.get("collection"),
                      "catalog_url":f.get("links",[{}])[0].get("href")})
    return {"items":items,"source":"Element 84 Earth Search STAC / Sentinel-2 L2A",
            "status":"catalog_discovery_only","note":"No change detection or parcel boundary inference has been performed."}

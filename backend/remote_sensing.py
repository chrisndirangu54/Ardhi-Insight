"""Sentinel-2 spectral indices and paired-scene change diagnostics.

Consumes reflectance observations extracted from co-registered, cloud-masked pixels.
Does not infer land use or urban expansion from indices alone.
"""
from __future__ import annotations
import math
from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(prefix="/api/remote-sensing",tags=["remote-sensing"])
class Bands(BaseModel):
    blue:float=Field(ge=0,le=1)
    green:float=Field(ge=0,le=1)
    red:float=Field(ge=0,le=1)
    nir:float=Field(ge=0,le=1)
    swir1:float=Field(ge=0,le=1)
    swir2:float=Field(ge=0,le=1)
    cloud_masked:bool=True
    acquisition_date:str|None=None
    scene_id:str|None=None
class Pair(BaseModel):
    before:Bands
    after:Bands
def ratio(a:float,b:float)->float|None:
    return round((a-b)/(a+b),5) if a+b>1e-9 else None
def indices(b:Bands)->dict:
    return {"ndvi":ratio(b.nir,b.red),"ndwi":ratio(b.green,b.nir),
            "ndbi":ratio(b.swir1,b.nir),"nbr":ratio(b.nir,b.swir2),
            "source_scene":b.scene_id,"acquisition_date":b.acquisition_date}
@router.post("/indices")
def spectral_indices(b:Bands):
    if not b.cloud_masked:return {"status":"rejected","reason":"Pixel must be cloud and shadow screened"}
    return {"status":"computed","indices":indices(b),
            "note":"Indices are physical indicators, not validated land-cover labels."}
@router.post("/change")
def change(p:Pair):
    if not p.before.cloud_masked or not p.after.cloud_masked:
        return {"status":"rejected","reason":"Both observations require cloud and shadow masking"}
    if not p.before.acquisition_date or not p.after.acquisition_date:
        return {"status":"rejected","reason":"Acquisition dates required for temporal comparison"}
    if p.before.acquisition_date>=p.after.acquisition_date:
        return {"status":"rejected","reason":"Before acquisition must precede after"}
    a=indices(p.before);b=indices(p.after)
    delta={key:round(b[key]-a[key],5) if a[key] is not None and b[key] is not None else None for key in ("ndvi","ndwi","ndbi","nbr")}
    return {"status":"computed","before":a,"after":b,"delta":delta,
            "warnings":["Verify pixel co-registration, atmospheric correction and seasonal comparability.",
                        "Index change alone cannot establish construction, flooding or vegetation loss."]}

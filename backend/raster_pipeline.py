"""Rasterio-based Sentinel-2 GeoTIFF feature extraction.

Input files must be downloaded from authorized sources and supplied locally.
All band files must share grid/CRS; valid pixels are screened with SCL.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np

REQUIRED=("B03","B04","B08","B11","B12","SCL")
VALID_SCL={4,5,6,7} # vegetation, bare, water, unclassified (cloud/shadow excluded)
def safe_index(a:np.ndarray,b:np.ndarray)->np.ndarray:
    denominator=a+b
    return np.divide(a-b,denominator,out=np.full(a.shape,np.nan,dtype=np.float32),where=np.abs(denominator)>1e-7)
def extract_scene(bands:dict[str,str],reflectance_scale:float=10000.0)->dict[str,Any]:
    try:
        import rasterio
    except ImportError as exc:
        raise RuntimeError("Install rasterio for raster processing") from exc
    if not all(k in bands for k in REQUIRED):raise ValueError("Required Sentinel-2 bands: "+", ".join(REQUIRED))
    arrays={};metadata=None
    for name in REQUIRED:
        path=Path(bands[name])
        if not path.is_file():raise FileNotFoundError(path)
        with rasterio.open(path) as src:
            current=(src.crs,src.transform,src.width,src.height)
            if metadata is None:metadata=current
            elif current!=metadata:raise ValueError("Bands must have identical CRS, transform, width and height; resample explicitly beforehand")
            arrays[name]=src.read(1,masked=True)
    scl=np.asarray(arrays["SCL"].filled(0))
    valid=np.isin(scl,list(VALID_SCL))
    scaled={}
    for name in ("B03","B04","B08","B11","B12"):
        arr=arrays[name]
        valid &= ~np.ma.getmaskarray(arr)
        x=np.asarray(arr.filled(0),dtype=np.float32)/reflectance_scale
        valid &= np.isfinite(x)&(x>=0)&(x<=1)
        scaled[name]=x
    ndvi=safe_index(scaled["B08"],scaled["B04"])
    ndwi=safe_index(scaled["B03"],scaled["B08"])
    ndbi=safe_index(scaled["B11"],scaled["B08"])
    nbr=safe_index(scaled["B08"],scaled["B12"])
    result={"status":"computed","width":metadata[2],"height":metadata[3],
            "valid_pixel_count":int(valid.sum()),"total_pixel_count":int(valid.size),
            "valid_fraction":float(valid.mean()),"indices":{}}
    for name,values in (("ndvi",ndvi),("ndwi",ndwi),("ndbi",ndbi),("nbr",nbr)):
        sample=values[valid & np.isfinite(values)]
        result["indices"][name]={"mean":float(sample.mean()),"median":float(np.median(sample)),
                                  "std":float(sample.std()),"valid_count":int(sample.size)} if sample.size else None
    result["note"]="Scene-wide statistics; not parcel-specific, not land-cover classification or appreciation prediction."
    return result
def paired_change(before:dict[str,Any],after:dict[str,Any])->dict[str,Any]:
    if before["width"]!=after["width"] or before["height"]!=after["height"]:
        raise ValueError("Paired scenes require aligned grids")
    return {"delta_mean":{key:(
        round(after["indices"][key]["mean"]-before["indices"][key]["mean"],5)
        if before["indices"].get(key) and after["indices"].get(key) else None
    ) for key in ("ndvi","ndwi","ndbi","nbr")},
    "note":"Mean changes do not establish per-pixel change, construction, flood events or causation."}

"""Parcel zonal satellite statistics from aligned Sentinel-2 GeoTIFFs.

Requires a verified parcel GeoJSON polygon and rasterio. Does not validate title,
survey authenticity, zoning, or land-cover class.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from backend.raster_pipeline import REQUIRED,VALID_SCL,safe_index
def zonal_features(bands:dict[str,str],geometry:dict,geometry_crs:str="EPSG:4326",reflectance_scale:float=10000)->dict:
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.warp import transform_geom
    if geometry.get("type") not in ("Polygon","MultiPolygon"):
        raise ValueError("A Polygon or MultiPolygon geometry is required")
    if reflectance_scale<=0:raise ValueError("Invalid reflectance scale")
    if not all(k in bands for k in REQUIRED):raise ValueError("Missing Sentinel-2 bands")
    arrays={};grid=None
    for name in REQUIRED:
        path=Path(bands[name])
        with rasterio.open(path) as src:
            if src.crs is None:raise ValueError("Raster CRS is required")
            current=(str(src.crs),src.transform,src.width,src.height)
            if grid is None:grid=current
            elif current!=grid:raise ValueError("Bands are not aligned on identical grids")
            arrays[name]=src.read(1,masked=True)
    crs,transform,width,height=grid
    shape=transform_geom(geometry_crs,crs,geometry)
    inside=geometry_mask([shape],out_shape=(height,width),transform=transform,invert=True,all_touched=False)
    if not inside.any():
        return {"status":"no_pixel_overlap","valid_pixel_count":0}
    scl=np.asarray(arrays["SCL"].filled(0))
    valid=inside & np.isin(scl,list(VALID_SCL))
    scaled={}
    for name in ("B03","B04","B08","B11","B12"):
        raw=arrays[name]
        x=np.asarray(raw.filled(0),dtype=np.float32)/reflectance_scale
        valid &= ~np.ma.getmaskarray(raw) & np.isfinite(x) & (x>=0) & (x<=1)
        scaled[name]=x
    indices={"ndvi":safe_index(scaled["B08"],scaled["B04"]),
             "ndwi":safe_index(scaled["B03"],scaled["B08"]),
             "ndbi":safe_index(scaled["B11"],scaled["B08"]),
             "nbr":safe_index(scaled["B08"],scaled["B12"])}
    output={}
    for name,arr in indices.items():
        sample=arr[valid & np.isfinite(arr)]
        output[name]={"mean":round(float(sample.mean()),5),"median":round(float(np.median(sample)),5),
                      "std":round(float(sample.std()),5),"count":int(sample.size)} if sample.size else None
    return {"status":"computed" if valid.any() else "no_valid_pixels",
            "parcel_pixel_count":int(inside.sum()),"valid_pixel_count":int(valid.sum()),
            "valid_fraction_of_parcel_pixels":round(float(valid.sum()/inside.sum()),4),
            "raster_crs":crs,"indices":output,
            "limitations":["Input geometry is not independently verified as a surveyed parcel.",
                           "Pixel-based indicators are not legal land-use classification.",
                           "Small parcels may contain too few 10–20m pixels for reliable inference.",
                           "Mixed pixels, seasonality and atmospheric effects may distort results."]}

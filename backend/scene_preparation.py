"""Sentinel-2 STAC asset preparation with explicit network and raster boundaries.

Requires rasterio, httpx and numpy. STAC item is downloaded from a trusted
catalog; asset URLs are validated against a strict allowlist before opening.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
import json
import httpx
ALLOWED_HOSTS=("sentinel-cogs.s3.us-west-2.amazonaws.com","sentinel-cogs.s3.amazonaws.com",
               "sentinel-cogs.s3.us-east-1.amazonaws.com","sentinel-cogs.s3.amazonaws.com",
               "earth-search.aws.element84.com")
BANDS={"B03":"green","B04":"red","B08":"nir","B11":"swir16","B12":"swir22","SCL":"scl"}
def allowed_asset_url(url:str)->bool:
    try:
        p=urlparse(url)
        return p.scheme=="https" and p.hostname in ALLOWED_HOSTS and p.username is None and p.password is None
    except ValueError:return False
def resolve_assets(item:dict)->dict[str,str]:
    assets=item.get("assets") or {}
    mapping={}
    for band,stac_key in BANDS.items():
        asset=assets.get(stac_key) or assets.get(band)
        if not isinstance(asset,dict) or not isinstance(asset.get("href"),str):
            raise ValueError("Missing STAC asset: "+band)
        url=asset["href"]
        if not allowed_asset_url(url):raise ValueError("Asset host not allowlisted: "+band)
        mapping[band]=url
    return mapping
def align_scene(item:dict,output_dir:str,resolution_m:int=20)->dict:
    if resolution_m not in (10,20,30):raise ValueError("Resolution must be 10, 20 or 30m")
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import calculate_default_transform,reproject
    urls=resolve_assets(item)
    out=Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    # Choose the native B11 grid (20m) as reference; no claim of improved
    # native spatial resolution when upsampling to smaller pixels.
    with rasterio.open(urls["B11"]) as reference:
        if reference.crs is None:raise ValueError("Source CRS missing")
        ref_crs=reference.crs
        bounds=reference.bounds
        from rasterio.transform import from_origin
        from math import ceil
        transform=from_origin(bounds.left,bounds.top,resolution_m,resolution_m)
        width=ceil((bounds.right-bounds.left)/resolution_m)
        height=ceil((bounds.top-bounds.bottom)/resolution_m)
        if width*height>30_000_000:raise ValueError("Scene too large; crop first")
    manifest={}
    for band,url in urls.items():
        with rasterio.open(url) as src:
            if src.crs is None:raise ValueError("Source CRS missing: "+band)
            target=np.zeros((height,width),dtype=np.uint16)
            reproject(source=rasterio.band(src,1),destination=target,src_transform=src.transform,
                      src_crs=src.crs,dst_transform=transform,dst_crs=ref_crs,
                      resampling=Resampling.nearest if band=="SCL" else Resampling.bilinear,
                      dst_nodata=0)
            path=out/(band+".tif")
            with rasterio.open(path,"w",driver="GTiff",height=height,width=width,count=1,
                               dtype="uint16",crs=ref_crs,transform=transform,compress="deflate") as dst:
                dst.write(target,1)
            manifest[band]=str(path)
    result={"scene_id":item.get("id"),"datetime":item.get("properties",{}).get("datetime"),
            "cloud_cover":item.get("properties",{}).get("eo:cloud_cover"),
            "resolution_m":resolution_m,"manifest":manifest,
            "warning":"Aligned imagery is not parcel-specific. Validate reflectance scaling, SCL quality, source metadata and seasonality."}
    (out/"provenance.json").write_text(json.dumps(result,indent=2))
    return result

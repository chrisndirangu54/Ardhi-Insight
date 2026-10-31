# Sentinel-2 scene preparation

The workflow supports an Earth Search STAC item and prepares aligned GeoTIFF bands for parcel-level analysis.

1. Discover scenes with `GET /api/imagery/sentinel-scenes` and retrieve a full STAC item JSON from the catalog.
2. Install `numpy rasterio httpx`.
3. Run `python -m scripts.prepare_scene --item item.json --output-dir data/aligned --resolution 20`.
4. Use the resulting `manifest` from `provenance.json` with `python -m scripts.parcel_features --manifest scene.json --geometry parcel.geojson` (copy the manifest object into scene.json).

The processor uses a 20m default output grid, bilinear resampling for reflectance bands and nearest-neighbor for SCL classification. It checks a strict allowlist of asset hosts, validates source CRS and enforces a maximum output pixel count.

**Limitations:** This is a CLI pipeline, not an unattended scheduler. Scene discovery does not yet retrieve the complete STAC item for the operator. Asset keys and hosts depend on the STAC provider and may require configuration. Remote COG reading requires GDAL HTTPS access and can be slow. Upsampling does not create higher-resolution observations. Scene-wide preparation is not parcel cropping, cloud-free mosaicking, validated land-cover classification or land-price prediction. Use licensed and appropriately attributed imagery.

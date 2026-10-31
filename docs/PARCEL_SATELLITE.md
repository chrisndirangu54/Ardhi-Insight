# Parcel-level satellite intelligence

Use verified parcel geometry in GeoJSON (Polygon or MultiPolygon) with a matching Sentinel-2 scene manifest described in [RASTER_PIPELINE.md](RASTER_PIPELINE.md).

```bash
pip install -r backend/requirements.txt
pip install numpy rasterio
python -m scripts.parcel_features --manifest scene.json --geometry parcel.geojson --output parcel_features.json
```

The extractor transforms the geometry into the raster CRS, checks aligned bands, masks pixels outside the polygon and excludes cloud/shadow classes using Sentinel-2 SCL. It produces parcel-specific NDVI, NDWI, NDBI and NBR summary statistics, valid-pixel counts and data-quality warnings.

**Current limitations:** Local GeoTIFFs must be supplied and co-registered. A geometry file is not proof of survey validity or ownership. Outputs are spectral features, not zoning decisions or verified land-use labels. Scene-level provenance, seasonal composites, automated STAC download, change-detection validation and ML integration remain pending.

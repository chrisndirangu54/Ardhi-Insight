# Satellite raster processing

The pipeline reads locally provided Sentinel-2 bands B03, B04, B08, B11, B12 and SCL as aligned GeoTIFFs. Install optional dependencies with `pip install numpy rasterio`.

```json
{
  "B03": "data/scene/B03.tif",
  "B04": "data/scene/B04.tif",
  "B08": "data/scene/B08.tif",
  "B11": "data/scene/B11.tif",
  "B12": "data/scene/B12.tif",
  "SCL": "data/scene/SCL.tif"
}
```

Run: `python -m scripts.process_scene --manifest scene.json --output features.json`

The pipeline checks matching CRS, affine transforms and raster dimensions, screens SCL classes and computes NDVI, NDWI, NDBI and NBR scene-wide summary statistics.

**Important limitations:** Sentinel-2 bands are delivered at different native resolutions and must be explicitly resampled and co-registered before use. Cloud mask and atmospheric correction quality must be assessed. Scene-wide summaries are not parcel-level features. Source imagery is not automatically downloaded; real Earth Search STAC discovery is available separately. No land-cover classification or appreciation forecast is asserted.

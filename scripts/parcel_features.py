"""Run parcel zonal statistics on local imagery and GeoJSON geometry.

python -m scripts.parcel_features --manifest scene.json --geometry parcel.geojson
"""
import argparse,json
from pathlib import Path
from backend.parcel_zonal import zonal_features
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--geometry",required=True)
    parser.add_argument("--geometry-crs",default="EPSG:4326")
    parser.add_argument("--output")
    args=parser.parse_args()
    geo=json.loads(Path(args.geometry).read_text())
    if geo.get("type")=="Feature":geo=geo["geometry"]
    elif geo.get("type")=="FeatureCollection":
        if len(geo.get("features",[]))!=1:raise ValueError("Exactly one feature required")
        geo=geo["features"][0]["geometry"]
    result=zonal_features(json.loads(Path(args.manifest).read_text()),geo,args.geometry_crs)
    text=json.dumps(result,indent=2,allow_nan=False)
    if args.output:Path(args.output).write_text(text)
    else:print(text)
if __name__=="__main__":main()

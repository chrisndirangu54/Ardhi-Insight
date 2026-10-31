"""CLI: python -m scripts.process_scene --manifest path/to/scene.json"""
import argparse,json
from pathlib import Path
from backend.raster_pipeline import extract_scene
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True,help="JSON mapping B03/B04/B08/B11/B12/SCL to local GeoTIFF paths")
    p.add_argument("--output",default=None)
    args=p.parse_args()
    bands=json.loads(Path(args.manifest).read_text())
    result=extract_scene(bands)
    text=json.dumps(result,indent=2,allow_nan=False)
    if args.output:Path(args.output).write_text(text)
    else:print(text)
if __name__=="__main__":main()

"""Run STAC scene preparation on a previously obtained Earth Search item JSON."""
import argparse,json
from pathlib import Path
from backend.scene_preparation import align_scene
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--item",required=True,help="STAC Feature JSON downloaded from trusted Earth Search")
    p.add_argument("--output-dir",required=True)
    p.add_argument("--resolution",type=int,default=20,choices=(10,20,30))
    a=p.parse_args()
    item=json.loads(Path(a.item).read_text())
    print(json.dumps(align_scene(item,a.output_dir,a.resolution),indent=2))
if __name__=="__main__":main()

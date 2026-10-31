import unittest,tempfile
from pathlib import Path
import numpy as np
class TestParcelZonal(unittest.TestCase):
    def test_polygon_statistics(self):
        import rasterio
        from rasterio.transform import from_origin
        from backend.parcel_zonal import zonal_features
        with tempfile.TemporaryDirectory() as temp:
            bands={}
            values={"B03":2000,"B04":1000,"B08":5000,"B11":3000,"B12":2000,"SCL":4}
            for name,value in values.items():
                path=Path(temp)/(name+".tif")
                with rasterio.open(path,"w",driver="GTiff",height=3,width=3,count=1,dtype="uint16",crs="EPSG:4326",transform=from_origin(36,-1,.01,.01)) as ds:
                    ds.write(np.full((3,3),value,dtype=np.uint16),1)
                bands[name]=str(path)
            polygon={"type":"Polygon","coordinates":[[[36,-1],[36.03,-1],[36.03,-1.03],[36,-1.03],[36,-1]]]}
            result=zonal_features(bands,polygon)
            self.assertEqual(result["status"],"computed")
            self.assertAlmostEqual(result["indices"]["ndvi"]["mean"],.66667,places=4)
            self.assertEqual(result["valid_pixel_count"],9)
if __name__=="__main__":unittest.main()

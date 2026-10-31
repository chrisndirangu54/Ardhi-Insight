import unittest
import numpy as np
from backend.raster_pipeline import safe_index,paired_change
class TestRaster(unittest.TestCase):
    def test_ndvi(self):
        a=np.array([.5,.2],dtype=np.float32);b=np.array([.1,.2],dtype=np.float32)
        r=safe_index(a,b)
        self.assertAlmostEqual(float(r[0]),2/3,places=5)
        self.assertAlmostEqual(float(r[1]),0)
    def test_zero_denominator(self):
        r=safe_index(np.array([0.],dtype=np.float32),np.array([0.],dtype=np.float32))
        self.assertTrue(np.isnan(r[0]))
    def test_change(self):
        a={"width":1,"height":1,"indices":{"ndvi":{"mean":0.4}}}
        b={"width":1,"height":1,"indices":{"ndvi":{"mean":0.6}}}
        self.assertAlmostEqual(paired_change(a,b)["delta_mean"]["ndvi"],0.2)
if __name__=="__main__":unittest.main()

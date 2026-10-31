import unittest
from backend.remote_sensing import Bands,Pair,spectral_indices,change
class TestRemoteSensing(unittest.TestCase):
    def bands(self,day):
        return Bands(blue=.1,green=.2,red=.1,nir=.5,swir1=.3,swir2=.2,acquisition_date=day)
    def test_ndvi(self):
        r=spectral_indices(self.bands("2024-01-01"))
        self.assertAlmostEqual(r["indices"]["ndvi"],0.66667)
    def test_cloud_rejected(self):
        b=self.bands("2024-01-01");b.cloud_masked=False
        self.assertEqual(spectral_indices(b)["status"],"rejected")
    def test_order(self):
        self.assertEqual(change(Pair(before=self.bands("2025-01-01"),after=self.bands("2024-01-01")))["status"],"rejected")
    def test_delta(self):
        a=self.bands("2024-01-01");b=self.bands("2025-01-01");b.nir=.4
        self.assertEqual(change(Pair(before=a,after=b))["status"],"computed")
if __name__=="__main__":unittest.main()

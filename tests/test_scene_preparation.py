import unittest
from backend.scene_preparation import allowed_asset_url,resolve_assets
class TestScenePreparation(unittest.TestCase):
    def test_host_allowlist(self):
        self.assertTrue(allowed_asset_url("https://sentinel-cogs.s3.us-west-2.amazonaws.com/a.tif"))
        self.assertFalse(allowed_asset_url("http://sentinel-cogs.s3.us-west-2.amazonaws.com/a.tif"))
        self.assertFalse(allowed_asset_url("https://evil.example.org/a.tif"))
    def test_missing_assets(self):
        with self.assertRaises(ValueError):resolve_assets({"assets":{}})
    def test_resolve(self):
        keys=("green","red","nir","swir16","swir22","scl")
        assets={k:{"href":"https://sentinel-cogs.s3.us-west-2.amazonaws.com/a.tif"} for k in keys}
        self.assertEqual(len(resolve_assets({"assets":assets})),6)
if __name__=="__main__":unittest.main()

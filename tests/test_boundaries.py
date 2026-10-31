import unittest
from backend.boundaries import Fix,Track,build
class TestBoundaryWalk(unittest.TestCase):
    def test_closed_track(self):
        points=[Fix(latitude=-1,longitude=36,accuracy_m=4),Fix(latitude=-1,longitude=36.0001,accuracy_m=4),Fix(latitude=-1.0001,longitude=36.0001,accuracy_m=4),Fix(latitude=-1.0001,longitude=36,accuracy_m=4),Fix(latitude=-1,longitude=36,accuracy_m=4)]
        r=build(Track(points=points))
        self.assertGreater(r["properties"]["area_estimate_sqm"],100)
        self.assertEqual(r["properties"]["verification_status"],"unverified_gps_walk")
    def test_open_track_rejected(self):
        points=[Fix(latitude=-1,longitude=36,accuracy_m=4),Fix(latitude=-1,longitude=36.001,accuracy_m=4),Fix(latitude=-1.001,longitude=36.001,accuracy_m=4)]
        with self.assertRaises(ValueError):build(Track(points=points))
if __name__=="__main__":unittest.main()

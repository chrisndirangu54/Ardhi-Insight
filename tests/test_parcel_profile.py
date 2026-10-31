import unittest
from backend.parcel_profile import Parcel,Amenity,LandUse,SecurityEvidence,Compare,analyze,compare
class TestParcelProfiles(unittest.TestCase):
    def sample(self,label,price):
        return Parcel(label=label,latitude=-1.1,longitude=36.9,acreage=.25,asking_price_kes=price,
                      amenities=[Amenity(name="Clinic",category="healthcare",latitude=-1.1,longitude=36.9)])
    def test_amenities(self):
        result=analyze(self.sample("A",2000000))
        self.assertEqual(result["amenity_profile"]["categories"]["healthcare"]["within_1km"],1)
    def test_comparison(self):
        result=compare(Compare(first=self.sample("A",2000000),second=self.sample("B",3000000)))
        self.assertEqual(result["differences"]["asking_price_per_acre_kes"],-4000000)
    def test_security_not_scored(self):
        result=analyze(self.sample("A",2000000))
        self.assertEqual(result["security_profile"]["status"],"evidence_inventory_only")
        self.assertNotIn("crime_score",result["security_profile"])
    def test_zoning_not_inferred(self):
        result=analyze(self.sample("A",2000000))
        self.assertFalse(result["land_use_profile"]["zoning_verified"])
if __name__=="__main__":unittest.main()

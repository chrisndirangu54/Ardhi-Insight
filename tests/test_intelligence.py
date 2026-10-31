import unittest
from backend.intelligence import Property, CompareRequest, due_diligence, listing_quality, comparables, forecast_readiness
from backend.reports import ReportRequest, property_report
class TestIntelligence(unittest.TestCase):
    def setUp(self):
        self.p=Property(price_kes=2000000,acreage=0.25,latitude=-1.1,longitude=36.9)
    def test_checklist(self):
        self.assertEqual(due_diligence(self.p)["completed"],0)
    def test_listing(self):
        self.assertEqual(listing_quality(self.p)["price_per_acre_kes"],8000000)
    def test_comparables_abstain(self):
        self.assertEqual(comparables(CompareRequest(target=self.p))["status"],"insufficient_verified_comparables")
    def test_forecast_abstain(self):
        self.assertEqual(forecast_readiness()["status"],"not_available")
    def test_report(self):
        r=property_report(ReportRequest(property=self.p))
        self.assertEqual(r["environment"]["status"],"not_assessed")
        self.assertEqual(r["ownership"]["status"],"not_independently_verified")
if __name__=="__main__":unittest.main()

import unittest
from backend.data_quality import validate_transactions,holdout_diagnostics
from backend.monitoring import evaluate_intervals,population_stability_index
class TestDataQuality(unittest.TestCase):
    def record(self,date="2024-01-01",lat=-1.1,parcel="A"):
        return {"sale_date":date,"sale_price_kes":2000000,"acreage":0.25,
                "latitude":lat,"longitude":36.9,"source_url":"https://example.org/transaction",
                "source_type":"documented_sale","license":"permission-granted","parcel_id":parcel}
    def test_missing_provenance(self):
        r=self.record();del r["license"]
        self.assertEqual(validate_transactions([r])["accepted_count"],0)
    def test_asking_price_rejected(self):
        r=self.record();r["source_type"]="asking_price"
        self.assertEqual(validate_transactions([r])["accepted_count"],0)
    def test_spatial_temporal_diagnostics(self):
        rows=[self.record(),self.record("2025-01-01",-2.1,"B")]
        self.assertEqual(holdout_diagnostics(rows,"2025-01-01")["spatially_unseen_future_test_count"],1)
    def test_coverage(self):
        r=evaluate_intervals([2,3],[2,4],[1,2],[3,4])
        self.assertEqual(r["empirical_coverage"],1)
    def test_psi(self):
        self.assertGreaterEqual(population_stability_index([1,2,3,4],[1,2,3,4])["psi"],0)
if __name__=="__main__":unittest.main()

import unittest
from backend.main import haversine, simulate, Simulation, listing_intelligence
from backend.valuation import prepare, train_and_evaluate

class TestCore(unittest.TestCase):
    def test_distance(self):
        self.assertAlmostEqual(haversine(-1.286389,36.817223,-1.286389,36.817223),0)
        self.assertGreater(haversine(-1.286389,36.817223,-1.04,37.08),0)
    def test_scenario(self):
        r=simulate(Simulation(purchase_kes=1000000,annual_growth_pct=0,years=5))
        self.assertEqual(r["net_profit_kes"],0)
        self.assertEqual(r["roi_pct"],0)
    def test_ownership_never_assumed(self):
        self.assertEqual(listing_intelligence(1)["ownership"]["status"],"unverified")
    def test_no_training_data(self):
        self.assertEqual(train_and_evaluate([],"2025-01-01")["status"],"insufficient_data")
    def test_temporal_split(self):
        def row(day):
            return dict(sale_date=day,sale_price_kes=1000000,latitude=-1.1,longitude=36.9,acreage=1,distance_to_nairobi_km=10,distance_to_nearest_city_km=8,road_access_km=1,schools_3km=2,hospitals_5km=1)
        train,test=prepare([row("2023-01-01"),row("2025-01-01")],"2024-01-01")
        self.assertEqual((len(train),len(test)),(1,1))
if __name__=="__main__":unittest.main()

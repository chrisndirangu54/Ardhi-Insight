import unittest
from backend.risk import Evidence,RiskInput,readiness
class TestRisk(unittest.TestCase):
    def test_missing_environment_abstains(self):
        yes=Evidence(status="verified",source="official",observed_at="2026-10-01T00:00:00Z")
        no=Evidence(status="unavailable")
        data=RiskInput(title=yes,survey=yes,environmental=no,comparable_sales=yes,zoning=yes,road_access=yes)
        result=readiness(data)
        self.assertEqual(result["status"],"insufficient_evidence")
        self.assertIn("environmental",result["critical_gaps"])
    def test_unverified_title_abstains(self):
        yes=Evidence(status="verified",source="official",observed_at="2026-10-01T00:00:00Z")
        data=RiskInput(title=Evidence(status="unverified"),survey=yes,environmental=yes,comparable_sales=yes,zoning=yes,road_access=yes)
        self.assertIn("title",readiness(data)["critical_gaps"])
if __name__=="__main__":unittest.main()

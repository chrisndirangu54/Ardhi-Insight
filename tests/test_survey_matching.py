import unittest
from backend.survey_matching import SurveyCandidate,MatchRequest,match
P={"type":"Polygon","coordinates":[[[36,-1],[36.001,-1],[36.001,-1.001],[36,-1.001],[36,-1]]]}
class TestSurveyMatching(unittest.TestCase):
    def test_identical_geometry(self):
        c=SurveyCandidate(parcel_reference="test",geometry=P,source_name="authorized export",source_reference="ref",authorization_confirmed=True)
        r=match(MatchRequest(provisional_geometry=P,candidates=[c]))
        self.assertEqual(r["matches"][0]["intersection_over_union"],1)
        self.assertEqual(r["status"],"candidate_search_only")
    def test_requires_authorization(self):
        c=SurveyCandidate(parcel_reference="test",geometry=P,source_name="x",source_reference="ref")
        r=match(MatchRequest(provisional_geometry=P,candidates=[c]))
        self.assertEqual(r["matches"][0]["status"],"authorization_not_confirmed")
if __name__=="__main__":unittest.main()

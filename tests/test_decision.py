import unittest
from backend.decision import Candidate,EvidenceScore,DecisionRequest,evaluate,sensitivity,CRITERIA
class TestDecision(unittest.TestCase):
    def candidate(self,name,value,verified=True):
        return Candidate(name=name,title_verified=True,survey_verified=True,
            criteria={k:EvidenceScore(value=value,verified=verified,source="reviewed document") for k in CRITERIA})
    def request(self):
        return DecisionRequest(first=self.candidate("A",70),second=self.candidate("B",50),
                               weights={k:.2 for k in CRITERIA})
    def test_comparison(self):
        self.assertEqual(evaluate(self.request())["score_difference_first_minus_second"],20)
    def test_missing_evidence_abstains(self):
        r=self.request();r.first.title_verified=False
        self.assertEqual(evaluate(r)["status"],"abstained")
    def test_invalid_weights(self):
        r=self.request();r.weights["affordability"]=.9
        self.assertEqual(evaluate(r)["status"],"invalid_weights")
    def test_sensitivity(self):
        self.assertEqual(sensitivity(self.request())["status"],"computed")
if __name__=="__main__":unittest.main()

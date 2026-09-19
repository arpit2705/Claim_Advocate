import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.reasoning.consistency import tally_consistency

passes_3_3 = [{"verdict": "valid"}, {"verdict": "valid"}, {"verdict": "valid"}]
print("3/3:", tally_consistency(passes_3_3))

passes_2_3 = [{"verdict": "valid"}, {"verdict": "valid"}, {"verdict": "questionable"}]
print("2/3:", tally_consistency(passes_2_3))

passes_1_3 = [{"verdict": "valid"}, {"verdict": "questionable"}, {"verdict": "likely_misapplied"}]
print("1/3:", tally_consistency(passes_1_3))

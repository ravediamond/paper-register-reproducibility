"""L0: recompute the conformal check from series.json; the stored band must replay 22.7 % / 46 % and the file must match."""
import json, subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import conformal_check as c
want = json.loads((here / "expected" / "conformal_check.json").read_text())
got = c.main()
assert got == json.loads(json.dumps(got)) and json.loads(json.dumps(got)) == want, "expected/conformal_check.json differs"
old = got["stored_band_replay"]
assert old["success_flagged"]["median"] == 0.2273 and old["failure_flagged"]["median"] == 0.46, "stored band does not replay"
new = got["papers_band_eq2"]
print("stored band", old["success_flagged"]["median"], old["failure_flagged"]["median"], "| papers' band", new["success_flagged"]["median"], new["failure_flagged"]["median"], new["c007_1"], new["c007_2"])
print("L0 PASS")

"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")




def run():
    from dataclasses import replace
    import hashlib
    from truthai_assurance import Artifact, Claim, Dependency, Registry
    now, end = "2026-11-08T12:00:00Z", "2026-11-09T12:00:00Z"
    r = Registry()
    a = Artifact("data",hashlib.sha256(b"synthetic").hexdigest(),"fictional:source","test",now,end)
    r.add(a); r.add(Claim("child","test","Synthetic child","test","author"))
    r.add(Claim("parent","test","Synthetic parent","test","author"))
    r.link(Dependency("child","data")); r.link(Dependency("parent","child"))
    rejects("review before prerequisites", lambda: r.review("parent","reviewer",now,end))
    check("matching evidence bytes", r.verify_artifact("data",b"synthetic",now), True)
    r.review("child","reviewer",now,end); r.review("parent","reviewer",now,end)
    check("bottom-up review recorded", r.status("parent",now)["status"], "REVIEW_RECORDED")
    old = r.snapshot("parent")
    r.replace(replace(a,source="fictional:changed"))
    check("transitive binding changes", r.snapshot("parent") != old, True)
    check("upstream change invalidates parent review", r.status("parent",now)["status"] != "REVIEW_RECORDED", True)
    rejects("dependency cycle rejected", lambda: r.link(Dependency("child","parent")))

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))

import json, sys
from pydantic import BaseModel

class EvalReport(BaseModel):
    metrics: dict[str, float]
    ci95: dict[str, list[float]] = {}
    def save(self, path: str): open(path, "w").write(self.model_dump_json(indent=2))
    @staticmethod
    def load(path: str): return EvalReport(**json.load(open(path)))

def compare_runs(baseline: dict, candidate: dict, thresholds: dict) -> dict:
    rows, failures = [], []
    for metric, min_delta in thresholds.items():
        b, c = baseline.get(metric), candidate.get(metric)
        if b is None or c is None:
            failures.append((metric, "missing")); continue
        delta = c - b; ok = delta >= min_delta
        rows.append({"metric": metric, "baseline": b, "candidate": c,
                     "delta": round(delta, 4), "ok": ok})
        if not ok: failures.append((metric, round(delta, 4)))
    return {"passed": not failures, "rows": rows, "failures": failures}

class RegressionGate:
    """Exit non-zero in CI if any metric regresses beyond its allowed delta."""
    def __init__(self, thresholds: dict): self.thresholds = thresholds
    def run(self, baseline_path: str, candidate_path: str) -> int:
        b = EvalReport.load(baseline_path).metrics
        c = EvalReport.load(candidate_path).metrics
        res = compare_runs(b, c, self.thresholds)
        for r in res["rows"]:
            flag = "OK " if r["ok"] else "FAIL"
            print(f"[{flag}]{r['metric']}:{r['baseline']}->{r['candidate']} "
                  f"(Δ{r['delta']:+})")
        if not res["passed"]:
            print("REGRESSION GATE FAILED", file=sys.stderr); return 1
        print("regression gate passed"); return 0
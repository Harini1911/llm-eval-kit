import argparse, sys
from .report import RegressionGate, EvalReport

def main():
    ap = argparse.ArgumentParser(prog="llm-eval")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate")
    g.add_argument("--baseline", required=True); g.add_argument("--candidate", required=True)
    g.add_argument("--min-recall1-delta", type=float, default=-0.02)
    g.add_argument("--min-recall5-delta", type=float, default=-0.02)
    a = ap.parse_args()
    if a.cmd == "gate":
        gate = RegressionGate({"recall@1": a.min_recall1_delta,
                               "recall@5": a.min_recall5_delta})
        sys.exit(gate.run(a.baseline, a.candidate))

if __name__ == "__main__":
    main()
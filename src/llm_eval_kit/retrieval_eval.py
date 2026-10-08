import math, statistics
from pydantic import BaseModel
from .metrics import recall_at_k, mrr, ndcg_at_k, bootstrap_ci
from .golden import GoldenSet

class RetrievalReport(BaseModel):
    config: str
    metrics: dict[str, float]       # point estimates
    ci95: dict[str, list[float]]    # [lo, hi]

def evaluate_retrieval(name, retrieve_fn, goldens: GoldenSet) -> RetrievalReport:
    """retrieve_fn(question) -> ordered list of ids."""
    r1, r5, mr, nd = [], [], [], []
    for it in goldens.answerable:
        rel = set(it.relevant_ids); got = retrieve_fn(it.question)
        r1.append(recall_at_k(got, rel, 1)); r5.append(recall_at_k(got, rel, 5))
        mr.append(mrr(got, rel)); nd.append(ndcg_at_k(got, rel, 5))
    def clean(xs): return [x for x in xs if not math.isnan(x)]
    series = {"recall@1": r1, "recall@5": r5, "mrr": mr, "ndcg@5": nd}
    metrics, ci = {}, {}
    for k, xs in series.items():
        mean, lo, hi = bootstrap_ci(clean(xs))
        metrics[k] = round(mean, 4); ci[k] = [round(lo, 4), round(hi, 4)]
    return RetrievalReport(config=name, metrics=metrics, ci95=ci)
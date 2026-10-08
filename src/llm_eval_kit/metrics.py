import math, random, statistics

def recall_at_k(retrieved, relevant, k):
    if not relevant: return math.nan
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)

def precision_at_k(retrieved, relevant, k):
    if k == 0: return 0.0
    return sum(1 for d in retrieved[:k] if d in relevant) / k

def mrr(retrieved, relevant):
    for rank, d in enumerate(retrieved, start=1):
        if d in relevant: return 1.0 / rank
    return 0.0

def ndcg_at_k(retrieved, relevant, k):
    if not relevant: return math.nan
    dcg = sum(1/math.log2(i+2) for i, d in enumerate(retrieved[:k]) if d in relevant)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant), k)))
    return dcg/idcg if idcg else 0.0

def bootstrap_ci(values, n=2000, alpha=0.05, seed=0):
    """Mean + 95% CI via bootstrap. Drops NaN. Deterministic with seed."""
    vals = [v for v in values if v == v]
    if not vals: return (math.nan, math.nan, math.nan)
    rng = random.Random(seed); m = len(vals); means = []
    for _ in range(n):
        means.append(sum(vals[rng.randrange(m)] for _ in range(m)) / m)
    means.sort()
    return (statistics.mean(vals), means[int(alpha/2*n)], means[int((1-alpha/2)*n)])
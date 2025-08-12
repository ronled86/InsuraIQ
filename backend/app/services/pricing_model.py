def price_score(premium_monthly: float, coverage_limit: float, deductible: float) -> float:
    score = 0.0
    score += min(1_000_000, coverage_limit) / 1_000_000 * 0.5
    score += max(0, 500 - min(500, premium_monthly)) / 500 * 0.3
    score += max(0, 10_000 - min(10_000, deductible)) / 10_000 * 0.2
    return round(score * 100, 1)

def feature_contributions(premium_monthly: float, coverage_limit: float, deductible: float):
    cov_part = min(1_000_000, coverage_limit) / 1_000_000 * 0.5
    prem_part = max(0, 500 - min(500, premium_monthly)) / 500 * 0.3
    ded_part = max(0, 10_000 - min(10_000, deductible)) / 10_000 * 0.2
    total = (cov_part + prem_part + ded_part) * 100
    return {
        "coverage_component": round(cov_part*100,1),
        "premium_component": round(prem_part*100,1),
        "deductible_component": round(ded_part*100,1),
        "total_score": round(total,1)
    }
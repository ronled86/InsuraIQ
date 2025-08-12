from typing import List, Dict
from .pricing_model import price_score, feature_contributions

def find_gaps(policies: List[Dict]) -> List[Dict]:
    types = {p["product_type"] for p in policies if p.get("active", True)}
    possible = {"health","life","auto","home","disability"}
    missing = possible - types
    return [{
        "title": f"Consider adding {t} coverage",
        "reason": f"No active {t} policy detected",
        "impact": "Risk exposure if an event occurs without coverage",
        "explanation": {"missing_type": t}
    } for t in sorted(missing)]

def find_overlaps(policies: List[Dict]) -> List[Dict]:
    by_type = {}
    for p in policies:
        by_type.setdefault(p["product_type"], []).append(p)
    return [{
        "title": f"Overlap in {t} policies",
        "reason": f"You have {len(items)} {t} policies",
        "impact": "You may be overpaying, consider consolidating",
        "explanation": {"count": len(items), "policy_ids": [i.get("id") for i in items if i.get("id")]}
    } for t, items in by_type.items() if len(items) > 1]

def shortlist_value(policies: List[Dict]) -> List[Dict]:
    scored = []
    for p in policies:
        s = price_score(p.get("premium_monthly",0), p.get("coverage_limit",0), p.get("deductible",0))
        contrib = feature_contributions(p.get("premium_monthly",0), p.get("coverage_limit",0), p.get("deductible",0))
        scored.append((s, p, contrib))
    scored.sort(key=lambda x: -x[0])
    top = scored[:3]
    return [{
        "title": f"Good value candidate: {p['insurer']} {p['product_type']}",
        "reason": f"Score {s} based on coverage, premium, deductible",
        "impact": "Consider keeping or negotiating a better rate",
        "explanation": contrib
    } for s, p, contrib in top]

def recommend(policies: List[Dict]) -> List[Dict]:
    return find_gaps(policies) + find_overlaps(policies) + shortlist_value(policies)
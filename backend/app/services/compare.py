from typing import List, Dict

def compare_policies(policies: List[Dict]) -> Dict:
    table = []
    for p in policies:
        premium = p.get("premium_monthly") or 0.0
        cov = p.get("coverage_limit") or 0.0
        ratio = cov / max(premium, 1)
        table.append({
            "id": p["id"],
            "insurer": p["insurer"],
            "product_type": p["product_type"],
            "premium_monthly": premium,
            "deductible": p.get("deductible",0.0),
            "coverage_limit": cov,
            "coverage_per_shekel": round(ratio, 2)
        })
    table.sort(key=lambda r: (-r["coverage_per_shekel"], r["deductible"]))
    summary = "Sorted by coverage per currency then deductible."
    return {"summary": summary, "table": table}
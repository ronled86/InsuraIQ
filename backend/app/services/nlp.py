import csv
from typing import List, Dict

def parse_csv(lines) -> List[Dict]:
    reader = csv.DictReader(lines)
    rows = []
    for row in reader:
        rows.append({
            "owner_name": row.get("owner_name","").strip(),
            "insurer": row.get("insurer","").strip(),
            "product_type": normalize_product(row.get("product_type","").strip()),
            "policy_number": row.get("policy_number","").strip(),
            "start_date": row.get("start_date","").strip(),
            "end_date": row.get("end_date","").strip(),
            "premium_monthly": float(row.get("premium_monthly",0) or 0),
            "deductible": float(row.get("deductible",0) or 0),
            "coverage_limit": float(row.get("coverage_limit",0) or 0),
            "notes": row.get("notes","").strip()
        })
    return rows

def normalize_product(product: str) -> str:
    m = product.strip().lower()
    aliases = {
        "auto": ["car","vehicle","auto"],
        "home": ["home","house","property"],
        "health": ["health","medical"],
        "life": ["life","term life","whole life"],
        "disability": ["disability","income protection"]
    }
    for key, vals in aliases.items():
        if m in vals:
            return key
    return m
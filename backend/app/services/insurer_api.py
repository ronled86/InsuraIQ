from typing import Dict, Any, List
import httpx
from ..core.settings import settings

async def fetch_sample_quotes(product_type: str, coverage_limit: float, deductible: float) -> List[Dict[str, Any]]:
    # Stub: mimic external aggregator, replace with real endpoint
    # If settings.INSURER_API_BASE is set, you can call it with API key
    if settings.INSURER_API_BASE:
        headers = {}
        if settings.INSURER_API_KEY:
            headers["Authorization"] = f"Bearer {settings.INSURER_API_KEY}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{settings.INSURER_API_BASE}/quotes", params={"type": product_type, "coverage": coverage_limit, "deductible": deductible}, headers=headers)
                r.raise_for_status()
                return r.json()
        except Exception:
            pass
    # fallback demo quotes
    base_price = max(20.0, coverage_limit/10000.0 - deductible/1000.0)
    return [
        {"insurer":"Alpha", "monthly": round(base_price*1.0, 2), "deductible": deductible, "coverage": coverage_limit},
        {"insurer":"Beta", "monthly": round(base_price*0.95, 2), "deductible": deductible*1.2, "coverage": coverage_limit*0.98},
        {"insurer":"Gamma", "monthly": round(base_price*1.1, 2), "deductible": deductible*0.8, "coverage": coverage_limit*1.05},
    ]
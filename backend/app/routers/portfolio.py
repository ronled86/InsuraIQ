from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..core.auth_security import require_auth

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/summary")
def portfolio_summary(db: Session = Depends(get_db), user=Depends(require_auth)):
    items = db.query(models.Policy).filter(models.Policy.user_id==user['id']).all()
    totals = {}
    for p in items:
        t = p.product_type
        totals.setdefault(t, {"count":0,"premium":0.0,"coverage":0.0})
        totals[t]["count"] += 1
        totals[t]["premium"] += p.premium_monthly or 0.0
        totals[t]["coverage"] += p.coverage_limit or 0.0
    return {"by_type": totals, "total_premium": sum(v["premium"] for v in totals.values())}
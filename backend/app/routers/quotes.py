import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..services.compare import compare_policies
from ..services.recommendations import recommend
from ..services.insurer_api import fetch_sample_quotes
from ..core.auth_security import require_auth

router = APIRouter(prefix="/advisor", tags=["advisor"])

@router.post("/compare", response_model=schemas.CompareResult)
def compare(req: schemas.CompareRequest, db: Session = Depends(get_db), user=Depends(require_auth)):
    ids = req.policy_ids
    rows = db.query(models.Policy).filter(models.Policy.id.in_(ids), models.Policy.user_id==user['id']).all()
    if not rows: raise HTTPException(status_code=404, detail="No policies found")
    data = [{
        "id": r.id, "insurer": r.insurer, "product_type": r.product_type,
        "premium_monthly": r.premium_monthly, "deductible": r.deductible,
        "coverage_limit": r.coverage_limit, "active": r.active
    } for r in rows]
    result = compare_policies(data)
    # store history
    hist = models.CompareHistory(user_id=user['id'], policy_ids_csv=",".join(map(str, ids)), result_json=json.dumps(result))
    db.add(hist); db.commit()
    return {"summary": result["summary"], "table": result["table"]}

@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db), user=Depends(require_auth)):
    rows = db.query(models.Policy).filter(models.Policy.user_id==user['id']).all()
    data = [{
        "id": r.id, "insurer": r.insurer, "product_type": r.product_type,
        "premium_monthly": r.premium_monthly, "deductible": r.deductible,
        "coverage_limit": r.coverage_limit, "active": r.active
    } for r in rows]
    recs = recommend(data)
    return recs

@router.get("/compare_history", response_model=list[schemas.CompareHistoryItem])
def compare_history(db: Session = Depends(get_db), user=Depends(require_auth)):
    items = db.query(models.CompareHistory).filter(models.CompareHistory.user_id==user['id']).order_by(models.CompareHistory.created_at.desc()).limit(50).all()
    out = []
    for it in items:
        out.append({
            "id": it.id,
            "policy_ids": [int(x) for x in it.policy_ids_csv.split(",") if x],
            "result": json.loads(it.result_json or "{}"),
            "created_at": it.created_at
        })
    return out

@router.get("/quotes_demo")
async def quotes_demo(product_type: str = Query(...), coverage_limit: float = Query(...), deductible: float = Query(0)):
    return await fetch_sample_quotes(product_type, coverage_limit, deductible)
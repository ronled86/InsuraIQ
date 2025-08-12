from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..core.auth_security import require_auth
from ..services import nlp, pdf_import

router = APIRouter(prefix="/policies", tags=["policies"])

@router.post("/", response_model=schemas.PolicyOut)
def create_policy(policy: schemas.PolicyCreate, db: Session = Depends(get_db), user=Depends(require_auth)):
    p = models.Policy(**policy.model_dump(), user_id=user['id'])
    db.add(p); db.commit(); db.refresh(p); return p

@router.get("/", response_model=List[schemas.PolicyOut])
def list_policies(db: Session = Depends(get_db), user=Depends(require_auth)):
    return db.query(models.Policy).filter(models.Policy.user_id==user['id']).all()

@router.put("/{policy_id}", response_model=schemas.PolicyOut)
def update_policy(policy_id: int = Path(...), patch: schemas.PolicyUpdate = None, db: Session = Depends(get_db), user=Depends(require_auth)):
    p = db.query(models.Policy).filter(models.Policy.id==policy_id, models.Policy.user_id==user['id']).first()
    if not p: raise HTTPException(status_code=404, detail="Policy not found")
    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(p, k, v)
    db.add(p); db.commit(); db.refresh(p); return p

@router.delete("/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db), user=Depends(require_auth)):
    p = db.query(models.Policy).filter(models.Policy.id==policy_id, models.Policy.user_id==user['id']).first()
    if not p: raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(p); db.commit(); return {"deleted_id": policy_id}

@router.post("/upload")
async def upload_policies(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(require_auth)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")
    content = (await file.read()).decode("utf-8").splitlines()
    rows = nlp.parse_csv(content)
    created = []
    for r in rows:
        p = models.Policy(**r, user_id=user['id'])
        db.add(p); db.commit(); db.refresh(p); created.append(p.id)
    return {"created_ids": created}

@router.post("/import/pdf")
async def import_pdf(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(require_auth)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    
    # Read file content
    payload = await file.read()
    
    # Create a temporary file path that works on Windows
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(payload)
        tmp_path = tmp_file.name
    
    try:
        # Extract data from PDF
        data = pdf_import.parse_pdf_to_policy_fields(tmp_path, payload)
        
        # Validate that we extracted some useful data
        if not any([data.get('owner_name'), data.get('insurer'), data.get('policy_number')]):
            raise HTTPException(status_code=400, detail="Could not extract policy information from PDF")
        
        # Set defaults for required fields if not extracted
        if not data.get('owner_name'):
            data['owner_name'] = f"Unknown ({file.filename})"
        if not data.get('insurer'):
            data['insurer'] = "Unknown"
        if not data.get('product_type'):
            data['product_type'] = "general"
        if not data.get('policy_number'):
            data['policy_number'] = f"PDF-{file.filename[:10]}"
        if not data.get('start_date'):
            data['start_date'] = "2024-01-01"
        if not data.get('end_date'):
            data['end_date'] = "2024-12-31"
        
        # Create policy record
        p = models.Policy(**data, user_id=user['id'])
        db.add(p)
        db.commit()
        db.refresh(p)
        
        return {"success": True, "created_id": p.id, "extracted": data, "message": "PDF imported successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass
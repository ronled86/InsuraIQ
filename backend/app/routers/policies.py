from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Dict, Any
import os
import re
import tempfile
import shutil
import logging
import uuid
from datetime import datetime
from pathlib import Path as PathLib
from ..database import get_db
from .. import models, schemas
from ..core.auth_security import require_auth
from ..core.settings import settings
from ..core.sanitization import input_sanitizer
from ..core.exceptions import (
    NotFoundException, 
    ValidationException, 
    FileProcessingException,
    DatabaseException,
    handle_database_error,
    handle_exceptions
)
from ..services import nlp, pdf_import
from ..services.compare import comparison_service

# Security constants
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = {'.pdf', '.csv'}

def validate_file_upload(file: UploadFile) -> None:
    """Validate uploaded file for security"""
    if not file.filename:
        raise ValidationException("No filename provided", field="filename")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationException(
            f"File type {file_ext} not allowed. Only {', '.join(ALLOWED_FILE_EXTENSIONS)} are permitted",
            field="file_type"
        )
    
    # Sanitize filename to prevent path traversal
    file.filename = input_sanitizer.sanitize_filename(file.filename)

def check_file_size(payload: bytes) -> None:
    """Check if file size is within limits"""
    if len(payload) > MAX_FILE_SIZE:
        raise ValidationException(
            f"File size {len(payload)/1024/1024:.1f}MB exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
            field="file_size"
        )

def generate_unique_policy_number(db: Session, base_filename: str) -> str:
    """Generate a unique policy number based on filename"""
    # Clean filename for policy number
    clean_filename = re.sub(r'[^\w\-_.]', '', base_filename[:10])
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    
    # Try different variations until we find a unique one
    for attempt in range(100):  # Max 100 attempts
        if attempt == 0:
            policy_number = f"PDF-{clean_filename}-{timestamp}"
        else:
            policy_number = f"PDF-{clean_filename}-{timestamp}-{attempt:02d}"
        
        # Check if this policy number already exists
        existing = db.query(models.Policy).filter(
            models.Policy.policy_number == policy_number
        ).first()
        
        if not existing:
            return policy_number
    
    # Fallback to UUID if all attempts failed
    return f"PDF-{uuid.uuid4().hex[:12]}"

router = APIRouter(prefix="/policies", tags=["policies"])

@router.post("/", response_model=schemas.PolicyOut)
@handle_exceptions()
async def create_policy(
    policy: schemas.PolicyCreate, 
    db: Session = Depends(get_db), 
    user: Dict[str, Any] = Depends(require_auth)
) -> models.Policy:
    """Create a new policy with comprehensive error handling"""
    try:
        # Sanitize input data
        sanitized_data = input_sanitizer.sanitize_policy_data(policy.model_dump())
        p = models.Policy(**sanitized_data, user_id=user['id'])
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    except IntegrityError as e:
        db.rollback()
        raise handle_database_error(e, "create_policy")
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException("Failed to create policy", operation="create_policy")

@router.get("/", response_model=List[schemas.PolicyOut])
@handle_exceptions()
async def list_policies(
    db: Session = Depends(get_db), 
    user: Dict[str, Any] = Depends(require_auth)
) -> List[models.Policy]:
    """List all policies for the authenticated user"""
    try:
        return db.query(models.Policy).filter(models.Policy.user_id == user['id']).all()
    except SQLAlchemyError as e:
        raise DatabaseException("Failed to retrieve policies", operation="list_policies")

@router.put("/{policy_id}", response_model=schemas.PolicyOut)
def update_policy(policy_id: int = Path(...), patch: schemas.PolicyUpdate = None, db: Session = Depends(get_db), user=Depends(require_auth)):
    p = db.query(models.Policy).filter(models.Policy.id==policy_id, models.Policy.user_id==user['id']).first()
    if not p: raise HTTPException(status_code=404, detail="Policy not found")
    
    # Sanitize update data
    data = input_sanitizer.sanitize_policy_data(patch.model_dump(exclude_unset=True))
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
    validate_file_upload(file)
    
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")
    
    content = (await file.read()).decode("utf-8").splitlines()
    check_file_size(content.encode())
    
    rows = nlp.parse_csv(content)
    created = []
    for r in rows:
        p = models.Policy(**r, user_id=user['id'])
        db.add(p); db.commit(); db.refresh(p); created.append(p.id)
    return {"created_ids": created}

@router.post("/import/pdf")
async def import_pdf(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(require_auth)):
    import tempfile
    import os
    import logging
    import shutil
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    logger.info(f"PDF import started for file: {file.filename}")
    
    # Validate file upload
    validate_file_upload(file)
    
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    
    tmp_path = None
    pdf_file_path = None
    try:
        # Read file content and validate size
        logger.info("Reading file content...")
        payload = await file.read()
        check_file_size(payload)
        
        file_size = len(payload)
        logger.info(f"File content read, size: {file_size} bytes")
        
        # Create a temporary file path that works on Windows
        logger.info("Creating temporary file...")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(payload)
            tmp_path = tmp_file.name
        logger.info(f"Temporary file created at: {tmp_path}")
        
        # Extract data from PDF
        logger.info("Extracting data from PDF...")
        data = pdf_import.parse_pdf_to_policy_fields(tmp_path, payload, file.filename)
        logger.info(f"Data extracted: {data}")
        
        # Validate that we extracted some useful data
        if not any([data.get('owner_name'), data.get('insurer'), data.get('policy_number')]):
            # If no data was extracted, create a basic policy with minimal info
            logger.info("No specific data extracted, creating basic policy with filename")
            data = {
                "owner_name": f"PDF Import ({file.filename})",
                "insurer": "Unknown",
                "product_type": "general", 
                "policy_number": generate_unique_policy_number(db, file.filename),
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "premium_monthly": 0.0,
                "deductible": 0.0,
                "coverage_limit": 0.0,
                "notes": f"Imported from PDF: {file.filename}"
            }
        
        # Set defaults for required fields if not extracted (this is now redundant but kept for safety)
        if not data.get('owner_name'):
            data['owner_name'] = f"Unknown ({file.filename})"
        if not data.get('insurer'):
            data['insurer'] = "Unknown"
        if not data.get('product_type'):
            data['product_type'] = "general"
        if not data.get('policy_number'):
            data['policy_number'] = generate_unique_policy_number(db, file.filename)
        if not data.get('start_date'):
            data['start_date'] = "2024-01-01"
        if not data.get('end_date'):
            data['end_date'] = "2024-12-31"
        
        logger.info("Creating policy record...")
        # Create policy record first to get ID
        try:
            p = models.Policy(**data, user_id=user['id'])
            db.add(p)
            db.commit()
            db.refresh(p)
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Integrity error when creating policy, generating new policy number: {str(e)}")
            
            # If we get a constraint violation, try with a new unique policy number
            data['policy_number'] = generate_unique_policy_number(db, file.filename + "_retry")
            p = models.Policy(**data, user_id=user['id'])
            db.add(p)
            db.commit()
            db.refresh(p)
        
        # Save PDF file to permanent location
        upload_dir = Path(__file__).parent.parent.parent / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        # Create a unique filename using policy ID and original filename
        safe_filename = f"policy_{p.id}_{file.filename}"
        pdf_file_path = upload_dir / safe_filename
        
        # Copy the PDF file to permanent storage
        shutil.copy2(tmp_path, pdf_file_path)
        
        # Update policy with PDF file information
        p.original_filename = file.filename
        p.pdf_file_path = str(pdf_file_path)
        p.pdf_file_size = file_size
        db.commit()
        
        logger.info(f"PDF imported successfully, policy ID: {p.id}, PDF stored at: {pdf_file_path}")
        return {"success": True, "created_id": p.id, "extracted": data, "message": "PDF imported successfully"}
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        # Clean up PDF file if it was created but policy creation failed
        if pdf_file_path and os.path.exists(pdf_file_path):
            try:
                os.unlink(pdf_file_path)
            except:
                pass
        # Generic error message for security
        from ..core.settings import settings
        if settings.LOCAL_DEV:
            detail = f"Error processing PDF: {str(e)}"
        else:
            detail = "Error processing PDF file. Please try again or contact support."
        raise HTTPException(status_code=500, detail=detail)
    finally:
        # Clean up temporary file
        if tmp_path:
            try:
                os.unlink(tmp_path)
                logger.info(f"Temporary file {tmp_path} cleaned up")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {tmp_path}: {str(e)}")

@router.get("/{policy_id}/pdf")
async def get_policy_pdf(policy_id: int, db: Session = Depends(get_db), user=Depends(require_auth)):
    """Serve the PDF file for a specific policy"""
    policy = db.query(models.Policy).filter(
        models.Policy.id == policy_id,
        models.Policy.user_id == user['id']
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    if not policy.pdf_file_path or not os.path.exists(policy.pdf_file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        path=policy.pdf_file_path,
        media_type='application/pdf',
        filename=policy.original_filename or f"policy_{policy_id}.pdf"
    )

@router.post("/compare")
async def compare_policies(policy_ids: List[int], db: Session = Depends(get_db), user=Depends(require_auth)):
    """Compare multiple policies with AI-powered analysis"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Comparing policies: {policy_ids} for user: {user['id']}")
        
        if len(policy_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 policies are required for comparison")
        
        # Use the enhanced comparison service
        comparison_result = comparison_service.compare_policies(db, policy_ids, user['id'])
        
        # Save comparison to history
        history_record = models.CompareHistory(
            user_id=user['id'],
            policy_ids_csv=','.join(map(str, policy_ids)),
            result_json=str(comparison_result)
        )
        db.add(history_record)
        db.commit()
        
        logger.info(f"Comparison completed successfully for policies: {policy_ids}")
        return comparison_result
        
    except ValueError as e:
        logger.error(f"Comparison validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.get("/compare/history")
async def get_comparison_history(db: Session = Depends(get_db), user=Depends(require_auth)):
    """Get user's comparison history"""
    history = db.query(models.CompareHistory).filter(
        models.CompareHistory.user_id == user['id']
    ).order_by(models.CompareHistory.created_at.desc()).limit(10).all()
    
    return [
        {
            "id": h.id,
            "policy_ids": h.policy_ids_csv.split(','),
            "created_at": h.created_at,
            "result_summary": str(h.result_json)[:200] + "..." if len(str(h.result_json)) > 200 else str(h.result_json)
        }
        for h in history
    ]
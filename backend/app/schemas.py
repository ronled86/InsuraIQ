from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class PolicyBase(BaseModel):
    owner_name: str
    insurer: str
    product_type: str
    policy_number: str
    start_date: str
    end_date: str
    premium_monthly: float
    premium_annual: Optional[float] = 0.0
    deductible: float = 0.0
    coverage_limit: float = 0.0
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    contact_address: Optional[str] = None
    policy_language: Optional[str] = "en"
    coverage_details: Optional[dict] = None
    policy_chapters: Optional[dict] = None
    terms_and_conditions: Optional[str] = None
    original_filename: Optional[str] = None
    document_type: Optional[str] = "manual"
    extraction_confidence: Optional[float] = 0.0
    notes: Optional[str] = ""

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    owner_name: Optional[str] = None
    insurer: Optional[str] = None
    product_type: Optional[str] = None
    policy_number: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    premium_monthly: Optional[float] = None
    premium_annual: Optional[float] = None
    deductible: Optional[float] = None
    coverage_limit: Optional[float] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    contact_address: Optional[str] = None
    policy_language: Optional[str] = None
    coverage_details: Optional[dict] = None
    policy_chapters: Optional[dict] = None
    terms_and_conditions: Optional[str] = None
    original_filename: Optional[str] = None
    document_type: Optional[str] = None
    extraction_confidence: Optional[float] = None
    notes: Optional[str] = None
    active: Optional[bool] = None

class PolicyOut(PolicyBase):
    id: int
    user_id: str
    active: bool = True
    updated_at: Optional[datetime] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    class Config:
        from_attributes = True

class CompareRequest(BaseModel):
    policy_ids: List[int]

class CompareResult(BaseModel):
    summary: str
    table: list

class Recommendation(BaseModel):
    title: str
    reason: str
    impact: str
    explanation: Optional[dict] = None

class CompareHistoryItem(BaseModel):
    id: int
    policy_ids: List[int]
    result: Any
    created_at: datetime
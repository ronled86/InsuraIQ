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
    deductible: float = 0.0
    coverage_limit: float = 0.0
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
    deductible: Optional[float] = None
    coverage_limit: Optional[float] = None
    notes: Optional[str] = None
    active: Optional[bool] = None

class PolicyOut(PolicyBase):
    id: int
    user_id: str
    active: bool = True
    updated_at: Optional[datetime] = None
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
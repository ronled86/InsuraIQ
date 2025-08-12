from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from .database import Base
from datetime import datetime

class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    owner_name = Column(String, index=True, nullable=False)
    insurer = Column(String, index=True, nullable=False)
    product_type = Column(String, index=True, nullable=False)
    policy_number = Column(String, unique=True, index=True, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    premium_monthly = Column(Float, default=0.0)
    deductible = Column(Float, default=0.0)
    coverage_limit = Column(Float, default=0.0)
    notes = Column(String, default="")
    active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CompareHistory(Base):
    __tablename__ = "compare_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    policy_ids_csv = Column(String, nullable=False)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from .database import Base
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from .database import Base
from datetime import datetime

class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Basic policy information
    owner_name = Column(String, index=True, nullable=False)
    insurer = Column(String, index=True, nullable=False)
    product_type = Column(String, index=True, nullable=False)
    policy_number = Column(String, unique=True, index=True, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    
    # Financial information
    premium_monthly = Column(Float, default=0.0)
    premium_annual = Column(Float, default=0.0)
    deductible = Column(Float, default=0.0)
    coverage_limit = Column(Float, default=0.0)
    
    # Contact and administrative information
    contact_phone = Column(String)
    contact_email = Column(String) 
    contact_address = Column(Text)
    policy_language = Column(String, default="en")  # Language of the document
    
    # Extended coverage information for comprehensive policies
    coverage_details = Column(JSON)  # Store detailed coverage as JSON
    policy_chapters = Column(JSON)   # Store policy chapters/sections
    terms_and_conditions = Column(Text)  # Full terms text
    
    # Document metadata
    original_filename = Column(String)
    document_type = Column(String, default="pdf")  # pdf, csv, manual
    extraction_confidence = Column(Float, default=0.0)  # How confident we are in the extraction
    pdf_file_path = Column(String)  # Path to stored PDF file
    pdf_file_size = Column(Integer)  # Size of PDF file in bytes
    
    # Standard fields
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
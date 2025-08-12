import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .core.settings import settings

DB_URL = settings.SQLALCHEMY_DATABASE_URL
if settings.LOCAL_DEV and DB_URL.startswith("postgresql"):
    # Override to local SQLite for easy non-docker runs
    DB_URL = "sqlite:///./local_dev.db"

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
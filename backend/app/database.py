import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.orm.session import SessionTransaction
from typing import Generator, Any, Dict
from .core.settings import settings

DB_URL: str = settings.SQLALCHEMY_DATABASE_URL
if settings.LOCAL_DEV and DB_URL.startswith("postgresql"):
    # Override to local SQLite for easy non-docker runs
    DB_URL = "sqlite:///./local_dev.db"

connect_args: Dict[str, Any] = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine: Engine = create_engine(DB_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Database dependency injection for FastAPI"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
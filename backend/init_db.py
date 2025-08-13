#!/usr/bin/env python3
"""
Database initialization script for InsuraIQ
"""
from app.database import Base, engine
from app import models

def init_database():
    """Initialize the database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    init_database()

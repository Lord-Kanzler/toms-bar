# database.py - Database connection and session management

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./gastropro.db"

# SQLAlchemy base model
Base = declarative_base()

# Database engine creation
engine = create_engine(DATABASE_URL)

# Session local class for database interaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency function for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

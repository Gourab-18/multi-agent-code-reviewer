from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    overall_score = Column(Float)
    summary = Column(Text)
    findings = Column(JSON) # Storing list of findings as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")

engine = create_engine("sqlite:///./data/reviews.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

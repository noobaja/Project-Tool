from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# URL koneksi ke database PostgreSQL lokal
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'guardian')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'secret')}@"
    f"localhost:5432/"
    f"{os.getenv('POSTGRES_DB', 'guardian_db')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, index=True, nullable=False)
    is_suspicious = Column(Boolean, default=False, nullable=True)
    verdict = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="PENDING")

def init_db():
    Base.metadata.create_all(bind=engine)
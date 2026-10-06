from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./doctor_patient.db"
)

engine = create_engine(DATABASE_URL,
    connect_args={"check_same_thread": False}
)

session=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close
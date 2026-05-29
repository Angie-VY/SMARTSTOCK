from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("sqlite:///./"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_name = DATABASE_URL.replace("sqlite:///./", "")
    DATABASE_URL = f"sqlite:///{os.path.join(base_dir, db_name)}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
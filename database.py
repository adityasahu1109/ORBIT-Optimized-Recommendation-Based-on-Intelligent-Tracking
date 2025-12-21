from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# --- FIX: USE ABSOLUTE PATHS ---
# Get the folder where this script (database.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Point directly to the 'data' folder inside that directory
DB_PATH = os.path.join(BASE_DIR, "data", "orbit.db")
DB_URL = f"sqlite:///{DB_PATH}"
# -------------------------------

# Create the engine
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    product_id = Column(String, index=True)
    interaction_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print(f"Database connected at {DB_URL}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
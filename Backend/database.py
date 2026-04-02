from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite connection string; database file will be created in the Backend folder.
DATABASE_PATH = Path(__file__).resolve().parent / "smart_kitchen.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

# Session creator for operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Helper function to open and close database connections as needed
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
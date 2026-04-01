from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQL Server connection string
DATABASE_URL = "mssql+pyodbc://@localhost/SmartKitchenDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"

engine = create_engine(DATABASE_URL, echo=True)

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
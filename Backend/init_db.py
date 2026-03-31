from database import engine
from models import Base

print("Establishing a database connection and creating tables...")

# All tables defined in the models (models.py) are physically created in SQL Server
Base.metadata.create_all(bind=engine)

print("All tables have been successfully created!")
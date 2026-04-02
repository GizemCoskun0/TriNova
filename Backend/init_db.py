from Backend.database import engine
from Backend.models import Base

print("Establishing a database connection and creating tables...")

# All tables defined in the models (models.py) are created in SQLite
Base.metadata.create_all(bind=engine)

print("All tables have been successfully created!")
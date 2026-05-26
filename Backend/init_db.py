from database import engine
from Backend.models import Base

print("Establishing a database connection and creating tables...")

Base.metadata.create_all(bind=engine)

print("All tables have been successfully created!")

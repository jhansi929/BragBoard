# create_tables.py
from database import Base, engine
import models

print("Creating tables in the database...")
Base.metadata.create_all(bind=engine)
print("Tables created.")


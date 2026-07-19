import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()     #reads your .env file so DATABASE_URL becomes available to the code 
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)        #SQL alchemy's core connection object to Postgres; it manages the actual connection pool
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # a factory that creates database "sessions" (think of a session as one conversation with the database)
Base = declarative_base()   #the class all our database models (tables) will inherit  from SQLAlchemy uses this to know what tables exist

def get_db():   # a helper function FAST API will use to give each API request its own database session and guarantee it closes afterward
    # the try/finally ensures cleanup
    db = SessionLocal()     
    try:
        yield db
    finally:    #ensures cleanup
        db.close()
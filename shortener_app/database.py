from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_settings
# creating entry point to the database, using the db_url
engine = create_engine(
    get_settings().db_url, connect_args={"check_same_thread": False}
)
# creating a working database session when you instantiate SessionLocal
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# connects the database engine to the SQLAlchemy funtionality of the model
# base will be the class that the database model inherits from the models.py
Base = declarative_base()
# shortener_app/database.py

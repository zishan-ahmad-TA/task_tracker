# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL connection string
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/task_tracker_db"

# Create the SQLAlchemy engine to connect to MySQL
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})

# Create a session local to handle DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for defining models
Base = declarative_base()

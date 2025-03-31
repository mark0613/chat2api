from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Define the database directory and ensure it exists
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Get database URL from environment variable or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with larger pool size and longer timeout
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # 增加連接池大小
    max_overflow=20,  # 增加最大溢出連接數
    pool_timeout=60,  # 增加獲取連接的超時時間
    pool_recycle=3600,  # 回收連接的時間
    pool_pre_ping=True  # 在使用連接前驗證連接是否有效
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()

def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For alembic use
def get_database_url():
    """Return the database URL for alembic configuration"""
    return DATABASE_URL

@contextmanager
def get_db_context():
    """Context manager version of get_db for use in non-FastAPI contexts"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

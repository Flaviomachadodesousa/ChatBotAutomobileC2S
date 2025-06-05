import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_FILE = "carros.sqlite"
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DATABASE_FILE)}"

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base()

def create_db_and_tables(use_test_engine=False):
    current_engine = test_engine if use_test_engine else engine
    Base.metadata.create_all(bind=current_engine)

def get_db(use_test_engine=False):
    current_session_local = TestSessionLocal if use_test_engine else SessionLocal
    db = current_session_local()
    try:
        yield db
    finally:
        db.close()
        
@contextmanager
def get_db_session(use_test_engine=False):
    current_session_local = TestSessionLocal if use_test_engine else SessionLocal
    db = current_session_local()
    try:
        yield db
    finally:
        db.close()
    """Retorna uma sessão de banco de dados para uso fora do contexto de 'yield'."""
    return current_session_local()
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://devuser:devpassword@192.168.1.100:5432/devdb"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db
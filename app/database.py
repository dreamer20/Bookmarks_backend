from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://u5qgpo7x2p5ijga7onbe:3T1d3uCIdyuLZ1VfU5B2@bwlgavuqyiep9jy89old-postgresql.services.clever-cloud.com:5432/bwlgavuqyiep9jy89old"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:peri54ri7end@localhost:5432/mydb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

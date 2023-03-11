from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base


SQLALCHEMY_DATABASE_URL = 'sqlite:///database.sqlite3'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

Base = declarative_base()

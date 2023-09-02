import functools
import inspect
from typing import Callable, Generator
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine.base import Connection

SQLALCHEMY_DATABASE_URL = 'sqlite:///database.sqlite3'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db_connection() -> Connection:
    connection = engine.connect()
    try:
        yield connection
    except IntegrityError as e:
        connection.rollback()
    finally:
        connection.close()


def get_db() -> Session:
    session = Session()
    try:
        yield session
    except IntegrityError as e:
        session.rollback()
    finally:
        session.close()


class DBConnectDependencyManager:
    def __init__(self, dependency_db_connect: Callable, dependency_db: Callable):
        self.dependency_db_connect = dependency_db_connect
        self.dependency_db = dependency_db

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            parameter_list = inspect.getfullargspec(func)[0]
            if parameter_list:
                if 'db_connect' in parameter_list:
                    index = parameter_list.index('db_connect')
                    args = list(args)
                    gen: Generator = self.dependency_db_connect()
                    args.insert(index, next(gen))
                    return func(*args, **kwargs)
                elif 'db' in parameter_list:
                    index = parameter_list.index('db')
                    args = list(args)
                    gen: Generator = self.dependency_db()
                    args.insert(index, next(gen))
                    return func(*args, **kwargs)
                else:
                    raise ValueError('db_connect or db parameter is required inside the function.')
            else:
                raise ValueError('db_connect or db parameter is required inside the function.')

        return wrapper


db_connect_dependency_manager = DBConnectDependencyManager(get_db_connection, get_db)

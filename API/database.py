import functools
import inspect
from typing import Callable, Generator
from sqlalchemy import create_engine, URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine.base import Connection
from API.config import ConfigManager

config_manager = ConfigManager()


def database_url(url_param: ConfigManager):
    drivername = url_param.get_config.database_url.drivername
    database = url_param.get_config.database_url.database
    username = url_param.get_config.database_url.username
    password = url_param.get_config.database_url.password
    host = url_param.get_config.database_url.host
    port = url_param.get_config.database_url.port
    if drivername == 'sqlite':
        if database:
            return URL.create(
                drivername=drivername,
                database=database,
            )
    return URL.create(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )


SQLALCHEMY_DATABASE_URL = database_url(config_manager)

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

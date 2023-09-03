from API.database import Base, engine
from sqlalchemy import Column, Enum, String, Integer, Text, DateTime, UniqueConstraint, Float, Boolean
from API.schemas import DeviceType, Protocol, create_status_enum_class


class DeviceInfo(Base):
    __tablename__ = 'device_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(255))
    device_type = Column(Enum(DeviceType))
    username = Column(String(255))
    password = Column(String(255))
    super_pw = Column(String(255), nullable=True)
    protocol = Column(Enum(Protocol))
    port = Column(Integer, default=22)
    templates_name = Column(String(255), nullable=True)
    __table_args__ = (UniqueConstraint('hostname'),)

    def to_dict(self):
        return {'id': self.id, 'hostname': self.hostname, 'device_type': self.device_type.value,
                'username': self.username, 'password': self.password, 'super_pw': self.super_pw,
                'protocol': self.protocol.value, 'port': self.port, 'templates_name': self.templates_name}

    def create_device(self):
        return {'id': self.id, 'host': self.hostname, 'device_type': self.device_type.value,
                'username': self.username, 'password': self.password, 'secret': self.super_pw,
                'protocol': self.protocol.value, 'port': self.port, 'templates_name': self.templates_name}


class InterfaceInfo(Base):
    __tablename__ = 'interface_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    collect_time = Column(DateTime)
    ip_add = Column(String(255))
    inter_info = Column(Text, nullable=True)


# 发出创建表 DDL
Base.metadata.create_all(engine)

table_cache = {}


def create_table_model(table_name, fields, enum=False, enum_fields=None):
    if table_name in table_cache:
        return table_cache[table_name]

    class DynamicTable(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, index=True)

    for field_name, field_type in fields.items():
        if field_type == "integer":
            setattr(DynamicTable, field_name, Column(Integer))
        elif field_type == "string":
            setattr(DynamicTable, field_name, Column(String(255)))
        elif field_type == 'DateTime':
            setattr(DynamicTable, field_name, Column(DateTime))
        elif field_type == 'Text':
            setattr(DynamicTable, field_name, Column(Text))
        elif field_type == 'Float':
            setattr(DynamicTable, field_name, Column(Float))
        elif field_type == 'Boolean':
            setattr(DynamicTable, field_name, Column(Boolean))
        elif field_type == 'Enum':
            if enum and enum_fields:
                DynamicEnum = create_status_enum_class("DynamicEnum", enum_fields)
                setattr(DynamicTable, field_name, Column(Enum(DynamicEnum)))
            else:
                raise ValueError('当数据类型是Enum时，需要传入enum=True,enum_fields={key:value}')
        # 添加其他字段类型的处理逻辑
    table_cache[table_name] = DynamicTable
    return DynamicTable


def create_table(engine, table_model):
    Base.metadata.create_all(bind=engine, tables=[table_model.__table__])


def create_database_table(table_name, fields, enum=False, enum_fields=None):
    DynamicTable = create_table_model(table_name, fields, enum=enum, enum_fields=enum_fields)
    create_table(engine=engine, table_model=DynamicTable)
    return DynamicTable

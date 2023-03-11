from .database import Base
from sqlalchemy import Column, Enum, String, Integer
from .schemas import DeviceType, Protocol


class DeviceInfo(Base):
    __tablename__ = 'device_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String)
    device_type = Column(Enum(DeviceType))
    username = Column(String)
    password = Column(String)
    super_pw = Column(String, nullable=True)
    protocol = Column(Enum(Protocol))
    port = Column(Integer, default=22)
    templates_name = Column(String, nullable=True)

    def to_dict(self):
        return {'id': self.id, 'hostname': self.hostname, 'device_type': self.device_type.value,
                'username': self.username, 'password': self.password, 'super_pw': self.super_pw,
                'protocol': self.protocol.value, 'port': self.port, 'templates_name': self.templates_name}

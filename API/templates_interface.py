import json
from sqlalchemy.orm.session import Session
from API.crud import create_interface_info
from API.database import db_connect_dependency_manager
from API.models import create_database_table, create_table_model
from API.schemas import InterfaceInfo
from API.file_operations import FileService, FileHandler, FilePathInfo, TextFSMParser
from API.config import ConfigManager
from API.logger import logger


class InterfaceEntry:
    config = ConfigManager()
    file_handler = FileHandler()
    file_path = FilePathInfo(config=config)

    def __init__(self):
        self.file_service = FileService(self.file_handler, self.file_path)
        self.table_record_path = 'table_record.json'

    def create_table(self, table_name, fields, enum=False, enum_fields=None):
        table_models = create_database_table(table_name=table_name, fields=fields, enum=enum, enum_fields=enum_fields)
        logger.info(f'创建{table_name}表完成')
        record = {"table_name": table_name,
                  "fields": fields,
                  "enum": enum,
                  "enum_fields": enum_fields}
        self.save_table_record(record)
        return table_models

    def save_serialization(self, table_record):
        save_record = json.dumps(table_record, sort_keys=True, indent=4, separators=(',', ':'))
        self.file_service.handler.write_file(self.table_record_path, save_record)

    def save_table_record(self, record):
        table_name = record.get("table_name")
        table_record = {table_name: record}
        if not self.file_service.handler.file_exists(self.table_record_path):
            self.save_serialization(table_record)
        else:
            local_record = self.get_table_record()
            record_dict = {**local_record, **table_record}
            self.save_serialization(record_dict)

    @staticmethod
    def get_table_model(table_name: str, records: dict):
        record = records.get(table_name)
        table_name = record.get('table_name')
        fields = record.get('fields')
        enum = record.get('enum')
        enum_fields = record.get('enum_fields')
        return create_table_model(table_name=table_name,
                                  fields=fields,
                                  enum=enum,
                                  enum_fields=enum_fields)

    def get_table_record(self):
        content = self.file_service.handler.read_file(self.table_record_path)
        if content:
            record = json.loads(content)
            return record
        else:
            raise ValueError(f"record无内容{content}")

    def get_fsm_object(self, fsm_source_data: str, textfsm_templates_name: str):
        return TextFSMParser(fsm_source_data,
                             textfsm_templates_name,
                             textfsm_templates_path=self.config.get_dir_path().textfsm_templates_dir)

    @db_connect_dependency_manager
    def write_database_interface_table(self, db: Session, **kwargs):
        ip_add = kwargs.get('ip_add')
        inter_info = kwargs.get('inter_info')
        datas = {'ip_add': ip_add, 'inter_info': inter_info}
        interface_info = InterfaceInfo(**datas)
        create_interface_info(db=db, interface_info=interface_info)

    @db_connect_dependency_manager
    def database_insert_data(self, db: Session, **kwargs):
        table_name = kwargs.get("table_name")
        data_dict = kwargs.get("data_dict")
        record = self.get_table_record()
        model = self.get_table_model(table_name, record)
        db_info = model(**data_dict)
        db.add(db_info)
        db.commit()
        return db_info

    @db_connect_dependency_manager
    def database_get_data(self, db: Session, **kwargs):
        table_name = kwargs.get("table_name")
        record = self.get_table_record()
        model = self.get_table_model(table_name, record)
        return db.query(model).all()

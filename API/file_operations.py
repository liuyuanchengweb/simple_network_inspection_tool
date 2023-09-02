import json
import os
from abc import abstractmethod, ABC
from datetime import datetime
import numpy as np
import pandas as pd
from pydantic import ValidationError
from API.database import db_connect_dependency_manager, get_db, Session
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Session
from typing import Optional, Callable
import io
from API.schemas import ResponseDeviceIn, DeviceIn, InspectionOption, TestDeviceOption
from API.logger import logger
from API.config import ConfigManager
from textfsm import TextFSM

__all__ = ['get_db', 'Session', 'FileHandler', 'FilePathInfo', 'FileService', 'ResponseDeviceIn', 'DeviceIn',
           'InspectionOption', 'TextFSMParser', 'TestDeviceOption']


class FileHandlerBase(ABC):

    @abstractmethod
    def file_exists(self, file: str) -> bool:
        pass

    @abstractmethod
    def file_path_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def excel_exists(self, file: str) -> bool:
        pass

    @abstractmethod
    def create_directory(self, directory_path: str) -> None:
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str | bytes:
        pass

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> None:
        pass

    @abstractmethod
    def read_binary_file(self, file_path: str) -> bytes | None:
        pass

    @abstractmethod
    def write_binary_file(self, file_path: str, binary_data: bytes) -> None:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def append_to_file(self, file_path: str, content: str) -> None:
        pass

    @abstractmethod
    def read_from_database_to_excel(self, excel_file_path_name: str, sheet_name: str, table_name: str,
                                    engine: Connection,
                                    include_header: Optional[bool] = True, first: Optional[str] = None,
                                    data_validation_options: Optional[dict] = None) -> tuple[str, str]:
        pass

    @abstractmethod
    def write_to_database_from_excel(self, excel_file_path: str, sheet_name: str, table_name: str,
                                     engine: Connection) -> tuple[str, str] | bool:
        pass

    @abstractmethod
    def write_data_to_excel(self, content: dict[str:list | str] | list[dict, dict], excel_file_path_name: str,
                            sheet_name: str = '') -> None:
        pass


class FileHandler(FileHandlerBase):

    def file_exists(self, file: str) -> bool:
        return os.path.isfile(file)

    def file_path_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def excel_exists(self, file: str) -> None:
        assert file.endswith('.xls') or file.endswith('xlsx'), \
            'Please pass in the actual excel file name'

    def create_directory(self, directory_path: str) -> None:
        try:
            os.makedirs(directory_path)
            print(f"目录 '{directory_path}' 创建成功。")
        except FileExistsError:
            print(f"目录 '{directory_path}' 已经存在。")
        except OSError as e:
            print(f"创建目录 '{directory_path}' 时发生错误：{e}")

    def read_file(self, file_path: str) -> str | None:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"文件 '{file_path}' 未找到。")
            return None
        except IOError as e:
            print(f"读取文件 '{file_path}' 时发生错误：{e}")
            return None

    def write_file(self, file_path: str, content: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"内容已成功写入文件 '{file_path}'。")
        except IOError as e:
            print(f"写入文件 '{file_path}' 时发生错误：{e}")

    def read_binary_file(self, file_path: str) -> bytes | None:
        try:
            with open(file_path, 'rb') as file:
                binary_data = file.read()
            return binary_data
        except FileNotFoundError:
            print(f"二进制文件 '{file_path}' 未找到。")
            return None
        except IOError as e:
            print(f"读取二进制文件 '{file_path}' 时发生错误：{e}")
            return None

    def write_binary_file(self, file_path: str, binary_data: bytes) -> None:
        try:
            with open(file_path, 'wb') as file:
                file.write(binary_data)
            print(f"二进制数据已成功写入文件 '{file_path}'。")
        except IOError as e:
            print(f"写入二进制文件 '{file_path}' 时发生错误：{e}")

    def delete_file(self, file_path: str) -> None:
        try:
            os.remove(file_path)
            print(f"文件 '{file_path}' 删除成功。")
        except FileNotFoundError:
            print(f"要删除的文件 '{file_path}' 不存在。")
        except PermissionError:
            print(f"没有删除文件 '{file_path}' 的权限。")
        except Exception as e:
            print(f"删除文件 '{file_path}' 时发生错误：{e}")

    def append_to_file(self, file_path: str, content: str) -> None:
        try:
            with open(file_path, 'a') as file:
                file.write(content)
            print(f"内容已成功追加到文件 '{file_path}'。")
        except IOError as e:
            print(f"追加内容到文件 '{file_path}' 时发生错误：{e}")

    def read_from_database_to_excel(self, excel_file_path_name: str, sheet_name: str, table_name: str, engine,
                                    include_header: Optional[bool] = True, first: Optional[str] = None,
                                    data_validation_options: Optional[dict] = None) -> tuple[str, str]:
        self.excel_exists(excel_file_path_name)
        excel_file_path = os.path.dirname(excel_file_path_name)
        if not self.file_path_exists(excel_file_path):
            self.create_directory(excel_file_path)
        try:
            if include_header:
                df_header = pd.read_sql_table(table_name, engine, index_col=None)
                table_header = df_header.columns.tolist()[1:]
                df = pd.DataFrame(columns=table_header)
            else:
                df = pd.read_sql_table(table_name, engine)
            writer = pd.ExcelWriter(excel_file_path_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            if include_header and first is not None and data_validation_options is not None:
                worksheet = writer.sheets[sheet_name]
                worksheet.data_validation(first, data_validation_options)
            writer.close()
            if self.file_path_exists(excel_file_path_name):
                logger.info(
                    f"数据从数据库中读取成功，并写入 Excel 文件 '{excel_file_path_name}' 的工作表 '{sheet_name}'。")
                return excel_file_path_name, sheet_name
        except Exception as e:
            logger.error("从数据库读取数据并写入 Excel 文件时发生错误：", e)

    def write_to_database_from_excel(self, excel_file_path: str, sheet_name: str, table_name: str, engine) -> \
            tuple[str, str] | bool:
        try:
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            logger.info(
                f"数据从 Excel 文件 '{excel_file_path}' 的工作表 '{sheet_name}' 读取成功，并写入到数据库表 '{table_name}'。")
            return excel_file_path, sheet_name
        except Exception as e:
            logger.error("从 Excel 文件读取数据并写入数据库时发生错误：", e)
            return False

    def write_data_to_excel(self, content: dict[str:list | str] | list[dict, dict], excel_file_path_name: str,
                            sheet_name: str = '') -> None:
        self.excel_exists(excel_file_path_name)
        try:
            df = pd.DataFrame(content)
            if not sheet_name:
                with pd.ExcelWriter(excel_file_path_name) as writer:
                    df.to_excel(writer, index=False)
            else:

                if not self.file_path_exists(excel_file_path_name):
                    with pd.ExcelWriter(excel_file_path_name) as writer:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    with pd.ExcelWriter(excel_file_path_name, mode='a', engine="openpyxl",
                                        if_sheet_exists='replace') as writer:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            logger.error(f'数据写入到Excel时发生了错误:{e}')


class FilePathInfo:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.base_dir = self.config.get_dir_path().base_dir
        self.database_to_file_path = self.get_database_to_file_path()
        self.upload_template_zh_CN_file = self.get_upload_template_zh_CN_file()
        self.datasets_path = self.get_datasets_path()
        self.backup_config_path = self.get_backup_config_path()
        self.logs_path = self.get_logs_path()
        self.inspection_file_path = self.get_inspection_file_path()

    @staticmethod
    def get_current_date():
        return datetime.now().strftime('%Y_%m_%d')

    @staticmethod
    def get_current_time():
        return datetime.now().strftime('%H_%M_%S')

    def get_database_to_file_path(self):
        return os.path.join(self.base_dir, self.config.get_dir_path().customer_data_export_dir)

    def get_upload_template_zh_CN_file(self):
        return os.path.join(self.database_to_file_path, self.config.get_file_name().upload_template_name)

    def get_datasets_path(self):
        return os.path.join(self.base_dir, self.config.get_dir_path().datasets_dir)

    def get_backup_config_path(self):
        return os.path.join(self.datasets_path, self.config.get_dir_path().backup_device_config_file_dir,
                            self.get_current_date())

    def get_logs_path(self):
        return os.path.join(self.base_dir, self.config.get_dir_path().logs_dir)

    def get_templates_path(self):
        return os.path.join(self.base_dir, self.config.get_dir_path().templates_dir)

    def get_inspection_file_path(self):
        return os.path.join(self.datasets_path,
                            f'{self.get_current_date()}_{self.config.get_file_name().network_device_inspection_file_name}')

    def get_textfsm_templates_path(self):
        return os.path.join(self.base_dir, self.config.get_dir_path().textfsm_templates_dir)

    @staticmethod
    def join_path(*args):
        return os.path.join(*args)


class TextFSMParser:
    def __init__(self, source_data: str, textfsm_templates_name: str,
                 textfsm_templates_path: str = 'textfsm_templates'):
        self.source_data = source_data
        self.textfsm_templates_name = textfsm_templates_name
        self.textfsm_templates_path = textfsm_templates_path

    def get_textfsm_object(self):
        return TextFSM(open(self.get_textfsm_templates_path(), encoding='utf8'))

    def get_textfsm_templates_path(self):
        return os.path.join(self.textfsm_templates_path, self.textfsm_templates_name)

    def parse_data(self) -> list[dict]:
        textfsm_object = self.get_textfsm_object()
        parse_info = textfsm_object.ParseTextToDicts(self.source_data)
        return parse_info

    @staticmethod
    def _convert_to_json(data: list[dict]) -> str:
        return json.dumps(data)

    def get_parsed_data_as_json(self) -> str:
        parsed_data = self.parse_data()
        json_data = self._convert_to_json(parsed_data)
        return json_data


class FileService:
    def __init__(self, handler: FileHandlerBase, file_path_info: FilePathInfo) -> None:
        self.handler = handler
        self.file_path_info = file_path_info

    @db_connect_dependency_manager
    def get_upload_template_zh_CN_file(self, db_connect: Connection) -> tuple[str, str]:
        excel_file_path_name = self.file_path_info.upload_template_zh_CN_file
        sheet_name = 'CLI'
        table_name = 'device_info'
        first = 'F2:F999'
        data_validation_options = {'validate': 'list', 'source': ['ssh', 'telnet']}
        result = self.handler.read_from_database_to_excel(excel_file_path_name=excel_file_path_name,
                                                          sheet_name=sheet_name,
                                                          table_name=table_name, engine=db_connect, include_header=True,
                                                          first=first, data_validation_options=data_validation_options)
        return result

    @db_connect_dependency_manager
    def write_upload_template_zh_CN_file(self, db: Session, file: bytes, get_hostname: Callable,
                                         create_device: Callable) -> None | bool:
        file_obj = io.BytesIO(file)
        df = pd.read_excel(file_obj, na_values=None)
        drf = df.replace({pd.NA: None, np.nan: None})
        try:
            devices = [DeviceIn(**row) for row in drf.to_dict('records')]
            for device in devices:
                existing_device = get_hostname(db=db, hostname=device.hostname)
                if not existing_device:
                    create_device(db=db, device=device)
                    logger.info(f'添加设备成功{device.json()}')
                else:
                    logger.error(f'设备以存在{existing_device.hostname}')
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return False

    @staticmethod
    def str_to_list_or_dict(content: str):
        try:
            result = json.loads(content)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            return None

    def write_inspection_data_to_excel(self, data, excel_file_path_name: str, sheet_name: str = '') -> str:
        if isinstance(data, str):
            content = self.str_to_list_or_dict(data)
        else:
            content = data
        self.handler.write_data_to_excel(content=content, excel_file_path_name=excel_file_path_name,
                                         sheet_name=sheet_name)
        return excel_file_path_name

    def write_backup_config(self, backup_config_content: str, backup_config_name: str) -> str:
        if not self.handler.file_path_exists(path=self.file_path_info.backup_config_path):
            self.handler.create_directory(directory_path=self.file_path_info.backup_config_path)
        backup_config_file_path_and_name = self.file_path_info.join_path(self.file_path_info.backup_config_path,
                                                                         backup_config_name)
        self.handler.write_file(file_path=backup_config_file_path_and_name, content=backup_config_content)
        return backup_config_file_path_and_name

    def write_txt(self, content: str, file_path: str, file_name: str) -> None:
        if not self.handler.file_path_exists(file_path):
            self.handler.create_directory(file_path)
        else:
            file = self.file_path_info.join_path(file_path, file_name)
            self.handler.append_to_file(file_path=file, content=content)

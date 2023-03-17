import os
import asyncio
import pandas as pd
from .database import engine
from datetime import datetime
from queue import Queue

LOG_QUEUE = Queue()


class FileHandle:
    def __init__(self,
                 engine_obj: engine,
                 engine_connect: engine,
                 database_to_file_path=os.path.join(os.path.abspath(os.curdir), 'databast_to_file'),
                 database_to_file_name='uploadnes_template_zh_CN .xls',
                 default_path=os.path.join(os.path.abspath(os.curdir), 'datasets'),
                 patrol_network_excel_filename=f"Datasets.xlsx",
                 backup_config_path=f"backup_config",
                 ):
        self.engine_obj = engine_obj
        self.engine_connect = engine_connect
        self.date = datetime.now().strftime('%Y_%m_%d')
        self.database_to_file_path = database_to_file_path
        self.database_to_file_name = database_to_file_name
        self.default_path = default_path
        self.patrol_network_excel_filename = f'{self.date}_{patrol_network_excel_filename}'
        self.download_path = os.path.join(self.database_to_file_path, self.database_to_file_name)
        self.backup_config_path = os.path.join(self.default_path, backup_config_path, self.date)
        asyncio.run(self.create_directory())

    async def create_directory(self):
        if not os.path.exists(self.database_to_file_path):
            os.makedirs(self.database_to_file_path)
        if not os.path.exists(self.default_path):
            os.makedirs(self.default_path)

    def database_to_file(self):
        drf = pd.read_sql_table(table_name='device_info', con=self.engine_connect)
        drf.pop('id')
        drf_data = list(drf.columns)
        df = pd.DataFrame(columns=drf_data)
        writer = pd.ExcelWriter(self.download_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='CLI', index=False)
        worksheet = writer.sheets['CLI']
        worksheet.data_validation('F2:F999', {'validate': 'list', 'source': ['ssh', 'telnet']})
        writer._save()

    @staticmethod
    async def save_file(file_object, save_files):
        with open(save_files, 'wb') as f:
            f.write(file_object)
        return save_files

    async def exists_file_path(self, file_object, file_name, file_path: str | None = None):
        if file_path:
            save_files = os.path.join(file_path, file_name)
            save_path = await self.save_file(file_object, save_files)
            return save_path
        else:
            save_files = os.path.join(self.default_path, file_name)
            save_path = await self.save_file(file_object, save_files)
            return save_path

    async def excel_to_database(self, file_object, file_name, file_path: str | None = None):
        save_path = await self.exists_file_path(file_object, file_name, file_path)
        drf = pd.read_excel(save_path)
        drf.to_sql(name='device_info', con=self.engine_obj, index=False, if_exists='append')

    def patrol_network_to_excel(self, data):
        data = pd.DataFrame(data)
        data.to_excel(os.path.join(self.default_path, self.patrol_network_excel_filename), index=False)
        return os.path.join(self.default_path, self.patrol_network_excel_filename)

    def backup_config(self, data, save_files):
        if not os.path.exists(self.backup_config_path):
            os.makedirs(self.backup_config_path)
        with open(save_files, 'w', encoding='utf-8') as f:
            f.write(data)
        LOG_QUEUE.put(f'保存备份配置文件的路径{os.path.realpath(save_files)}')
        return save_files


file_handle = FileHandle(engine, engine.connect())

import functools
from typing import Any, Callable
from .file_handle import file_handle
import os


class DataHandle:
    data_dict: dict[str, list[str, int]] = {}
    backup_config_path = file_handle.backup_config_path

    def data(self, func: Callable[[Any], tuple[str, str]]):
        @functools.wraps(func)
        def data_processing(*args, **kwargs):
            data, table = func(*args, **kwargs)
            if table in self.data_dict:
                self.data_dict.get(table).append(data)
            else:
                self.data_dict.update({table: [data]})

        return data_processing

    def backup_config(self, func: Callable[[Any], tuple[str, str]]):
        @functools.wraps(func)
        def data_processing(*args, **kwargs):
            data, file_name = func(*args, **kwargs)
            file_name = os.path.join(self.backup_config_path, file_name)
            save_files = file_handle.backup_config(data, file_name)
            print(f'保存备份配置文件的路径{os.path.realpath(save_files)}')

        return data_processing

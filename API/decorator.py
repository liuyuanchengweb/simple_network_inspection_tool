import functools
from typing import Any, Callable, Optional
from .file_handle import file_handle
from .logger import logger
import os


class DataHandle:
    """
    模板函数执行前执行后处理类
    """
    data_dict: dict[str, list[str, int]] = {}
    backup_config_path = file_handle.backup_config_path

    def __init__(self):
        self.datas: Optional[str | list] = None
        self.table: Optional[str | list] = None

    def data_handle(self):
        """
        巡检函数处理，通过巡检函数返回的值进行生成可以保存在excel的字典数据
        接受返回的数据为字符串类型或者等长列表
        [t1,t2,t3,t4][d1,d2,d3,d4] 列名称，列数据
        :return:
        """
        if not isinstance(self.table, str):
            if not isinstance(self.datas, str):
                for (t, d) in zip(self.table, self.datas):
                    if t in self.data_dict:
                        self.data_dict.get(t).append(d)
                    else:
                        self.data_dict.update({t: [d]})
        else:
            if self.table in self.data_dict:
                self.data_dict.get(self.table).append(self.datas)
            else:
                self.data_dict.update({self.table: [self.datas]})

    def data(self, func: Callable[[Any], tuple[str, str]]):
        """
        获取巡检函数，并且接受函数返回值的装饰器
        :param func: 巡检函数
        :return: 函数对象
        """
        @functools.wraps(func)
        def data_processing(*args, **kwargs):
            self.datas, self.table = func(*args, **kwargs)
            self.data_handle()

        return data_processing

    def backup_config(self, func: Callable[[Any], tuple[str, str]]):
        """
        备份配置文件装饰器
        :param func: 备份配置文件函数
        :return: 函数对象
        """
        @functools.wraps(func)
        def data_processing(*args, **kwargs):
            data, file_name = func(*args, **kwargs)
            file_name = os.path.join(self.backup_config_path, file_name)
            save_files = file_handle.backup_config(data, file_name)
            logger.info(f'保存备份配置文件的路径{os.path.realpath(save_files)}')

        return data_processing

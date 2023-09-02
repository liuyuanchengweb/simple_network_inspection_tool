import os
from API.schemas import Configuration
import yaml
from API.logger import logger


class ConfigManager:
    _instance = None

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.config_file_path = 'config.yaml'
            self.default_config = Configuration()
            self.generate_default_config_file()
            self.load_config_dict = self.load_config()
            self.get_config = self.get_configuration()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            return cls._instance
        else:
            return cls._instance

    def generate_default_config_file(self):
        if not os.path.exists(self.config_file_path):
            default_config = self.default_config.dict()
            with open(self.config_file_path, "w") as file:
                yaml.dump(default_config, file)
            logger.info(f"默认配置文件已生成：{self.config_file_path}")

    def load_config(self):
        with open(self.config_file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
            logger.info(f'加载配置文件{self.config_file_path}')
        return config_dict

    def get_configuration(self):
        config_object = Configuration(**self.load_config_dict)
        logger.debug(f'更新配置文件{config_object}')
        return config_object

    def get_dir_path(self):
        return self.get_configuration().dir_path

    def get_file_name(self):
        return self.get_configuration().file_name

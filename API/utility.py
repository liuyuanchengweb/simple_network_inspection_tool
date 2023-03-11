import sys
import netmiko.exceptions
import os
from fastapi import WebSocket
from netmiko import ConnectHandler
from datetime import datetime
import socket
import pkgutil
from importlib import import_module
from .huawei_telnet import RewriteHuaweitelnet
from loguru import logger
from .decorator import DataHandle
from .file_handle import file_handle, LOG_QUEUE


LOG_PATH = r'./logs/log.log'


def enqueue_log(message):
    pass


logger.remove()
logger.add(enqueue_log, enqueue=True, level='INFO', format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")
logger.add(sys.stderr, level='INFO', format="{time:YYYY-MM-DD HH:mm:ss}  {level} {message}")
logger.add(LOG_PATH, level='DEBUG', format="{time:YYYY-MM-DD HH:mm:ss}  {level} {message}")


class ConnectDevice:

    def __init__(self, device_list_object: list, module_path: str, *args, **kwargs):
        self.connect = None
        self.device_list_object = device_list_object
        self.device_list: list = []
        self.module_path = module_path
        self.module = None
        self.device_type: str | None = None
        self.host = None
        self.module_dict: dict = {}
        self.websocket: WebSocket = kwargs.get('websocket')

    @staticmethod
    def date():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    async def get_device(self):
        for device_object in self.device_list_object:
            device = device_object.to_dict()
            await self.get_device_info(device)

    async def get_device_info(self, device):
        device_info = {'device_type': f"{device.get('device_type')}_{device.get('protocol')}",
                       'host': device.get('hostname'),
                       'username': device.get('username'),
                       'password': device.get('password'),
                       'port': device.get('port'),
                       'conn_timeout': 30,
                       'timeout': 120,
                       'templates_name': device.get('templates_name')
                       }
        if device.get('super_pw'):
            device_info['super_pw'] = device.get('super_pw')
        return self.device_list.append(device_info)

    async def load_plugins(self) -> dict:
        module_dict = {}
        for module_info in pkgutil.iter_modules(path=[self.module_path]):
            if module_info.name.startswith("_"):
                continue
            module = import_module(f'templates.{module_info.name}')
            module_dict[module_info.name] = module
        return module_dict

    async def templates(self, templates_name):
        if templates_name:
            self.module = self.module_dict.get(templates_name)
            return self.module
        else:
            templates_name = self.device_type.split('_')[0]
            self.module = self.module_dict.get(templates_name)
            return self.module

    async def connect_func(self, device):
        self.host = device.get('host')
        logger.info(f'当前登录了{self.host}设备')
        await self.websocket.send_text(f'{self.date()} 登录了{self.host}设备')
        self.device_type = device.get('device_type')
        if self.device_type == 'huawei_telnet':
            self.connect = RewriteHuaweitelnet(**device)
        else:
            self.connect = ConnectHandler(**device)
        return self.connect

    async def dev_run(self):
        func = self.module.__all__
        for data in func:
            fun = getattr(self.module, data)
            fun(self.connect)
            logger.info(f'执行了----->{fun.__name__}方法')
            await self.websocket.send_text(f'{self.date()} 执行了----->{fun.__name__}方法')

    async def data_processing(self, device):
        templates_name = device.get('templates_name')
        await self.templates(templates_name)
        device.pop('templates_name')
        await self.connect_func(device)
        await self.dev_run()

    async def production_data(self):
        for device in self.device_list:
            try:
                await self.data_processing(device)
            except netmiko.exceptions.NetmikoTimeoutException:
                logger.error(f'连接发生异常{self.host}')
                await self.websocket.send_text(f'连接发生异常{self.host}')
                continue
            except TimeoutError:
                logger.error(f'连接超时{self.host}')
                await self.websocket.send_text(f'连接超时{self.host}')
                continue
            except AttributeError:
                logger.error(f'返回数据异常，请检查相关函数返回的类型,错误类型{AttributeError}')
                await self.websocket.send_text(f'返回数据异常，请检查相关函数返回的类型,错误类型{AttributeError}')
            except TypeError:
                logger.error(f'类型错误，检查类型{TypeError}')
                await self.websocket.send_text(f'类型错误，检查类型{TypeError}')
            except ValueError:
                logger.error(f'存储数据过程异常，检查数据内容{ValueError}')
                await self.websocket.send_text(f'存储数据过程异常，检查数据内容{ValueError}')

    async def start(self):
        self.module_dict = await self.load_plugins()
        await self.get_device()
        await self.production_data()
        file_path = file_handle.patrol_network_to_excel(DataHandle.data_dict)
        await self.websocket.send_text(f'巡检文件路径为{os.path.realpath(file_path)}')
        DataHandle.data_dict.clear()


class BackupConfigConnectDevice(ConnectDevice):
    async def dev_run(self):
        fun = self.module.backup_config
        fun(self.connect)

    async def production_data(self):
        for device in self.device_list:
            try:
                await self.data_processing(device)
                await self.websocket.send_text(LOG_QUEUE.get())
            except netmiko.exceptions.NetmikoTimeoutException:
                logger.error(f'连接发生异常{self.host}')
                await self.websocket.send_text(f'连接发生异常{self.host}')
                continue
            except TimeoutError:
                logger.error(f'连接超时{self.host}')
                await self.websocket.send_text(f'连接超时{self.host}')
                continue
            except AttributeError:
                logger.error(f'返回数据异常，请检查相关函数返回的类型,错误类型{AttributeError}')
                await self.websocket.send_text(f'返回数据异常，请检查相关函数返回的类型,错误类型{AttributeError}')
            except TypeError:
                logger.error(f'类型错误，检查类型{TypeError}')
                await self.websocket.send_text(f'类型错误，检查类型{TypeError}')
            except ValueError:
                logger.error(f'存储数据过程异常，检查数据内容{ValueError}')
                await self.websocket.send_text(f'存储数据过程异常，检查数据内容{ValueError}')

    async def start(self):
        self.module_dict = await self.load_plugins()
        await self.get_device()
        await self.production_data()


class ConnectTest(ConnectDevice):
    async def connect_test(self):
        for device in self.device_list:
            socket.setdefaulttimeout(3)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = device.get('host')
            port = device.get('port')
            try:
                server.connect((ip, port))
                logger.debug(f'{ip}连接正常')
                server.close()
                await self.websocket.send_text(f'{self.date()} {ip}连接正常')
            except TimeoutError:
                logger.debug(f'{ip}端口不通')
                await self.websocket.send_text(f'{self.date()} {ip}端口不通')

    async def start(self):
        await self.get_device()
        await self.connect_test()

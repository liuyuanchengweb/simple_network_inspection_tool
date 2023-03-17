from datetime import datetime
import netmiko.exceptions
from fastapi import WebSocket
from netmiko import ConnectHandler, BaseConnection
import socket
import pkgutil
from importlib import import_module
from .huawei_telnet import RewriteHuaweitelnet
from .file_handle import LOG_QUEUE
from .logger import logger
from .config import netmiko_config


def log_date():
    """
    全局时间函数
    :return: 格式化时间
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Module:
    def __init__(self, module_path: str = 'templates') -> None:
        """
        初始化模块类
        :param module_path: 模块存放的包路径
        """
        self.module_path = module_path

    async def load_plugins(self) -> dict:
        """
        动态导入模块包中的模块
        :return: 模块对象字典{'模块名':'模块对象'}
        """
        module_dict = {}
        for module_info in pkgutil.iter_modules(path=[self.module_path]):
            if module_info.name.startswith("_"):
                continue
            module = import_module(f'{self.module_path}.{module_info.name}')
            module_dict[module_info.name] = module
        return module_dict


class ConnectData:
    def __init__(self, device_list_object) -> None:
        """
        登录设备数据类，传入从数据库获取到的设备信息对象，对数据库获取到的对象进行处理封装
        :param device_list_object: 登录设备信息列表
        """
        self.device_list_object = device_list_object
        self.device_list: list = []
        self.device = {}

    async def get_device(self):
        for device_object in self.device_list_object:
            self.device = device_object.to_dict()
            await self.get_device_info()

    async def get_device_info(self):
        device_info = {'device_type': f"{self.device.get('device_type')}_{self.device.get('protocol')}",
                       'host': self.device.get('hostname'),
                       'username': self.device.get('username'),
                       'password': self.device.get('password'),
                       'port': self.device.get('port'),
                       }
        await self.get_templates_name(device_info)
        if self.device.get('super_pw'):
            device_info['secret'] = self.device.get('super_pw')
        device_info.update(netmiko_config())
        return self.device_list.append(device_info)

    async def get_templates_name(self, device_info):
        pass

    async def get_device_list(self):
        await self.get_device()
        return self.device_list


class GetTemplatesName(ConnectData):
    """
    继承登录设备数据类，在登录设备数据基础上增加了模板数据，用于判断当前设备用什么模板进行处理
    """

    async def get_templates_name(self, device_info):
        device_info['templates_name'] = self.device.get('templates_name')


class ConnectDeviceBase:
    def __init__(self, device_list: list) -> None:
        """
        连接设备基类，预留了钩子函数，可以自定义要执行的函数放在钩子函数内，就会获得一个连接连接对象
        :param device_list: 登录设备信息列表
        """
        self.connect: BaseConnection | None = None
        self.device_list = device_list
        self.device_type: str | None = None
        self.except_type = {}
        self.host = None
        self.device = {}

    async def connect_func(self):
        """
        判断使用什么类进行登录，因为重写了华为telnet类
        其中await self.conn()为预留的钩子函数
        :return:
        """
        self.device_type = self.device.get('device_type')
        self.host = self.device.get('host')
        if self.device_type == 'huawei_telnet':
            self.connect = RewriteHuaweitelnet(**self.device)
            self.except_type['normal'] = self.host
            await self.login_log()
        else:
            self.connect = ConnectHandler(**self.device)
            self.except_type['normal'] = self.host
            await self.login_log()
        await self.conn()
        return self.connect

    async def conn(self):
        """实现连接的钩子函数，需要自定义连接，继承该类，重写该方法
        例子：
        class ConnTest(ConnectDeviceBase):
            def __init__(self, device_list, func):
                super().__init__(device_list)
                self.func = func

            async def conn(self):
                self.func(self.connect)
        使用方法：
        自定义函数
        def ctest(conn):
            output = conn.send_command(command_string='display current-configuration')
            print(output)
        实例化对象，传入设备列表，以及函数对象
        conn = ConnTest(get_device, ctest)
        执行函数
        asyncio.run(conn.start(test))
        """
        pass

    async def log_handle(self):
        """
        输出信息处理
        :return:
        """
        if self.except_type:
            for k, v in self.except_type.items():
                if k == 'normal':
                    info = f'{log_date()}设备{v}连接成功'
                    logger.info(info)
                    await self.webs(info)
                else:
                    info = f'{log_date()}存在异常{k}:{v}'
                    logger.error(info)
                    await self.webs(info)

    async def webs(self, info):
        """
        websocket输出信息钩子函数，用于在跟前端交互
        :param info: 输出到前端的信息
        :return:
        """
        pass

    async def login_log(self):
        """
        登录信息钩子，用于巡检时向前端输出登录设备信息，备份配置文件时关闭
        :return:
        """
        pass

    async def backup_log(self):
        """
        备份配置信息钩子，用于备份配置文件时，向前端输出信息
        :return:
        """
        pass

    async def data_processing(self):
        """
        设备信息的消费者，用于处理登录设备信息，可以在该节点对登录设备的信息进行修改调整
        :return:
        """
        await self.connect_func()

    async def production_data(self):
        """
        登录设备信息处理，生成者
        :return:
        """
        for self.device in self.device_list:
            try:
                await self.data_processing()
                await self.backup_log()
            except netmiko.exceptions.NetmikoTimeoutException as err:
                self.except_type[netmiko.exceptions.NetmikoTimeoutException] = err
                await self.log_handle()
                continue
            except TimeoutError as err:
                self.except_type[TimeoutError] = err
                await self.log_handle()
                continue
            except AttributeError as err:
                self.except_type[AttributeError] = err
                await self.log_handle()
            except TypeError as err:
                self.except_type[TypeError] = err
                await self.log_handle()
            except ValueError as err:
                self.except_type[ValueError] = err
                await self.log_handle()
            except Exception as err:
                self.except_type[Exception] = err
                await self.log_handle()
            finally:
                if self.connect:
                    self.connect.disconnect()
                else:
                    self.except_type['ERROR'] = '没有获取到连接对象'

    async def start(self):
        """
        类入口函数，用于调用生成者开始工作
        :return:
        """
        await self.production_data()


class ConnectDevice(ConnectDeviceBase):
    def __init__(self, device_list: list, module_dict, websocket: WebSocket) -> None:
        """
        巡检登录设备类，需要导入模块信息，需要导入设备所属模板信息，需要导入websocket连接对象
        :param device_list: 登录设备信息列表
        :param module_dict: 模块字典对象
        :param websocket: websocket对象
        """
        super().__init__(device_list)
        self.websocket: WebSocket = websocket
        self.module_dict = module_dict
        self.module = None

    async def templates(self, templates_name):
        """
        根据模板名称获取到对应的模板信息，用于后续执行模块内的函数
        :param templates_name: 模板名字
        :return: 模块对象
        """
        if templates_name:
            self.module = self.module_dict.get(templates_name)
            return self.module
        else:
            templates_name = self.device_type.split('_')[0]
            self.module = self.module_dict.get(templates_name)
            return self.module

    async def dev_run(self):
        """
        执行函数的方法，根据获取到的模块信息执行模块中__all__方法存在的函数，以及在函数中传入当前连接对象
        :return:
        """
        func = self.module.__all__
        for data in func:
            fun = getattr(self.module, data)
            self.except_type.clear()
            fun(self.connect)
            log_info = f'{log_date()}----->执行{fun.__name__}方法完成'
            await self.log_handle(log_info)

    async def data_processing(self):
        """
        登录设备信息消费者，处理登录设备信息，并且将模板名字传入到模块获取函数，并且弹出netmiko连接不需要的模板名字
        获取连接对象后对当前设备执行对应模块内的方法
        :return:
        """
        templates_name = self.device.get('templates_name')
        await self.templates(templates_name)
        self.device.pop('templates_name')
        await self.connect_func()
        await self.dev_run()

    async def log_handle(self, *args):
        """
        重写信息输出方法
        :param args: 输出的信息
        :return:
        """
        await super().log_handle()
        for i in args:
            logger.info(i)
            await self.websocket.send_text(i)

    async def webs(self, info):
        """
        提供websocket输出
        :param info: 输出的信息
        :return:
        """
        await self.websocket.send_text(info)

    async def login_log(self):
        """
        打开登录设备时往前端输出信息的开关
        :return:
        """
        await self.log_handle()

    async def start(self):
        """
        执行方法
        :return:
        """
        await self.log_handle(f'{log_date()}执行了---->start方法')
        await self.production_data()
        self.except_type.clear()


class BackupConfigConnectDevice(ConnectDevice):
    """
    备份配置文件类
    """

    async def dev_run(self):
        """
        重写执行函数，只执行模块中的backup_config()函数
        所以需要备份配置文件函数固定名称
        :return:
        """
        fun = self.module.backup_config
        fun(self.connect)

    async def backup_log(self):
        """
        重写向前端输出的信息
        :return:
        """
        await self.log_handle()
        await self.websocket.send_text(LOG_QUEUE.get())

    async def login_log(self):
        pass


class ConnectTest(ConnectDevice):
    """
    测试端口连通类
    """

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
                await self.websocket.send_text(f'{log_date()} {ip}连接正常')
            except TimeoutError:
                logger.debug(f'{ip}端口不通')
                await self.websocket.send_text(f'{log_date()} {ip}端口不通')

    async def start(self):
        await self.connect_test()


class Start:
    """
    统一入口类
    """

    def __init__(self):
        self.data_class = ConnectData
        self.get_templatesName = GetTemplatesName
        self.conn_class = ConnectDeviceBase
        self.conn_on = ConnectDevice
        self.conn_backup = BackupConfigConnectDevice
        self.conn_test = ConnectTest

    async def connect_on(self, dev_obj, module_dict, websocket):
        """
        设备巡检入口方法
        :param dev_obj: 数据库查询得到的设备对象
        :param module_dict: 模块字典
        :param websocket: websocket对象
        :return: 巡检启动方法
        """
        data_obj = self.get_templatesName(dev_obj)
        data = await data_obj.get_device_list()
        connect = self.conn_on(data, module_dict, websocket)
        return await connect.start()

    async def connect_backup(self, dev_obj, module_dict, websocket):
        """
        备份配置文件入口方法
        :param dev_obj: 数据库查询得到的设备对象
        :param module_dict: 模块字典
        :param websocket: websocket对象
        :return: 备份配置文件入口方法
        """
        data_obj = self.get_templatesName(dev_obj)
        data = await data_obj.get_device_list()
        connect = self.conn_backup(data, module_dict, websocket)
        return await connect.start()

    async def connect_test(self, dev_obj, module_dict, websocket):
        """
        测试设备端口连通入口方法
        :param dev_obj: 数据库查询得到的设备对象
        :param module_dict: 模块字典
        :param websocket: websocket对象
        :return: 测试设备端口入口方法
        """
        data_obj = self.data_class(dev_obj)
        data = await data_obj.get_device_list()
        connect = self.conn_test(data, module_dict, websocket)
        return await connect.start()

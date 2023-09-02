import pkgutil
import socket
from time import sleep
from importlib import import_module
from types import ModuleType
from typing import Dict, Callable, Type, Generator, Any, List
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from API.file_operations import FileService
from API.logger import logger
from API.config import ConfigManager
from API.database import db_connect_dependency_manager, Session
from API.models import DeviceInfo
from API.schemas import NetmikoOptionalParam, NetmikoKernelParameter, NetmikoInspectionTemplates, NetmikoDeviceType

task_lock = Lock()


def load_plugins(config: ConfigManager) -> Dict[str, ModuleType]:
    """
    动态导入模块包中的模块
    :param config:ConfigManager对象
    :return: 模块对象字典{'模块名':'模块对象'}
    """
    module_path = config.get_dir_path().templates_dir
    module_dict = {module_info.name: import_module(f'{module_path}.{module_info.name}')
                   for module_info in pkgutil.iter_modules(path=[module_path])
                   if not module_info.name.startswith("_")}
    return module_dict


@db_connect_dependency_manager
def get_device_info_from_db(db: Session, get_data_func: Callable[[Session], List[DeviceInfo]]) \
        -> Generator[dict[str:str], None, None]:
    """
    :param db: 通过依赖注入，不需要传
    :param get_data_func: CRUD，查询设备的信息的方法
    :return: 设备生成器对象
    """
    for device in get_data_func(db):
        yield device.create_device()


def generate_netmiko_data_and_templates(get_device_dict,
                                        netmiko_kernel_parameter: Type[NetmikoKernelParameter],
                                        netmiko_optional_param: Type[NetmikoOptionalParam],
                                        netmiko_inspection_templates: Type[NetmikoInspectionTemplates],
                                        netmiko_device_type: Type[NetmikoDeviceType],
                                        config: ConfigManager) -> Generator[tuple[dict], None, None]:
    """
    数据拼接
    :param get_device_dict: 设备生成器对象
    :param netmiko_kernel_parameter: netmiko核心参数数据模型类，数据来源通过迭代生成器对象获得
    :param netmiko_optional_param: netmiko可选参数数据模型类，数据来源通过配置文件读取
    :param netmiko_inspection_templates: 巡检模板数据类
    :param netmiko_device_type: netmiko设备类型数据拼接，因为数据库存放的设备类型和协议是分开的，而netmiko需要 deviceType_protocol
    :param config: ConfigManager对象,给NetmikoOptionalParam类传递数据
    :return: 生成器类型的元组()
    """
    for device in get_device_dict:
        get_device_type_or_protocol = netmiko_device_type(**device)
        device_type = {
            'device_type': f'{get_device_type_or_protocol.device_type}_{get_device_type_or_protocol.protocol}'
        }
        netmiko_kernel = netmiko_kernel_parameter(**device).dict()
        netmiko_optional = netmiko_optional_param(**config.get_config.netmiko_param.dict()).dict()
        netmiko_templates = netmiko_inspection_templates(**device).dict()
        netmiko_connect_data = {**netmiko_kernel, **netmiko_optional, **device_type}
        yield netmiko_connect_data, netmiko_templates


def execute_and_process_result_with_lock(func, connect, process_inspection_func, file_service, content_process,
                                         contents):
    """
    多线程执行，加锁执行，抽象出来供execute_all_functions()和execute_fixed_function()函数共同调用。
    :param func: 巡检方法
    :param connect: 连设备连接对象
    :param process_inspection_func:对返回数据的处理函数
    :param file_service:文件服务对象，提供给对返回数据的处理函数使用
    :param content_process:数据保存方式，从前端传入的
    :param contents:空列表，为保存到excel的数据做处理，收集数据后一次保存到excel
    :return:
    """
    with task_lock:
        result = func(connect)
        if result:
            # 对返回的数据进行处理
            process_inspection_func(file_service, content_process, contents, **result)
        else:
            logger.error(f'返回采集数据为空，请在模板函数内检查，或者是不返回数据自行在巡检模板内处理采集数据')
    logger.debug(f'执行函数返回的数据：{result}')


def execute_all_functions(module, connect, process_inspection_func, file_service, content_process, contents):
    """
    自动执行巡检模板all列表所有方法
    :param module: 巡检模块
    :param connect: 设备连接对象，传递给process_inspection_func()方法使用
    :param process_inspection_func: 数据保存方法，传递给process_inspection_func()方法使用
    :param file_service: 文件服务对象，传递给process_inspection_func()方法使用
    :param content_process: 数据保存方式，从前端传入的，传递给process_inspection_func()方法使用
    :param contents: 空列表，为保存到excel的数据做处理，收集数据后一次保存到excel
    :return:
    """
    func_list = module.__all__
    logger.debug(f'模块方法列表{func_list}')
    for func_name in func_list:
        func = getattr(module, func_name)
        logger.debug(f'执行的函数名字：{func_name} 执行的函数地址{func}')
        execute_and_process_result_with_lock(func=func,
                                             connect=connect,
                                             process_inspection_func=process_inspection_func,
                                             file_service=file_service,
                                             content_process=content_process,
                                             contents=contents)


def execute_fixed_function(module, connect, target_func_name, process_inspection_func, file_service, content_process,
                           contents):
    """
    自定义执行巡检模板内的函数
    :param module: 巡检模块
    :param connect: 设备连接对象，传递给process_inspection_func()方法使用
    :param target_func_name: 需要执行的函数名称，从前端传入
    :param process_inspection_func: 数据保存方法，传递给process_inspection_func()方法使用
    :param file_service: 文件服务对象，传递给process_inspection_func()方法使用
    :param content_process: 数据保存方式，从前端传入的，传递给process_inspection_func()方法使用
    :param contents: 空列表，为保存到excel的数据做处理，收集数据后一次保存到excel
    :return:
    """
    if hasattr(module, target_func_name):
        func = getattr(module, target_func_name)
        logger.debug(f'执行的函数名字：{target_func_name} 执行的函数地址{func}')
        execute_and_process_result_with_lock(func=func,
                                             connect=connect,
                                             process_inspection_func=process_inspection_func,
                                             file_service=file_service,
                                             content_process=content_process,
                                             contents=contents)


def get_device_connect(device, plugins, process_inspection_func, file_service, content_process, contents, execute_all=True,
                       target_func_name=None):
    """
    获取设备连接对象方法
    :param device: netmiko设备字典
    :param plugins:要执行的模块对象
    :param process_inspection_func:数据保存方法，传递给process_inspection_func()方法使用
    :param file_service:文件服务对象，传递给process_inspection_func()方法使用
    :param content_process:数据保存方式，从前端传入的，传递给process_inspection_func()方法使用
    :param contents:空列表，为保存到excel的数据做处理，收集数据后一次保存到excel
    :param execute_all:前端传回参数，用于判断是执行all列表方法，还是自定义方法
    :param target_func_name:执行自定义方法时，必须从前端传回方法名称
    :return:
    """
    connect = None
    try:
        connect = ConnectHandler(**device[0])
        logger.info(f'登录成功{device[0].get("host")}')
        module = plugins.get(device[1].get('templates_name'))
        logger.debug(f'调用的模块：{module}')

        if execute_all:
            execute_all_functions(module, connect, process_inspection_func, file_service, content_process, contents)
        elif target_func_name:
            execute_fixed_function(module, connect, target_func_name, process_inspection_func, file_service,
                                   content_process, contents)
        else:
            logger.error('未指定执行方式')

    except Exception as e:
        logger.error(f'登录设备信息出错：{device[0].get("host")}：{e}')
    finally:
        if connect:
            connect.disconnect()
        else:
            logger.error(f'未获取到连接对象：{device[0].get("host")}')


def netmiko_connect_threaded(netmiko_data_and_templates, plugins, process_inspection_func, file_service,
                             content_process,
                             contents,
                             execute_all, target_func_name, delay_time=1, max_thread_count=4):
    """
    多线程巡检方法
    :param netmiko_data_and_templates: netmiko登录数据和模板名称
    :param plugins: 要执行的模块对象
    :param process_inspection_func: 数据保存方法，传递给process_inspection_func()方法使用
    :param file_service: 文件服务对象，传递给process_inspection_func()方法使用
    :param content_process: 数据保存方式，从前端传入的，传递给process_inspection_func()方法使用
    :param contents: 空列表，为保存到excel的数据做处理，收集数据后一次保存到excel
    :param execute_all: 前端传回参数，用于判断是执行all列表方法，还是自定义方法
    :param target_func_name: 执行自定义方法时，必须从前端传回方法名称
    :param delay_time: 每创建一个线程后等待时间，通过时间确认设备不乱序
    :param max_thread_count: 线程数量，默认4线程
    :return:
    """
    delay = delay_time
    # 创建线程池
    with ThreadPoolExecutor(max_workers=max_thread_count) as executor:
        for device in netmiko_data_and_templates:
            executor.submit(get_device_connect,
                            device=device,
                            plugins=plugins,
                            process_inspection_func=process_inspection_func,
                            file_service=file_service,
                            content_process=content_process,
                            contents=contents,
                            execute_all=execute_all,
                            target_func_name=target_func_name,
                            )
            sleep(delay)


def process_backup(file_service: FileService, contents: list, kwargs: dict) -> None:
    """
    处理备份配置文件实现
    :param file_service: 文件服务对象
    :param contents: 空列表
    :param kwargs: 巡检返回的数据
    :return:
    """
    _ = contents
    expected_keys = ['content', 'file_name']
    if all(key in kwargs for key in expected_keys):
        content = kwargs.get('content')
        file_name = kwargs.get('file_name')
        save_path = file_service.write_backup_config(backup_config_content=content,
                                                     backup_config_name=file_name)
        logger.info(f'备份配置文件保存路径：{save_path}')
    else:
        raise ValueError("巡检函数返回的内容必须格式为 {'content': content,'file_name': file_name}")


def process_txt(file_service: FileService, contents: list, kwargs: dict) -> None:
    """
    数据保存到txt方法
    :param file_service: 文件服务对象
    :param contents: 空列表
    :param kwargs: 巡检返回数据
    :return:
    """
    _ = contents
    expected_keys = ['content', 'file_path', 'file_name']
    if all(key in kwargs for key in expected_keys):
        content = kwargs.get('content')
        file_path = kwargs.get('file_path')
        file_name = kwargs.get('file_name')
        file_service.write_txt(content=content, file_path=file_path, file_name=file_name)
    else:
        raise ValueError(
            "巡检函数返回的内容必须格式为 {'content': content,'file_path': file_path ,'file_name': file_name}")


def process_excel(file_service: FileService, contents: list, kwargs: dict) -> None:
    """
    单表保存到excel实现
    :param file_service: 文件服务对象
    :param contents: 空列表
    :param kwargs: 巡检返回数据
    :return:
    """
    _ = file_service
    # 处理 excel 的逻辑
    expected_keys = ['content']
    if all(key in kwargs for key in expected_keys):
        content = kwargs.get('content')
        contents.append(content)
    else:
        raise ValueError(
            "巡检函数返回的内容必须格式为 {'content': {'table':Value}}")


def process_excel_sheet(file_service: FileService, contents: list, kwargs: dict) -> None:
    # 处理 excel_sheet 的逻辑
    """
    多表保存到excel实现
    :param file_service: 文件服务对象
    :param contents: 空列表
    :param kwargs: 巡检返回数据
    :return:
    """
    _ = contents
    expected_keys = ['content', 'file_name', 'sheet_name']
    if all(key in kwargs for key in expected_keys):
        content = kwargs.get('content')
        file_name = kwargs.get('file_name')
        sheet_name = kwargs.get('sheet_name')
        file_path = file_service.file_path_info.datasets_path
        file = file_service.file_path_info.join_path(file_path, file_name)
        file_service.write_inspection_data_to_excel(data=content, excel_file_path_name=file, sheet_name=sheet_name)
    else:
        raise ValueError(
            "巡检函数返回的内容必须格式为 {'content': {'table':Value},'file_name':file_name,'sheet_name':sheet_name}")


def process_custom(file_service: FileService, contents: list, kwargs: dict) -> None:
    """
    其他处理
    :param file_service: 文件服务对象
    :param contents: 空列表
    :param kwargs: 巡检返回数据
    :return:
    """
    # 处理 custom 的逻辑
    pass


def process_inspection_data(file_service: FileService, content_process, contents, **kwargs: Any) -> None:
    """
    数据保存方法
    :param file_service: 文件服务类
    :param content_process: 数据保存方式，从前端传入的
    :param contents: 空列表
    :param kwargs: 巡检返回数据
    :return:
    """
    process_functions = {
        'backup_txt': process_backup,
        'txt': process_txt,
        'excel': process_excel,
        'excel_sheet': process_excel_sheet,
        'custom': process_custom
    }
    if content_process in process_functions:
        process_function = process_functions[content_process]
        process_function(file_service, contents, kwargs)
    else:
        raise ValueError("不支持的 content_process 值")


def merge_dicts_with_common_keys(contents):
    """
    对返回到列表中的数据进行拼接成为可以存入excel的数据
    :param contents: 单表保存时添加进列表的数据
    :return:
    """
    merged_dicts = []
    current_dict = {}

    for item in contents:
        if any(key in current_dict for key in item):
            merged_dicts.append(current_dict)
            current_dict = {}
        current_dict.update(item)

    if current_dict:
        merged_dicts.append(current_dict)
    return merged_dicts


def run_task(get_dev_all_func: Callable[[Session], List[DeviceInfo]], config_manager: ConfigManager,
             file_service: FileService,
             content_process,
             execute_all: bool,
             target_func_name: None | str,
             delay_time: int,
             max_thread_count: int):
    """
    执行巡检入口函数
    :param get_dev_all_func: CRUD查询方法
    :param config_manager: 配置文件对象
    :param file_service: 文件服务对象
    :param content_process: 数据保存方式
    :param execute_all: 选择是自动还是自定义执行
    :param target_func_name: 需要执行的函数名称
    :param delay_time: 每创建一个线程等待时间
    :param max_thread_count: 线程数
    :return:
    """
    contents = []
    get_load_plugins = load_plugins(config=config_manager)
    get_db_data = get_device_info_from_db(get_dev_all_func)
    get_netmiko_data = generate_netmiko_data_and_templates(
        get_device_dict=get_db_data,
        netmiko_kernel_parameter=NetmikoKernelParameter,
        netmiko_optional_param=NetmikoOptionalParam,
        netmiko_inspection_templates=NetmikoInspectionTemplates,
        netmiko_device_type=NetmikoDeviceType,
        config=config_manager
    )
    netmiko_connect_threaded(netmiko_data_and_templates=get_netmiko_data,
                             plugins=get_load_plugins,
                             process_inspection_func=process_inspection_data,
                             file_service=file_service,
                             content_process=content_process,
                             contents=contents,
                             execute_all=execute_all,
                             target_func_name=target_func_name,
                             delay_time=delay_time,
                             max_thread_count=max_thread_count,
                             )
    if contents:
        content = merge_dicts_with_common_keys(contents)
        file = file_service.file_path_info.get_inspection_file_path()
        file_service.write_inspection_data_to_excel(data=content, excel_file_path_name=file)
        logger.info(f'巡检文件保存位置{file}')
    logger.info(f'------巡检完成---------')


def connect_test(host: str, port: int):
    """
    测试连接方法
    :param host: 主机
    :param port: 端口
    :return:
    """
    socket.setdefaulttimeout(3)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((host, port))
        logger.info(f'{host}连接正常')
        server.close()
    except Exception as e:
        logger.info(f'{host}存在连接问题{e}')

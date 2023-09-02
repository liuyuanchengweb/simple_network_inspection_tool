# from API.templates_interface import ReceivedData
import re
from netmiko import BaseConnection
from API.templates_interface import InterfaceEntry
from datetime import datetime

# receive_data = ReceivedData()

__all__ = ['huawei_name', 'huawei_version', 'huawei_cpu']

from API.logger import logger

interface_entry = InterfaceEntry()


def huawei_cpu(conn: BaseConnection):
    output = conn.send_command(command_string='display cpu-usage')
    datas = re.search(r'CPU Usage\s+:\s([0-9]{1,3}%)', output).group(1)
    return {'content': {'CPU': datas}}


def huawei_name(conn: BaseConnection):
    output = conn.send_command(command_string='display current-configuration | include sysname')
    datas = re.search(r'sysname\s(.*)', output).group(1)
    return {'content': {'name': datas}}


def huawei_version(conn: BaseConnection):
    output = conn.send_command(command_string='display version')
    datas = re.search(r'VRP \(R\) software, Version\s\S+\s\(\S+\s(V[0-9]+R[0-9]+C[0-9]+)\)', output).group(1)
    return {'content': {'version': datas}}


def backup_config(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display curr')
    file_names = re.search(r'sysname\s(.*)', output).group(1)
    file_name = f'{file_names}.txt'
    logger.info(f'执行完成backup_config函数---->文件名{file_name}')
    return {'content': output, 'file_name': file_name}


def save_text(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display curr')
    file_path = 'D:\home\py\simple_network_inspection_tool_0.1.1\datasets'
    file_name = 'save_text.txt'
    return {'content': output, 'file_path': file_path, 'file_name': file_name}


def save_database_interface_info(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display interface brief')
    fsm_obj = interface_entry.get_fsm_object(output, 'interface_info.textfsm')
    data = fsm_obj.get_parsed_data_as_json()
    sheet = conn.host
    interface_entry.database_insert_data(table_name='interface_table1-1', data_dict={
        "time": datetime.now(),
        "ip_add": sheet,
        "content": data,
    })

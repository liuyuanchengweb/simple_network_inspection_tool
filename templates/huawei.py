from API.decorator import DataHandle
import re
from netmiko import BaseConnection

data = DataHandle()

__all__ = ['huawei_name', 'huawei_version', 'huawei_cpu']


@data.backup_config
def backup_config(conn: BaseConnection):
    output = conn.send_command(command_string='display current-configuration')
    file_names = re.search(r'sysname\s(.*)', output).group(1)
    file_name = f'{file_names}.txt'
    data = output
    return data, file_name


@data.data
def huawei_cpu(conn: BaseConnection):
    print(f'------>执行了huawei_cpu方法')
    table = 'CPU'
    output = conn.send_command(command_string='display cpu-usage')
    data = re.search(r'CPU Usage\s+:\s([0-9]{1,3}%)', output).group(1)
    return data, table


@data.data
def huawei_name(conn: BaseConnection):
    print(f'------>执行了huawei_name方法')
    table = 'name'
    output = conn.send_command(command_string='display current-configuration | include sysname')
    data = re.search(r'sysname\s(.*)', output).group(1)
    return data, table


@data.data
def huawei_version(conn: BaseConnection):
    print(f'------>执行了huawei_version方法')
    table = 'version'
    output = conn.send_command(command_string='display version')
    data = re.search(r'VRP \(R\) software, Version\s\S+\s\(\S+\s(V[0-9]+R[0-9]+C[0-9]+)\)', output).group(1)
    return data, table


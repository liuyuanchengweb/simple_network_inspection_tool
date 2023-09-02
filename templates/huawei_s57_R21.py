import re
from netmiko import BaseConnection

__all__ = ['huawei_name', 'huawei_version', 'huawei_cpu', 'huawei_startup', 'huawei_patch_information',
           'huawei_fan', 'huawei_temperature', 'huawei_elabel', 'huawei_memory_usage']


def backup_config(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display current-configuration')
    file_names = re.search(r'sysname\s(.*)', output).group(1)
    file_name = f'{file_names}.txt'
    return {'content': output, 'file_name': file_name}


def huawei_cpu(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display cpu-usage')
    datas = re.search(r'CPU Usage\s+:\s([0-9]{1,3}%)', output).group(1)
    return {'content': {'CPU': datas}}


def huawei_name(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display current-configuration')
    datas = re.search(r'sysname (.*)', output).group(1)
    return {'content': {'name': datas}}


def huawei_version(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display version')
    version = re.search(r'VRP \(R\) software, Version\s\S+\s\(\S+\s(V[0-9]+R[0-9]+C[0-9]+SPC[0-9]+)\)', output).group(1)
    device_type = re.search(r'VRP \(R\) software, Version\s\S+\s\(\S+\s(V[0-9]+R[0-9]+C[0-9]+SPC[0-9]+)\)(\n.\S*\s\S*)',
                            output).group(2)
    return {'content': {'version': version, 'device_type': device_type}}


def huawei_startup(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display startup')
    Startup_system_software = re.search(r'Startup system software:\s(.*.cc)', output).group(1).strip()
    Next_startup_system_software = re.search(r'Next startup system software:\s(.*.cc)', output).group(1).strip()
    Startup_saved_configuration_file = re.search(r'Startup saved-configuration file:\s(.*)', output).group(1).strip()
    Next_startup_saved_configuration_file = re.search(r'Next startup saved-configuration file:\s(.*)', output).group(
        1).strip()
    return {'content': {'Startup_system_software': Startup_system_software,
                        'Next_startup_system_software': Next_startup_system_software,
                        'Startup_saved_configuration_file':Startup_saved_configuration_file,
                        'Next_startup_saved_configuration_file':Next_startup_saved_configuration_file,
                        }}


def huawei_patch_information(conn: BaseConnection):
    table = 'patch_information'
    output = conn.send_command_timing(command_string='display patch-information')
    datas = re.search(r'Patch Package Version:(.*)', output)
    if datas:
        d = datas.group(1)
    else:
        d = '没有补丁'
    return {'content': {'patch_information': d}}


def huawei_fan(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display fan')
    datas = re.search(r'Absent|Abnormal', output)
    if datas:
        d = '风扇异常'
    else:
        d = '风扇正常'
    return {'content': {'fan': d}}


def huawei_memory_usage(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display memory-usage')
    datas = re.search(r' Memory Using Percentage Is:\s(.*)', output).group(1)
    return {'content': {'memory_usage': datas}}


def huawei_temperature(conn: BaseConnection):
    table = 'temperature'
    output = conn.send_command_timing(command_string='display temperature all')
    datas = re.search(r'Abnormal', output)
    if datas:
        d = '温度异常'
    else:
        d = '温度正常'
    return {'content': {'temperature': d}}


def huawei_elabel(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display esn')
    datas = re.search(r'ESN of ([A-Z|a-z]*\s[0-9]):(.*)', output).group(2)
    return {'content': {'esn': datas}}

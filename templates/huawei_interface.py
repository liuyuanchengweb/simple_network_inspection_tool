import re
from API.logger import logger
from netmiko import BaseConnection
# 先实现了一个接口模块，统一了模板接口路径，导入了InterfaceEntry类，ReceivedData就是以前的DataHandle类，只是统一 到templates_interface模块
from API.templates_interface import InterfaceEntry

# received_data = ReceivedData()

__all__ = ['inter_info']


def inter_info(conn: BaseConnection):
    sheet_name = conn.host
    output = conn.send_command_timing(command_string='display interface brief')
    # 实例化一个InterfaceEntry类型，该类需要传入一个源数据，和textfsm模板名字
    fsm = InterfaceEntry(output, 'interface_info.textfsm')
    fsm_object = fsm.get_fsm_object()
    interface_info = fsm_object.get_parsed_data_as_json()
    fsm.write_database_interface_table(ip_add=sheet_name, inter_info=interface_info)


def backup_config(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display curr')
    file_names = re.search(r'sysname\s(.*)', output).group(1)
    file_name = f'{file_names}.txt'
    # received_data.backup_file_save(output, file_name)
    logger.info(f'执行完成backup_config函数---->文件名{file_name}')
    return {'content': output, 'file_name': file_name}


def test_txt(conn: BaseConnection):
    output = conn.send_command_timing(command_string='display curr')
    file_path = 'D:\home\py\simple_network_inspection_tool_0.1.1'
    file_name = 'text.txt'
    return {'content': output, 'file_path': file_path, 'file_name': file_name}

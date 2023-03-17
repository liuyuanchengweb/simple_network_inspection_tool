import json
import os

config = {
    'netmiko_connect': {
        'conn_timeout': 30,
        'timeout': 120,
        'global_delay_factor': 1,
        'fast_cli': True
    }}


def config_init():
    config_json = json.dumps(config, sort_keys=True, indent=4, separators=(',', ':'))
    with open(os.path.join(os.path.abspath(os.curdir), 'config.json'), 'w') as f:
        f.write(config_json)


def config_get() -> dict:
    with open(os.path.join(os.path.abspath(os.curdir), 'config.json'), 'r') as f:
        config_json = f.read()
        config_dict = json.loads(config_json)
        return config_dict




def netmiko_config():
    net_con = config_get().get('netmiko_connect')
    return net_con



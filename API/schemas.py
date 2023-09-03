from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import os

CLASS_MAPPER_BASE = {
    "a10": 'A10',
    "accedian": 'Accedian',
    "adtran_os": 'AdtranOS',
    "alcatel_aos": 'AlcatelAos',
    "alcatel_sros": 'NokiaSros',
    "allied_telesis_awplus": 'AlliedTelesisAwplus',
    "apresia_aeos": 'ApresiaAeos',
    "arista_eos": 'Arista',
    "aruba_os": 'Aruba',
    "aruba_osswitch": 'HPProcurve',
    "aruba_procurve": 'HPProcurve',
    "audiocode_72": 'Audiocode72',
    "audiocode_66": 'Audiocode66',
    "audiocode_shell": 'AudiocodeShell',
    "avaya_ers": 'ExtremeErs',
    "avaya_vsp": 'ExtremeVsp',
    "broadcom_icos": 'BroadcomIcos',
    "brocade_fos": 'BrocadeFOS',
    "brocade_fastiron": 'RuckusFastiron',
    "brocade_netiron": 'ExtremeNetiron',
    "brocade_nos": 'ExtremeNos',
    "brocade_vdx": 'ExtremeNos',
    "brocade_vyos": 'VyOS',
    "checkpoint_gaia": 'CheckPointGaia',
    "calix_b6": 'CalixB6',
    "cdot_cros": 'CdotCros',
    "centec_os": 'CentecOS',
    "ciena_saos": 'CienaSaos',
    "cisco_asa": 'CiscoAsa',
    "cisco_ftd": 'CiscoFtd',
    "cisco_ios": 'CiscoIos',
    "cisco_nxos": 'CiscoNxos',
    "cisco_s300": 'CiscoS300',
    "cisco_tp": 'CiscoTpTcCe',
    "cisco_viptela": 'CiscoViptela',
    "cisco_wlc": 'CiscoWlc',
    "cisco_xe": 'CiscoIos',
    "cisco_xr": 'CiscoXr',
    "cloudgenix_ion": 'CloudGenixIon',
    "coriant": 'Coriant',
    "dell_dnos9": 'DellForce10',
    "dell_force10": 'DellForce10',
    "dell_os6": 'DellDNOS6',
    "dell_os9": 'DellForce10',
    "dell_os10": 'DellOS10',
    "dell_sonic": 'DellSonic',
    "dell_powerconnect": 'DellPowerConnect',
    "dell_isilon": 'DellIsilon',
    "dlink_ds": 'DlinkDS',
    "endace": 'Endace',
    "eltex": 'Eltex',
    "eltex_esr": 'EltexEsr',
    "enterasys": 'Enterasys',
    "ericsson_ipos": 'EricssonIpos',
    "extreme": 'ExtremeExos',
    "extreme_ers": 'ExtremeErs',
    "extreme_exos": 'ExtremeExos',
    "extreme_netiron": 'ExtremeNetiron',
    "extreme_nos": 'ExtremeNos',
    "extreme_slx": 'ExtremeSlx',
    "extreme_tierra": 'ExtremeTierra',
    "extreme_vdx": 'ExtremeNos',
    "extreme_vsp": 'ExtremeVsp',
    "extreme_wing": 'ExtremeWing',
    "f5_ltm": 'F5Tmsh',
    "f5_tmsh": 'F5Tmsh',
    "f5_linux": 'F5Linux',
    "flexvnf": 'Flexvnf',
    "fortinet": 'Fortinet',
    "generic": 'Generic',
    "generic_termserver": 'TerminalServer',
    "hp_comware": 'HPComware',
    "hp_procurve": 'HPProcurve',
    "huawei": 'Huawei',
    "huawei_smartax": 'HuaweiSmartAX',
    "huawei_olt": 'HuaweiSmartAX',
    "huawei_vrpv8": 'HuaweiVrpv8',
    "ipinfusion_ocnos": 'IpInfusionOcNOS',
    "juniper": 'Juniper',
    "juniper_junos": 'Juniper',
    "juniper_screenos": 'JuniperScreenOs',
    "keymile": 'Keymile',
    "keymile_nos": 'KeymileNOS',
    "linux": 'Linux',
    "mikrotik_routeros": 'MikrotikRouterOs',
    "mikrotik_switchos": 'MikrotikSwitchOs',
    "mellanox": 'MellanoxMlnxos',
    "mellanox_mlnxos": 'MellanoxMlnxos',
    "mrv_lx": 'MrvLx',
    "mrv_optiswitch": 'MrvOptiswitch',
    "netapp_cdot": 'NetAppcDot',
    "netgear_prosafe": 'NetgearProSafe',
    "netscaler": 'Netscaler',
    "nokia_sros": 'NokiaSros',
    "nokia_srl": 'NokiaSrl',
    "oneaccess_oneos": 'OneaccessOneOS',
    "ovs_linux": 'OvsLinux',
    "paloalto_panos": 'PaloAltoPanos',
    "pluribus": 'Pluribus',
    "quanta_mesh": 'QuantaMesh',
    "rad_etx": 'RadETX',
    "raisecom_roap": 'RaisecomRoap',
    "ruckus_fastiron": 'RuckusFastiron',
    "ruijie_os": 'RuijieOS',
    "sixwind_os": 'SixwindOS',
    "sophos_sfos": 'SophosSfos',
    "supermicro_smis": 'SmciSwitchSmis',
    "tplink_jetstream": 'TPLinkJetStream',
    "ubiquiti_edge": 'UbiquitiEdge',
    "ubiquiti_edgerouter": 'UbiquitiEdgeRouter',
    "ubiquiti_edgeswitch": 'UbiquitiEdge',
    "ubiquiti_unifiswitch": 'UbiquitiUnifiSwitch',
    "vyatta_vyos": 'VyOS',
    "vyos": 'VyOS',
    "watchguard_fireware": 'WatchguardFireware',
    "zte_zxros": 'ZteZxros',
    "yamaha": 'Yamaha',
    "zyxel_os": 'Zyxel',
}


class DeviceType(Enum):
    a10 = 'a10'
    accedian = 'accedian'
    adtran_os = 'adtran_os'
    alcatel_aos = 'alcatel_aos'
    alcatel_sros = 'alcatel_sros'
    allied_telesis_awplus = 'allied_telesis_awplus'
    apresia_aeos = 'apresia_aeos'
    arista_eos = 'arista_eos'
    aruba_os = 'aruba_os'
    aruba_osswitch = 'aruba_osswitch'
    aruba_procurve = 'aruba_procurve'
    audiocode_72 = 'audiocode_72'
    audiocode_66 = 'audiocode_66'
    audiocode_shell = 'audiocode_shell'
    avaya_ers = 'avaya_ers'
    avaya_vsp = 'avaya_vsp'
    broadcom_icos = 'broadcom_icos'
    brocade_fos = 'brocade_fos'
    brocade_fastiron = 'brocade_fastiron'
    brocade_netiron = 'brocade_netiron'
    brocade_nos = 'brocade_nos'
    brocade_vdx = 'brocade_vdx'
    brocade_vyos = 'brocade_vyos'
    checkpoint_gaia = 'checkpoint_gaia'
    calix_b6 = 'calix_b6'
    cdot_cros = 'cdot_cros'
    centec_os = 'centec_os'
    ciena_saos = 'ciena_saos'
    cisco_asa = 'cisco_asa'
    cisco_ftd = 'cisco_ftd'
    cisco_ios = 'cisco_ios'
    cisco_nxos = 'cisco_nxos'
    cisco_s300 = 'cisco_s300'
    cisco_tp = 'cisco_tp'
    cisco_viptela = 'cisco_viptela'
    cisco_wlc = 'cisco_wlc'
    cisco_xe = 'cisco_xe'
    cisco_xr = 'cisco_xr'
    cloudgenix_ion = 'cloudgenix_ion'
    coriant = 'coriant'
    dell_dnos9 = 'dell_dnos9'
    dell_force10 = 'dell_force10'
    dell_os6 = 'dell_os6'
    dell_os9 = 'dell_os9'
    dell_os10 = 'dell_os10'
    dell_sonic = 'dell_sonic'
    dell_powerconnect = 'dell_powerconnect'
    dell_isilon = 'dell_isilon'
    dlink_ds = 'dlink_ds'
    endace = 'endace'
    eltex = 'eltex'
    eltex_esr = 'eltex_esr'
    enterasys = 'enterasys'
    ericsson_ipos = 'ericsson_ipos'
    extreme = 'extreme'
    extreme_ers = 'extreme_ers'
    extreme_exos = 'extreme_exos'
    extreme_netiron = 'extreme_netiron'
    extreme_nos = 'extreme_nos'
    extreme_slx = 'extreme_slx'
    extreme_tierra = 'extreme_tierra'
    extreme_vdx = 'extreme_vdx'
    extreme_vsp = 'extreme_vsp'
    extreme_wing = 'extreme_wing'
    f5_ltm = 'f5_ltm'
    f5_tmsh = 'f5_tmsh'
    f5_linux = 'f5_linux'
    flexvnf = 'flexvnf'
    fortinet = 'fortinet'
    generic = 'generic'
    generic_termserver = 'generic_termserver'
    hp_comware = 'hp_comware'
    hp_procurve = 'hp_procurve'
    huawei = 'huawei'
    huawei_smartax = 'huawei_smartax'
    huawei_olt = 'huawei_olt'
    huawei_vrpv8 = 'huawei_vrpv8'
    ipinfusion_ocnos = 'ipinfusion_ocnos'
    juniper = 'juniper'
    juniper_junos = 'juniper_junos'
    juniper_screenos = 'juniper_screenos'
    keymile = 'keymile'
    keymile_nos = 'keymile_nos'
    linux = 'linux'
    mikrotik_routeros = 'mikrotik_routeros'
    mikrotik_switchos = 'mikrotik_switchos'
    mellanox = 'mellanox'
    mellanox_mlnxos = 'mellanox_mlnxos'
    mrv_lx = 'mrv_lx'
    mrv_optiswitch = 'mrv_optiswitch'
    netapp_cdot = 'netapp_cdot'
    netgear_prosafe = 'netgear_prosafe'
    netscaler = 'netscaler'
    nokia_sros = 'nokia_sros'
    nokia_srl = 'nokia_srl'
    oneaccess_oneos = 'oneaccess_oneos'
    ovs_linux = 'ovs_linux'
    paloalto_panos = 'paloalto_panos'
    pluribus = 'pluribus'
    quanta_mesh = 'quanta_mesh'
    rad_etx = 'rad_etx'
    raisecom_roap = 'raisecom_roap'
    ruckus_fastiron = 'ruckus_fastiron'
    ruijie_os = 'ruijie_os'
    sixwind_os = 'sixwind_os'
    sophos_sfos = 'sophos_sfos'
    supermicro_smis = 'supermicro_smis'
    tplink_jetstream = 'tplink_jetstream'
    ubiquiti_edge = 'ubiquiti_edge'
    ubiquiti_edgerouter = 'ubiquiti_edgerouter'
    ubiquiti_edgeswitch = 'ubiquiti_edgeswitch'
    ubiquiti_unifiswitch = 'ubiquiti_unifiswitch'
    vyatta_vyos = 'vyatta_vyos'
    vyos = 'vyos'
    watchguard_fireware = 'watchguard_fireware'
    zte_zxros = 'zte_zxros'
    yamaha = 'yamaha'
    zyxel_os = 'zyxel_os'


class Protocol(Enum):
    ssh = 'ssh'
    telnet = 'telnet'


class ResponseDeviceIn(BaseModel):
    id: Optional[int]
    hostname: str
    device_type: DeviceType
    username: str
    protocol: Protocol
    port: Optional[int] = 22
    templates_name: Optional[str] = None


class DeviceIn(ResponseDeviceIn):
    password: str
    super_pw: Optional[str] = None


class InterInfo(BaseModel):
    pass


class InterfaceInfo(BaseModel):
    """
    模型类，实现通过pydantic校验，也是一个结构体
    """
    id: Optional[int]
    collect_time: datetime = datetime.now()
    ip_add: str
    inter_info: str


class DirPath(BaseModel):
    base_dir: str = os.path.abspath(os.curdir)
    templates_dir: str = 'templates'
    textfsm_templates_dir: str = 'textfsm_templates'
    logs_dir: str = 'Logs'
    datasets_dir: str = 'Datasets'
    customer_data_export_dir: str = 'Customer_Data_Export'
    backup_device_config_file_dir: str = 'backup_config'


class FileName(BaseModel):
    upload_template_name: str = 'upload_template_zh_CN.xls'
    network_device_inspection_file_name: str = 'Network_Device_Inspection.xlsx'


class NetmikoDeviceType(BaseModel):
    protocol: str = ''
    device_type: str = ''


class NetmikoKernelParameter(BaseModel):
    ip: str = ""
    host: str = ""
    username: str = ""
    password: Optional[str] = None
    secret: str = Field(default=None)
    port: Optional[int] = None

    @classmethod
    @validator('secret', pre=True, always=True)
    def convert_none_to_empty_string(cls, value):
        if value is None:
            return ''
        return value


class NetmikoOptionalParam(BaseModel):
    conn_timeout: int = 30
    timeout: int = 120
    global_delay_factor: int = 1
    fast_cli: bool = True
    session_log: str = os.path.join(os.path.abspath(os.curdir), 'Logs', 'netmiko_session_log.txt')
    session_log_record_writes: bool = True
    session_log_file_mode: str = 'append'
    allow_auto_change: bool = False
    encoding: str = "utf-8"


class NetmikoInspectionTemplates(BaseModel):
    templates_name: str


class DatabaseConfig(BaseModel):
    drivername: str = 'sqlite'
    username: Optional[str]
    password: Optional[str]
    host: Optional[str]
    port: Optional[int]
    database: Optional[str] = '/database.sqlite3'


class Configuration(BaseModel):
    database_url: DatabaseConfig = DatabaseConfig()
    device_task_delay: int = 1
    device_task_threads: int = 4
    dir_path: DirPath = DirPath()
    file_name: FileName = FileName()
    netmiko_param: NetmikoOptionalParam = NetmikoOptionalParam()


class ContentProcessEnum(str, Enum):
    backup_txt: str = '备份配置文件'
    txt: str = '保存内容txt'
    excel: str = '保存内容单表excel'
    excel_sheet: str = '保存多表excel'
    custom: str = '自定义保存格式'


class InspectionOption(BaseModel):
    execute_all: bool
    target_func_name: Optional[str]
    content_process: ContentProcessEnum = Field(ContentProcessEnum.backup_txt, description="Choose a content process")


def create_status_enum_class(enum_name, enum_fields: dict):
    return Enum(enum_name, enum_fields)


class TestDeviceOption(BaseModel):
    pattern: bool
    hostname: Optional[str]
    port: Optional[int]

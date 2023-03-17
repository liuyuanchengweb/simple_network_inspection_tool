import asyncio
import os
from sqlalchemy.orm import sessionmaker
from typing import List
from .database import engine, Base
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, WebSocket
from .schemas import ResponseDeviceIn, DeviceIn
from starlette.responses import FileResponse
from .utility import Module, Start, log_date
from .file_handle import file_handle
from API import crud
from .decorator import DataHandle
from .config import config_init

application = APIRouter()
module = asyncio.run(Module().load_plugins())
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_conn = engine.connect()
config_init()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@application.post("/add_device", response_model=ResponseDeviceIn, summary='添加设备')
def create_device(device: DeviceIn, db: Session = Depends(get_db)):
    """
    添加设备接口，传入设备信息，返回一个添加的设备字典
    :param device: json
    :param db:
    :return: json
    """
    db_device = crud.create_device(db=db, device=device)
    return db_device.to_dict()


@application.get("/download_dev_profile", summary='下载接口')
def download_dev_profile():
    """
    下载设备模板接口
    :return:
    """
    file_handle.database_to_file()
    return FileResponse(file_handle.download_path,
                        headers={"content-disposition": 'attachment; filename="uploadnes_template_zh_CN.xlsx"'})


@application.post("/upload_dev_profile", summary="上传接口")
async def upload_dev_profile(file: UploadFile = File(...)):
    """
    上传设备信息，传入excel文件，会对字段进行检查
    :param file: excel文件类型
    :return:
    """
    file_name = file.filename
    file_data = await file.read()
    await file_handle.excel_to_database(file_data, file_name)
    return {'msg': 'ok'}


@application.get("/get_dev", response_model=List[ResponseDeviceIn], summary='分页查询接口')
def get_dev(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    分页查询设备信息
    :param skip: 开始数据
    :param limit: 结束数据
    :param db:
    :return: [{device_info},{device_info}...]
    """
    device_info = crud.get_dev(db=db, skip=skip, limit=limit)
    device = [device.to_dict() for device in device_info]
    return device


@application.get("/get_count", summary='查询设备总条数')
def get_count(db: Session = Depends(get_db)):
    return crud.get_count(db)


@application.get("/update_que", response_model=DeviceIn, summary='查询接口，返回所有数据')
def que_hostname(hostname: str, db: Session = Depends(get_db)):
    """
    根据hostname查询数据库接口,用作修改设备信息时，查询返回信息做为默认值，修改后提交到updata接口
    :param hostname: hostname地址，str
    :param db:
    :return: {device_info}
    """

    res = crud.get_hostname(db=db, hostname=hostname)
    if res:
        return res.to_dict()
    else:
        raise HTTPException(status_code=404, detail='设备不存在')


@application.post("/update_dev", response_model=ResponseDeviceIn, summary='修改设备信息接口')
def update(device_info: DeviceIn, db: Session = Depends(get_db)):
    """
    修改设备信息接口，传入设备信息
    :param device_info: {       "id": 2,                     需要修改设备的ID
                                "hostname": "172.16.1.11",   修改后的hostname
                                "templates_name": "huawei",     修改后的device_type
                                "username": "admin",         修改后的username
                                "protocol": "ssh",            修改后的protocol
                                "port": 22,                   修改后的port
                                "password": "Huawei@123",     修改后的password
                                "super_pw": null              修改后的super_pw}
    :param db: 
    :return: {device_info}
    """
    res = crud.update_device_info(db=db, device_info=device_info)
    return res.to_dict()


@application.get("/del", summary='删除设备接口')
def delete_device(id_name: int, db: Session = Depends(get_db)):
    """
    删除设备信息
    :param id_name: id
    :param db:
    :return:
    """
    crud.delete_device_info(db=db, id_name=id_name)
    return {"msg": "ok"}


@application.get("/que_host", response_model=ResponseDeviceIn, summary='hostname查询接口')
def get_hostname(hostname: str, db: Session = Depends(get_db)):
    """
    通过hostname查找设备
    :param hostname: hostname
    :param db:
    :return: {device_info}
    """
    res = crud.get_hostname(db=db, hostname=hostname)
    if res:
        return res.to_dict()
    else:
        raise HTTPException(status_code=404, detail='未找到设备')


@application.websocket("/ws/start")
async def ws_start(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    启动巡检接口
    :param websocket: websocket类
    :param db: db连接对象
    :return:
    """
    device_obj = crud.get_dev_all(db)
    await websocket.accept()
    await websocket.send_text('连接成功')
    start = Start()
    await start.connect_on(device_obj, module, websocket)
    file_path = file_handle.patrol_network_to_excel(DataHandle.data_dict)
    log_info = f'{log_date()}巡检文件路径为{os.path.realpath(file_path)}'
    await websocket.send_text(log_info)
    DataHandle.data_dict.clear()
    await websocket.send_text('完成断开链接')
    await websocket.close()


@application.websocket("/ws/BackupConfig")
async def ws_backup_config(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    备份配置文件接口
    :param websocket:  websocket类
    :param db: db连接对象
    :return:
    """
    device_obj = crud.get_dev_all(db)
    await websocket.accept()
    await websocket.send_text('连接成功')
    start = Start()
    await start.connect_backup(device_obj, module, websocket)
    await websocket.send_text('完成断开链接')
    await websocket.close()


@application.websocket("/ws/ConnectTest")
async def ws_connect_test(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    测试设备连通性接口
    :param websocket: websocket类
    :param db: db连接对象
    :return:
    """
    device_obj = crud.get_dev_all(db)
    await websocket.accept()
    await websocket.send_text('连接成功')
    start = Start()
    await start.connect_test(device_obj, module, websocket)
    await websocket.send_text('完成断开链接')
    await websocket.close()

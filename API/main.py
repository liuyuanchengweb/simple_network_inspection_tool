import asyncio
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, WebSocket
from websockets.exceptions import ConnectionClosedError
from starlette.responses import FileResponse
from API import crud
from API.file_operations import get_db, Session, FileHandler, FilePathInfo, FileService, ResponseDeviceIn, DeviceIn, \
    InspectionOption, TestDeviceOption
from API.config import ConfigManager
from API.logger import log_queue, logger
from API.device_management import run_task, connect_test

application = APIRouter()
app_websocket = APIRouter()
config = ConfigManager()
file_handler = FileHandler()
file_path_info = FilePathInfo(config=config)
file_service = FileService(file_handler, file_path_info)


@app_websocket.websocket('/ws')
async def handle_websocket(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            while not log_queue.empty():
                queue_data = log_queue.get()
                await websocket.send_json({'msg': f'"日志数据: {queue_data}"'})
            await websocket.send_json({'msg': 'ok'})
            await asyncio.sleep(0.50)
    except ConnectionClosedError:
        logger.debug("WebSocket connection closed.")
    except Exception as e:
        logger.error(f'websocket服务异常关闭{e}')
    finally:
        await websocket.close()
        print(f'--------------关闭连接')


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
    file = file_service.get_upload_template_zh_CN_file()
    try:
        return FileResponse(file[0],
                            headers={"content-disposition": 'attachment; filename="uploadnes_template_zh_CN.xlsx"'})
    except Exception as e:
        return {'error': e}


@application.post("/upload_dev_profile", summary="上传接口")
async def upload_dev_profile(file: UploadFile = File(...)):
    """
    上传设备信息，传入excel文件，会对字段进行检查
    :param file: excel文件类型
    :return:
    """
    file_data = await file.read()
    file_service.write_upload_template_zh_CN_file(file_data, crud.get_hostname, crud.create_device)
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


@application.post("/DeviceStart")
async def device_start(action: InspectionOption):
    execute_all = action.execute_all
    target_func_name = action.target_func_name
    content_process = action.content_process.name
    run_task(get_dev_all_func=crud.get_dev_all,
             config_manager=config,
             file_service=file_service,
             content_process=content_process,
             execute_all=execute_all,
             target_func_name=target_func_name,
             delay_time=config.get_config.device_task_delay,
             max_thread_count=config.get_config.device_task_threads
             )
    return {'msg': 'ok'}


@application.post("/TestDevice")
async def test_device(action: TestDeviceOption, db: Session = Depends(get_db)):
    if action.pattern:
        for device in crud.get_dev_all(db=db):
            host = device.hostname
            port = device.port
            connect_test(host=host, port=port)
    else:
        host = action.hostname
        port = action.port
        connect_test(host=host, port=port)
    return {'msg': 'ok'}

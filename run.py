import threading
import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from API import application, app_websocket

app = FastAPI()
web_app = FastAPI()
if not os.path.exists('./static'):
    os.mkdir('./static')

app.mount('/static', StaticFiles(directory='./static'), name="static")
app.include_router(application, prefix="/API", tags=["API"])
web_app.include_router(app_websocket, prefix="/API", tags=["API"])


@app.get("/")
async def root():
    redirect_url = f'/index'
    return RedirectResponse(redirect_url)


@app.get("/index")
async def index() -> HTMLResponse:
    html_path = './index.html'
    with open(html_path) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


def start_websocket_server():
    uvicorn.run("run:web_app", host="0.0.0.0", port=18887)


if __name__ == '__main__':
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()
    uvicorn.run("run:app", host='0.0.0.0', port=18888)

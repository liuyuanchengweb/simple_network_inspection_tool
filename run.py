import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from API import application
import os

app = FastAPI()
if not os.path.exists('./static'):
    os.mkdir('./static')

app.mount('/static', StaticFiles(directory='./static'), name="static")
app.include_router(application, prefix="/API", tags=["API"])


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


if __name__ == '__main__':
    uvicorn.run("run:app", host='0.0.0.0', port=18888, reload=True, workers=3)

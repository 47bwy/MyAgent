# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 15:14:47
@Author  :   47bwy
@Desc    :   FastAPI 的应用入口，定义 app = FastAPI() 并挂载路由。
'''

from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.core.logger import get_logger, setup_logging
from app.core.db import init_db
from app.models.user import User
from app.routers import auth, qa
from app.routers.auth import get_current_user

setup_logging()
logger = get_logger(__name__)
logger.info("🚀 项目启动！")

app = FastAPI(title="AI QA System")

init_db()

# 设置 Jinja2 模板引擎
templates = Jinja2Templates(directory="app/templates")

app.include_router(qa.router, prefix="/qa", tags=["qa"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def home(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/auth/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/auth/me")
async def get_me(user: str = Depends(get_current_user)):
    return {"username": user}
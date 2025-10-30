# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:32:33
@Author  :   47bwy
@Desc    :   None
'''

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core import db
from app.auth import auth
from app.auth.auth import get_current_user
from app.core.config import settings
from app.schemas.user import UserCreate, UserLogin

router = APIRouter()


# 注册用户
@router.post("/register")
def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(db.get_db)
):
    # 校验密码是否一致
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # 检查用户名是否已存在
    db_user = auth.get_user(db, username=username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 创建新用户
    new_user = auth.create_user(db=db, username=username, password=password, email=email)
    
    return {"message": "User registered successfully", "username": new_user.username}

# 登录用户
@router.post("/login")
def login_user(
    username: str = Form(...),  # 使用 Form 接收表单数据
    password: str = Form(...),
    db: Session = Depends(db.get_db)
):
    db_user = auth.get_user(db, username=username)
    if not db_user or not auth.verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # 生成 JWT token
    access_token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# 登出用户
@router.get("/logout")
def logout_user(user: str = Depends(get_current_user)):
    # 这里你可以选择删除 JWT token 或进行其他操作来处理用户注销
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")  # 删除存储在 cookie 中的 JWT token
    return response




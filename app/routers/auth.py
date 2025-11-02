# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:32:33
@Author  :   47bwy
@Desc    :   None
'''

from fastapi import APIRouter, Depends, HTTPException
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
    user_data: UserCreate,  # 使用 Pydantic 模型，自动进行类型和格式校验
    db: Session = Depends(db.get_db)
):
    """
    注册新用户
    
    Pydantic 已自动校验：
    - username: 3-50个字符，只能包含字母、数字和下划线
    - email: 正确的邮箱格式
    - password: 至少8个字符，包含数字和字母
    - confirm_password: 与 password 匹配
    """
    # 检查用户名是否已存在（业务逻辑校验，需要查询数据库）
    db_user = auth.get_user(db, username=user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 检查邮箱是否已存在（可选，如果需要的话）
    # db_user_by_email = auth.get_user_by_email(db, email=user_data.email)
    # if db_user_by_email:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    new_user = auth.create_user(db=db, user_data=user_data)
    
    return {"message": "User registered successfully", "username": new_user.username}


# 登录用户
@router.post("/login")
def login_user(
    user_data: UserLogin,  # 使用 Pydantic 模型，自动进行类型和格式校验
    db: Session = Depends(db.get_db)
):
    """
    用户登录
    
    Pydantic 已自动校验：
    - username: 至少1个字符
    - password: 至少1个字符
    """
    db_user = auth.get_user(db, username=user_data.username)
    if not db_user or not auth.verify_password(user_data.password, db_user.password_hash):
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




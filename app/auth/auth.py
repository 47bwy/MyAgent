# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 22:09:13
@Author  :   47bwy
@Desc    :   None
'''


from datetime import datetime, timedelta, timezone

import redis
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models import User

logger = get_logger(__name__)

# 加密密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 配置 Redis 连接
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# JWT 配置
SECRET_KEY = "a5c6e8f497d8ad2a3b0899a5f8157f7c74eb5c2e7b03e5459fe301d5d4ff16b1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600  # Token 过期时间

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# 创建用户（注册）
def create_user(db: Session, username: str, password: str, email: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password_hash=hashed_password, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 登录，生成 Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取用户
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# 访客提问限制（基于 Redis）
def check_visitor_limit(user_id: str):
    current_day = datetime.now().strftime('%Y-%m-%d')
    key = f"user:{user_id}:questions:{current_day}"
    count = r.get(key)
    if count and int(count) >= 5:
        return False  # 达到每日提问限制
    else:
        r.incr(key)  # 增加提问次数
        r.expire(key, 86400)  # 设置过期时间（24小时）
        return True
    

def get_optional_user(token: str = Depends(oauth2_scheme)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

# 从请求的 Token 中获取当前用户信息
def get_current_user(token: str = Depends(oauth2_scheme)):
    if token is None:
        # 访客用户，不提供 token 时标识为 "guest"
        return "guest"
    
    try:
        # 解码 token 并验证
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        logger.info(f"Authenticated user: {username}")
        return username  # 返回用户名作为当前用户标识
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
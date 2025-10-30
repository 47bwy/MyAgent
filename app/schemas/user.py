# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 15:13:24
@Author  :   47bwy
@Desc    :   请求和响应 Pydantic 模型
'''

from pydantic import BaseModel


# 用户注册请求模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str


# 用户登录请求模型
class UserLogin(BaseModel):
    username: str
    password: str

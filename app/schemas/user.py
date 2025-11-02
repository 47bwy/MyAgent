# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 15:13:24
@Author  :   47bwy
@Desc    :   请求和响应 Pydantic 模型
'''

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional


# 用户注册请求模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名，3-50个字符")
    email: EmailStr = Field(..., description="邮箱地址")  # EmailStr 会自动校验邮箱格式
    password: str = Field(..., min_length=8, description="密码，至少8个字符")
    confirm_password: str = Field(..., description="确认密码")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """校验用户名格式：只能包含字母、数字和下划线"""
        # 检查是否只包含字母、数字和下划线
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """校验密码强度"""
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含至少一个字母')
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'UserCreate':
        """校验两次输入的密码是否一致"""
        if self.password != self.confirm_password:
            raise ValueError('密码和确认密码不匹配')
        return self


# 用户登录请求模型
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")

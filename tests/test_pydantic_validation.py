# -*- encoding: utf-8 -*-
"""
测试 Pydantic 模型验证
"""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserLogin


def test_user_create_valid():
    """测试有效的用户创建数据"""
    user_data = UserCreate(
        username="testuser123",
        email="test@example.com",
        password="password123",
        confirm_password="password123"
    )
    assert user_data.username == "testuser123"
    assert user_data.email == "test@example.com"


def test_user_create_invalid_username_short():
    """测试用户名太短"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            username="ab",  # 少于 3 个字符
            email="test@example.com",
            password="password123",
            confirm_password="password123"
        )
    assert "至少" in str(exc_info.value) or "minimum" in str(exc_info.value).lower()


def test_user_create_invalid_username_chars():
    """测试用户名包含非法字符"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            username="test@user",  # 包含 @ 符号
            email="test@example.com",
            password="password123",
            confirm_password="password123"
        )
    assert "字母、数字和下划线" in str(exc_info.value) or "alphanumeric" in str(exc_info.value).lower()


def test_user_create_invalid_email():
    """测试无效邮箱"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            username="testuser",
            email="invalid-email",  # 无效邮箱格式
            password="password123",
            confirm_password="password123"
        )
    assert "email" in str(exc_info.value).lower()


def test_user_create_password_mismatch():
    """测试密码不匹配"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            confirm_password="password456"  # 不匹配
        )
    assert "不匹配" in str(exc_info.value) or "match" in str(exc_info.value).lower()


def test_user_create_weak_password():
    """测试弱密码（只有数字）"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="12345678",  # 只有数字
            confirm_password="12345678"
        )
    assert "字母" in str(exc_info.value) or "letter" in str(exc_info.value).lower()


def test_user_login_valid():
    """测试有效的登录数据"""
    login_data = UserLogin(
        username="testuser",
        password="password123"
    )
    assert login_data.username == "testuser"
    assert login_data.password == "password123"


def test_user_login_empty_username():
    """测试空用户名"""
    with pytest.raises(ValidationError):
        UserLogin(
            username="",  # 空字符串
            password="password123"
        )


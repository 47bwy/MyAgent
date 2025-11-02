# -*- encoding: utf-8 -*-
"""
测试认证相关的 API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.db import Base, get_db

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_register_user_success(client):
    """测试成功注册用户"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == "testuser"


def test_register_user_duplicate_username(client):
    """测试重复用户名注册"""
    # 先注册一个用户
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )
    
    # 尝试用相同用户名注册
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_user_password_mismatch(client):
    """测试密码不匹配"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password456"  # 不匹配
        }
    )
    assert response.status_code == 422  # Pydantic 验证错误
    data = response.json()
    assert "detail" in data


def test_register_user_invalid_email(client):
    """测试无效邮箱格式"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "invalid-email",  # 无效邮箱
            "password": "password123",
            "confirm_password": "password123"
        }
    )
    assert response.status_code == 422  # Pydantic 验证错误


def test_register_user_short_password(client):
    """测试密码太短"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",  # 少于 8 个字符
            "confirm_password": "short"
        }
    )
    assert response.status_code == 422  # Pydantic 验证错误


def test_login_success(client):
    """测试成功登录"""
    # 先注册用户
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )
    
    # 登录
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """测试无效凭据登录"""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


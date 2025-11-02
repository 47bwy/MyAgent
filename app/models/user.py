# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:38:39
@Author  :   47bwy
@Desc    :   用户模型
'''

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    
    # 定义与 Question 的关系（可选，如果需要通过 user.questions 访问用户的所有问题）
    # questions = relationship("Question", back_populates="user")





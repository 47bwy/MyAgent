# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:38:39
@Author  :   47bwy
@Desc    :   None
'''

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)





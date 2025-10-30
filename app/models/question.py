# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/16 15:08:43
@Author  :   47bwy
@Desc    :   None
'''

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.core.db import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    user_id = Column(String, ForeignKey("users.username"))
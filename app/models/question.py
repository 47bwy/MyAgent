# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/16 15:08:43
@Author  :   47bwy
@Desc    :   问题模型
'''

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    user_id = Column(String, ForeignKey("users.username"))
    
    # 定义与 User 的关系（可选，如果需要通过 question.user 访问用户信息）
    # user = relationship("User", back_populates="questions")
# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/16 15:05:57
@Author  :   47bwy
@Desc    :   None
'''

from pydantic import BaseModel


# 定义请求体模型
class QuestionRequest(BaseModel):
    question: str
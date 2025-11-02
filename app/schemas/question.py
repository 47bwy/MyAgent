# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/16 15:05:57
@Author  :   47bwy
@Desc    :   None
'''

from pydantic import BaseModel, Field


# 定义请求体模型
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="问题内容，1-2000个字符")
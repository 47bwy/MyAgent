# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:39:32
@Author  :   47bwy
@Desc    :   None
'''

import torch
from sqlalchemy.orm import Session
from transformers import BertForQuestionAnswering, BertTokenizer

from app.models import user
from app.core.config import settings
from app.core.db import SessionLocal

# 加载预训练的 BERT 模型和 Tokenizer
# model_name = "bert-base-chinese"
model_name = settings.local_model  # 从配置读取本地模型路径
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForQuestionAnswering.from_pretrained(model_name)

# 确保使用 GPU（如果可用）
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# 问答服务
def get_answer(question: str, context: str):
    # 将问题和上下文编码为模型可以接受的格式
    inputs = tokenizer(question, context, return_tensors="pt")
    
    # 使用模型进行推理
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 获取答案的位置
    start_scores, end_scores = outputs.start_logits, outputs.end_logits
    start_idx = torch.argmax(start_scores)
    end_idx = torch.argmax(end_scores)

    # 解码出答案文本
    answer_tokens = inputs.input_ids[0][start_idx:end_idx + 1]
    answer = tokenizer.decode(answer_tokens)
    return answer

# 提供问题答案
def process_question(question: str, user_id: str, db: Session = SessionLocal()):
    # 获取上下文信息（可以从数据库或固定文本中获取）
    context = " "  # 你可以替换为从数据库或文档中提取的上下文
    answer = get_answer(question, context)
    
    # 记录问题与回答到数据库（可选）
    question_record = user.Question(question=question, answer=answer, user_id=user_id)
    db.add(question_record)
    db.commit()

    return answer

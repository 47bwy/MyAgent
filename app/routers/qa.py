# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 15:15:31
@Author  :   47bwy
@Desc    :   /ask 接口。
'''

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.auth.auth import check_visitor_limit
from app.routers.auth import get_current_user
from worker.tasks import answer_question_task, celery_app

router = APIRouter()

# 设置 Jinja2 模板引擎
templates = Jinja2Templates(directory="app/templates")

# 问答接口（以后加上模型推理逻辑）
# @router.post("/ask")
# def ask_question(user_id: str = Depends(get_current_user)):
#     if not check_visitor_limit(user_id):
#         raise HTTPException(status_code=403, detail="Daily question limit reached")
#     return {"answer": "This will be the answer from the model."}


@router.post("/ask")
async def ask_question(
    question: str = Form(...),  # 使用 Form 来接收表单数据
    user: str = Depends(get_current_user)
):
    if user == "guest":
        # 访客用户，每天最多提问 3 次
        if not check_visitor_limit(user):
            raise HTTPException(status_code=403, detail="Daily question limit reached for guest user, please login for more access.")
    # 提交 celery 异步任务
    task = answer_question_task.delay(question, user)
    return {"task_id": task.id}


@router.get("/ask/result/{task_id}")
async def get_ask_result(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "SUCCESS":
        return {"status": "success", "answer": task.result}
    elif task.state == "FAILURE":
        return {"status": "failure", "error": str(task.info)}
    else:
        return {"status": task.state.lower()}
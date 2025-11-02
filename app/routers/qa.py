# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 15:15:31
@Author  :   47bwy
@Desc    :   /ask 接口。
'''

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.auth.auth import check_visitor_limit, get_current_user
from app.core.logger import get_logger
from app.schemas.question import QuestionRequest
from worker.tasks import answer_question_task, celery_app

logger = get_logger(__name__)

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
    question_data: QuestionRequest,  # 使用 Pydantic 模型，自动进行类型和格式校验
    user: str = Depends(get_current_user)
):
    """
    提交问题
    
    Pydantic 已自动校验：
    - question: 必须是字符串类型
    """
    logger.info(f"收到问题提交请求，用户: {user}, 问题: {question_data.question}")
    
    if user == "guest":
        # 访客用户，每天最多提问 3 次（业务逻辑校验）
        if not check_visitor_limit(user):
            logger.warning(f"访客用户 {user} 已达到每日提问限制")
            raise HTTPException(
                status_code=403, 
                detail="Daily question limit reached for guest user, please login for more access."
            )
    
    try:
        # 提交 celery 异步任务
        logger.info(f"提交 Celery 任务，问题: {question_data.question}, 用户: {user}")
        task = answer_question_task.delay(question_data.question, user)
        logger.info(f"任务已提交，task_id: {task.id}")
        return {"task_id": task.id}
    except Exception as e:
        logger.error(f"提交 Celery 任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")


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
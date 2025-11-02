# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:39:32
@Author  :   47bwy
@Desc    :   LLM 服务，使用 BERT 进行问答
'''

import os
from sqlalchemy.orm import Session

from app.models.question import Question
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)

# 禁用 CUDA 相关警告（如果系统没有 GPU）
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "")

# 延迟导入 torch，避免在导入时立即加载 CUDA
try:
    import torch
    from transformers import BertForQuestionAnswering, BertTokenizer
    TORCH_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import PyTorch: {e}")
    TORCH_AVAILABLE = False
except Exception as e:
    logger.warning(f"Error importing PyTorch (might be CUDA related): {e}")
    TORCH_AVAILABLE = False
    # 尝试设置环境变量强制使用 CPU
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    try:
        import torch
        from transformers import BertForQuestionAnswering, BertTokenizer
        TORCH_AVAILABLE = True
    except Exception:
        TORCH_AVAILABLE = False

# 全局变量，延迟加载模型
_tokenizer = None
_model = None
_device = None


def _get_device():
    """获取设备（CPU 或 CUDA），优先使用 CPU 避免 CUDA 错误"""
    global _device
    if _device is not None:
        return _device
    
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not available, model functions will fail")
        return None
    
    try:
        # 强制使用 CPU，避免 CUDA 库问题
        _device = "cpu"
        
        # 可选：尝试检测 CUDA（但即使检测失败也不报错）
        try:
            if torch.cuda.is_available():
                _device = "cuda"
                logger.info("CUDA is available, using GPU")
            else:
                logger.info("CUDA not available, using CPU")
        except Exception as e:
            logger.warning(f"Error checking CUDA availability: {e}, defaulting to CPU")
            _device = "cpu"
            
    except Exception as e:
        logger.error(f"Error initializing device: {e}")
        _device = "cpu"
    
    return _device


def _load_model():
    """延迟加载模型，避免在模块导入时出错"""
    global _tokenizer, _model, _device
    
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is not available. Please install torch and transformers.")
    
    if _model is not None and _tokenizer is not None:
        return _tokenizer, _model
    
    try:
        model_name = settings.local_model if settings.local_model else "bert-base-chinese"
        logger.info(f"Loading model from: {model_name}")
        
        # 加载 tokenizer 和模型
        _tokenizer = BertTokenizer.from_pretrained(model_name)
        _model = BertForQuestionAnswering.from_pretrained(model_name)
        
        # 获取设备并移动模型
        _device = _get_device()
        if _device:
            _model = _model.to(_device)
            logger.info(f"Model loaded successfully on {_device}")
        else:
            logger.warning("No device available, model may not work correctly")
            
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise
    
    return _tokenizer, _model

# 问答服务
def get_answer(question: str, context: str):
    """
    使用 BERT 模型回答问题
    
    Args:
        question: 问题文本
        context: 上下文文本
        
    Returns:
        答案文本
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is not available. Cannot generate answer.")
    
    try:
        # 延迟加载模型
        tokenizer, model = _load_model()
        device = _get_device()
        
        # 将问题和上下文编码为模型可以接受的格式
        inputs = tokenizer(question, context, return_tensors="pt")
        
        # 移动输入到正确的设备（inputs 是字典，需要转换为 Tensor）
        if device:
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 使用模型进行推理
        import torch
        with torch.no_grad():
            outputs = model(**inputs)
        
        # 获取答案的位置
        start_scores, end_scores = outputs.start_logits, outputs.end_logits
        
        # 找到开始和结束位置（获取第一个 batch 的结果）
        start_idx = torch.argmax(start_scores[0]).item()  # 转换为 Python int
        end_idx = torch.argmax(end_scores[0]).item()  # 转换为 Python int
        
        # 确保索引有效
        input_ids = inputs['input_ids'][0]  # 获取 input_ids tensor
        max_len = input_ids.shape[0]
        
        # 确保 end_idx >= start_idx 且都在有效范围内
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        
        start_idx = max(0, min(start_idx, max_len - 1))
        end_idx = max(start_idx, min(end_idx, max_len - 1))
        
        # 提取答案 token
        answer_tokens = input_ids[start_idx:end_idx + 1]
        
        # 解码答案
        answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
        
        # 如果答案为空，返回提示信息
        if not answer.strip():
            answer = "无法从给定的上下文中找到答案。"
        
        return answer
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise

# 提供问题答案
def process_question(question: str, user_id: str, db: Session = SessionLocal()):
    """
    处理问题并返回答案，同时保存到数据库
    
    Args:
        question: 问题文本
        user_id: 用户 ID
        db: 数据库会话
        
    Returns:
        答案文本
    """
    try:
        # 获取上下文信息（可以从数据库或固定文本中获取）
        context = " "  # 你可以替换为从数据库或文档中提取的上下文
        
        # 获取答案
        answer = get_answer(question, context)
        
        # 记录问题与回答到数据库（可选）
        try:
            question_record = Question(question=question, answer=answer, user_id=user_id)
            db.add(question_record)
            db.commit()
            logger.info(f"Question saved to database for user: {user_id}")
        except Exception as db_error:
            logger.warning(f"Failed to save question to database: {db_error}")
            # 即使数据库保存失败，也返回答案
        
        return answer
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise

# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 23:13:23
@Author  :   47bwy
@Desc    :   None
'''

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.core.config import settings

print(torch.cuda.is_available())

model_name = "THUDM/chatglm-6b"
model_name = "THU-KEG/ChatGLM-6B"
model_name = "gpt2"
model_name = "uer/gpt2-chinese-cluecorpussmall" # 中文GPT2模型
model_name = "bert-base-chinese"
save_dir = settings.local_model  # 从配置中读取本地模型路径
print(f"模型将下载到: {save_dir}")
# tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
# tokenizer.save_pretrained(save_dir)

# model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
# model.save_pretrained(save_dir)




tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained(save_dir)

model = AutoModelForCausalLM.from_pretrained(model_name)
model.save_pretrained(save_dir)

print("模型和tokenizer已成功下载到本地。")

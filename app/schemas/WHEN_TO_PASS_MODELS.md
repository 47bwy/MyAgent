# 何时将 Pydantic 模型作为函数参数传递

## ✅ 需要优化的场景

### 场景 1：创建对象时，所有字段都来自 Pydantic 模型

**优化前：**
```python
def create_user(db: Session, username: str, password: str, email: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password_hash=hashed_password, email=email)
    db.add(db_user)
    db.commit()
    return db_user

# 调用时需要传递多个参数
new_user = create_user(db=db, username=user_data.username, 
                       password=user_data.password, email=user_data.email)
```

**优化后：**
```python
def create_user(db: Session, user_data: UserCreate):
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(username=user_data.username, 
                   password_hash=hashed_password, 
                   email=user_data.email)
    db.add(db_user)
    db.commit()
    return db_user

# 调用时只需要传递模型
new_user = create_user(db=db, user_data=user_data)
```

**优势：**
- ✅ 添加新字段时，只需修改模型定义和函数内部，调用处无需修改
- ✅ 代码更简洁，参数更少
- ✅ 类型提示更好，IDE 支持更好
- ✅ 减少传递错误参数的风险

---

### 场景 2：更新对象时，所有字段都来自 Pydantic 模型

**示例：**
```python
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 更新所有字段
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
```

---

### 场景 3：复杂对象创建，需要多步骤处理

**示例：**
```python
def create_order(db: Session, order_data: OrderCreate):
    # 1. 验证库存
    # 2. 计算总价
    # 3. 创建订单记录
    # 4. 创建订单明细
    # 5. 更新库存
    
    # 如果字段很多，传递 model 可以避免参数列表过长
    pass
```

---

## ❌ 不需要优化的场景

### 场景 1：Pydantic 模型只有一个字段

**当前代码（QuestionRequest）：**
```python
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

def ask_question(question_data: QuestionRequest):
    # 只用一个字段，直接传递单个参数即可
    task = answer_question_task.delay(question_data.question)
```

**说明：** 只传递一个参数不会造成维护问题，优化价值不大。

---

### 场景 2：对象创建需要额外的业务逻辑字段

**示例（当前 process_question）：**
```python
def process_question(question: str, user_id: str, db: Session):
    # question 来自 Pydantic 模型
    # user_id 来自外部认证
    # answer 需要在函数内部生成
    
    answer = get_answer(question, context)
    question_record = Question(question=question, 
                               answer=answer,      # 业务逻辑字段
                               user_id=user_id)    # 外部字段
    db.add(question_record)
```

**说明：** `answer` 和 `user_id` 不是来自 Pydantic 模型，无法用单一模型表示。

---

### 场景 3：函数参数大部分来自外部，少量来自模型

**示例：**
```python
def create_comment(post_id: int, user_id: int, comment_data: CommentCreate):
    # post_id, user_id 来自 URL 路径参数
    # 只有 comment 字段来自模型
    
    comment = Comment(post_id=post_id, user_id=user_id, 
                      content=comment_data.content)
```

**说明：** 大部分参数来自外部，只有少数来自模型，分开传递更清晰。

---

### 场景 4：需要分别处理不同来源的数据

**示例：**
```python
def update_profile(user_id: int, profile_data: ProfileUpdate, 
                  avatar_file: UploadFile):
    # profile_data 用于更新数据库
    # avatar_file 用于保存文件
    
    # 分别处理更清晰
    if profile_data.bio:
        user.bio = profile_data.bio
    
    if avatar_file:
        avatar_path = save_avatar(avatar_file)
        user.avatar_url = avatar_path
```

---

## 📋 决策树

```
需要创建/更新数据库对象？
├─ 是 → 所有字段都来自 Pydantic 模型？
│   ├─ 是 → ✅ 传递整个模型
│   └─ 否 → ❌ 分别传递参数
└─ 否 → 需要传递多个字段（> 3个）？
    ├─ 是 → ✅ 考虑传递模型
    └─ 否 → ❌ 分别传递参数
```

---

## 🎯 总结

### 优先传递模型当：
1. **字段数量 ≥ 3** 且都来自同一模型
2. **需要频繁扩展字段** 的场景
3. **多个函数需要相同字段组合** 时
4. **字段之间有复杂关联**，需要整体验证

### 避免传递模型当：
1. **只有一个字段** 来自模型
2. **字段来自不同来源**（模型 + URL参数 + 文件等）
3. **需要单独处理某个字段** 的业务逻辑
4. **传递模型会增加理解成本** 时

---

## 🔧 实际应用

### 当前项目中的优化情况

| 场景 | 模型 | 是否需要优化 | 状态 |
|------|------|-------------|------|
| 用户注册 | `UserCreate` | ✅ 需要 | ✅ 已优化 |
| 用户登录 | `UserLogin` | ❌ 不需要 | - （仅用于验证，不创建对象）|
| 问题提交 | `QuestionRequest` | ❌ 不需要 | - （只有1个字段）|
| 数据库创建 | `process_question` | ❌ 不需要 | - （字段来自多个来源）|


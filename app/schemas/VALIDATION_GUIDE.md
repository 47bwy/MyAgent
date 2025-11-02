# Pydantic 参数校验说明

## 回答你的问题：**还需要做参数校验吗？**

### ✅ **不需要手动校验的部分**（Pydantic 自动处理）

1. **类型校验**：如果传入的是字符串而不是整数，会自动报错
2. **必填字段校验**：如果缺少必填字段，会自动报错
3. **格式校验**：如 `EmailStr` 会自动校验邮箱格式
4. **长度校验**：如 `min_length`、`max_length` 会自动校验
5. **自定义验证器**：如 `@field_validator`、`@model_validator` 中定义的校验规则

### ⚠️ **仍需手动校验的部分**（业务逻辑）

1. **数据库唯一性校验**：如检查用户名/邮箱是否已存在
2. **跨系统校验**：如调用外部 API 验证
3. **复杂业务规则**：如权限检查、业务状态检查

## 改进后的代码示例

### 使用 JSON 请求体（推荐）

```python
from app.schemas.user import UserCreate

@router.post("/register")
def register_user(
    user_data: UserCreate,  # 直接使用 Pydantic 模型，自动校验
    db: Session = Depends(db.get_db)
):
    # ✅ 以下校验已由 Pydantic 自动完成：
    # - username 长度 3-50 字符
    # - email 格式正确
    # - password 至少 8 个字符且包含数字和字母
    # - password 和 confirm_password 匹配
    
    # ⚠️ 仍需手动校验的业务逻辑：
    # 检查用户名是否已存在
    db_user = auth.get_user(db, username=user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 检查邮箱是否已存在（如果需要）
    # ...
    
    # 创建新用户
    new_user = auth.create_user(
        db=db, 
        username=user_data.username, 
        password=user_data.password, 
        email=user_data.email
    )
    
    return {"message": "User registered successfully", "username": new_user.username}
```

### 使用 Form 表单数据（当前代码的方式）

如果你必须使用 `Form`（如表单提交），可以这样结合使用：

```python
@router.post("/register")
def register_user(
    user_data: UserCreate = Depends(),  # 需要自定义转换，或
    # 或者继续使用 Form，但手动创建 Pydantic 模型进行校验：
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(db.get_db)
):
    # 手动创建模型实例以触发校验
    try:
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    # 后续业务逻辑同上
    ...
```

## 校验流程总结

```
请求到达
    ↓
Pydantic 自动校验（类型、格式、长度、自定义规则）
    ↓
如果失败 → 自动返回 422 错误（Validation Error）
    ↓
如果通过 → 进入路由函数
    ↓
手动业务逻辑校验（唯一性、权限等）
    ↓
处理请求
```

## 建议

1. **优先使用 JSON + Pydantic 模型**：更清晰、自动校验、自动文档生成
2. **将可以通用的校验规则放在 Pydantic 模型中**：如格式、长度、复杂验证逻辑
3. **将数据库相关的校验放在业务逻辑中**：如唯一性检查


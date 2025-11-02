# Pydantic 验证器调用时机详解

## 验证器调用流程

### 1. **`@field_validator` - 字段验证器**

**调用时机：** 在解析和验证**单个字段**时调用

**执行顺序：**
```
请求到达 FastAPI
    ↓
FastAPI 接收 JSON 请求体
    ↓
Pydantic 开始解析 UserCreate 模型
    ↓
解析 username 字段 → 调用 @field_validator('username')
    ↓
解析 password 字段 → 调用 @field_validator('password')
    ↓
解析 email 字段 → EmailStr 自动校验
    ↓
解析 confirm_password 字段
    ↓
所有字段解析完成
```

**示例：**
```python
@field_validator('username')
@classmethod
def validate_username(cls, v: str) -> str:
    # 当解析到 username 字段时，立即调用
    # v 是传入的原始值（字符串）
    return v  # 返回验证后的值
```

**特点：**
- 每个字段验证器独立执行
- 如果验证失败，抛出 `ValueError`，整个模型创建失败
- 返回的值会替换原始值（可以用于数据转换）

---

### 2. **`@model_validator(mode='after')` - 模型验证器**

**调用时机：** 在**所有字段都解析和验证完成后**调用

**执行顺序：**
```
所有字段验证通过
    ↓
创建模型实例（self 可用）
    ↓
调用 @model_validator(mode='after')
    ↓
可以访问所有字段：self.username, self.password 等
    ↓
验证通过 → 返回模型实例
    ↓
进入路由函数
```

**示例：**
```python
@model_validator(mode='after')
def validate_passwords_match(self) -> 'UserCreate':
    # 此时 self.password 和 self.confirm_password 都已解析完成
    # 可以比较两个字段的值
    if self.password != self.confirm_password:
        raise ValueError('密码和确认密码不匹配')
    return self
```

**特点：**
- 可以访问所有字段的值
- 用于需要跨字段比较的验证
- `mode='after'` 表示在所有字段验证后执行
- `mode='before'` 表示在字段验证前执行（可用于预处理）

---

### 3. **Field 约束（如 min_length, max_length）**

**调用时机：** 在字段验证器**之前**自动校验

**执行顺序：**
```
解析字段值
    ↓
Field 约束检查（min_length, max_length, EmailStr 等）
    ↓
如果通过 → 调用 @field_validator
    ↓
如果失败 → 直接抛出 ValidationError
```

---

## 完整执行示例

假设客户端发送：
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**执行流程：**

1. **Field 约束检查**
   - `username`: 检查长度 3-50 ✓
   - `email`: EmailStr 检查格式 ✓
   - `password`: 检查长度 >= 8 ✓

2. **字段验证器执行**
   - `validate_username("user123")` → 检查只包含字母数字下划线 ✓
   - `validate_password_strength("password123")` → 检查包含数字和字母 ✓

3. **模型验证器执行**
   - `validate_passwords_match()` → 检查两个密码是否匹配 ✓

4. **验证通过**
   - 创建 `UserCreate` 实例
   - 传递给路由函数 `register_user(user_data: UserCreate)`

---

## 验证失败的场景

如果客户端发送：
```json
{
  "username": "ab",  // 长度 < 3
  "email": "invalid-email",  // 格式错误
  "password": "123",  // 长度 < 8
  "confirm_password": "456"  // 不匹配
}
```

**失败顺序：**
1. `username` Field 约束失败（长度 < 3） → **立即返回 422 错误**
2. 不会继续验证其他字段（Pydantic 会收集所有错误一并返回）

或者如果长度通过但格式失败：
1. `username` Field 约束通过
2. `validate_username` 检查失败 → **返回 422 错误**

---

## 关键要点

1. **验证器在模型实例化时自动调用**：当 FastAPI 尝试将请求体转换为 `UserCreate` 实例时
2. **不在路由函数内调用**：验证发生在数据到达路由函数**之前**
3. **验证失败会返回 422**：不会进入路由函数，直接返回验证错误
4. **验证通过才会进入路由函数**：路由函数接收到的 `user_data` 已经是验证过的有效数据


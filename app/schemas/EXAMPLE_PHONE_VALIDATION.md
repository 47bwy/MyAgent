# Pydantic 手机号校验示例

## 方法 1：使用正则表达式（推荐，轻量级）

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserCreateWithPhone(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    phone: str = Field(..., description="手机号码")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """校验中国手机号码格式：11位数字，1开头"""
        # 中国手机号正则：1开头，第二位是3/4/5/6/7/8/9，共11位
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的中国手机号码（11位数字，1开头）')
        return v
```

**验证示例：**

- ✅ `13800138000` - 有效
- ✅ `15901234567` - 有效
- ❌ `12345678901` - 无效（第二位不是3-9）
- ❌ `1380013800` - 无效（只有10位）
- ❌ `18800138000a` - 无效（包含字母）

---

## 方法 2：使用 pydantic-extra-types（国际手机号支持）

需要先安装依赖：

```bash
pip install pydantic-extra-types phonenumbers
```

```python
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber

class UserCreateWithPhone(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    phone: PhoneNumber  # 自动验证和格式化

# 使用示例
user = UserCreateWithPhone(
    username="test",
    email="test@example.com",
    password="password123",
    confirm_password="password123",
    phone="+8613800138000"  # 中国手机号需要加国家代码
)
print(user.phone)  # 输出: +8613800138000
```

**优点：**

- 支持国际手机号验证
- 自动格式化
- 验证更严格

**缺点：**

- 需要额外依赖
- 中国手机号需要加 `+86` 前缀

---

## 方法 3：使用第三方库 phony-identifier

```bash
pip install phony-identifier
```

```python
from pydantic import BaseModel, field_validator
from phony_identifier import parse_phone_number

class UserCreateWithPhone(BaseModel):
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """使用 phony-identifier 验证"""
        try:
            parsed = parse_phone_number(v, default_country_code='CN')
            return parsed
        except ValueError:
            raise ValueError('无效的手机号码')
```

---

## 推荐方案

对于中国手机号验证，**推荐使用方法 1（正则表达式）**：

- 无需额外依赖
- 性能好
- 验证规则清晰
- 适合大多数场景

```python
@field_validator('phone')
@classmethod
def validate_phone(cls, v: str) -> str:
    """校验中国手机号码：11位数字，1开头，第二位3-9"""
    if not re.match(r'^1[3-9]\d{9}$', v):
        raise ValueError('请输入有效的中国手机号码')
    return v
```

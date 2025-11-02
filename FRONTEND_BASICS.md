# 📚 前端基础知识 - HTML/JavaScript 快速指南

## 🎯 简单回答你的问题

**是的！HTML 中的 `function` 就是 JavaScript！**

---

## 📖 HTML、CSS、JavaScript 的关系

一个网页通常由三部分组成：

### 1. **HTML** - 网页的骨架（结构）
```html
<div id="user-info">这里是内容</div>
<button id="login-btn">登录</button>
```
- 定义网页的**结构**和**内容**
- 标签、按钮、输入框等

### 2. **CSS** - 网页的样式（外观）
```css
.bg-blue-500 { background-color: blue; }
.text-white { color: white; }
```
- 控制网页的**外观**（颜色、大小、布局等）
- 你的项目使用了 Tailwind CSS

### 3. **JavaScript** - 网页的行为（交互）
```javascript
function showUserInfo() {
    // 这是 JavaScript 代码
}
```
- 控制网页的**行为**和**交互**
- 处理点击、提交表单、调用 API 等

---

## 🔍 你的项目中的代码解析

### HTML 部分（结构）
```html
<form id="qa-form">
    <input type="text" name="question" id="question">
    <button type="submit">提交问题</button>
</form>
```
**作用**：创建一个表单，包含输入框和提交按钮

---

### JavaScript 部分（在 `<script>` 标签中）
```javascript
<script>
// 这是一个 JavaScript 函数
async function showUserInfo() {
    const token = localStorage.getItem('access_token');
    // ... 更多代码
}

// 这也是 JavaScript（匿名函数）
document.getElementById('qa-form').onsubmit = async function(e) {
    e.preventDefault();  // 阻止表单默认提交行为
    // ... 处理表单提交
};
</script>
```

**作用**：
- 监听表单提交事件
- 获取用户输入
- 发送请求到后端 API
- 更新页面显示结果

---

## 📝 JavaScript 基础语法

### 1. **变量声明**
```javascript
const token = localStorage.getItem('access_token');  // 常量，不会改变
let errorMsg = '提交失败';  // 变量，可以改变
```

### 2. **函数定义**
```javascript
// 方式 1：普通函数
function showUserInfo() {
    // 代码
}

// 方式 2：异步函数（用于 API 调用）
async function pollResult(task_id) {
    // 代码
}

// 方式 3：匿名函数（直接赋值）
document.getElementById('btn').onclick = function() {
    // 代码
};

// 方式 4：箭头函数（ES6 新语法）
const renderChat = () => {
    // 代码
};
```

### 3. **操作 DOM（HTML 元素）**
```javascript
// 获取元素
const element = document.getElementById('user-info');  // 通过 ID 获取

// 修改文本内容
element.innerText = '当前用户：访客';

// 修改 HTML 内容
element.innerHTML = '<div>新内容</div>';

// 添加/移除 CSS 类
element.classList.add('hidden');     // 添加类
element.classList.remove('hidden');  // 移除类
```

### 4. **事件处理**
```javascript
// 监听表单提交
document.getElementById('qa-form').onsubmit = async function(e) {
    e.preventDefault();  // 阻止默认行为（页面跳转）
    // 处理提交逻辑
};

// 监听按钮点击
document.getElementById('logout-btn').onclick = function() {
    localStorage.removeItem('access_token');
    window.location.href = '/auth/login';
};
```

### 5. **调用 API**
```javascript
// 使用 fetch 发送请求
const resp = await fetch('/auth/login', {
    method: 'POST',  // HTTP 方法
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(jsonData)  // 请求体（JSON 格式）
});

// 获取响应数据
const data = await resp.json();  // 解析 JSON
```

### 6. **存储数据**
```javascript
// 本地存储（localStorage）- 保存在浏览器中
localStorage.setItem('access_token', token);  // 保存
const token = localStorage.getItem('access_token');  // 读取
localStorage.removeItem('access_token');  // 删除
```

---

## 🎨 你项目中的代码解析

### `index.html` 中的 JavaScript

#### 1. **显示用户信息**
```javascript
async function showUserInfo() {
    // 从浏览器存储中获取 token
    const token = localStorage.getItem('access_token');
    
    if (token) {
        // 如果有 token，调用 API 验证用户
        const resp = await fetch('/auth/me', {
            headers: { 'Authorization': 'Bearer ' + token }
        });
        
        if (resp.ok) {
            const data = await resp.json();
            // 更新页面显示用户名
            userInfoDiv.innerText = `当前用户：${data.username}`;
        }
    }
}
```

#### 2. **处理表单提交**
```javascript
document.getElementById('qa-form').onsubmit = async function(e) {
    e.preventDefault();  // 阻止表单默认提交（避免页面刷新）
    
    // 获取输入框的值
    const question = form.question.value;
    
    // 发送 POST 请求到后端
    const resp = await fetch('/qa/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ question: question })
    });
    
    // 处理响应
    if (resp.ok) {
        const res = await resp.json();
        pollResult(res.task_id);  // 轮询任务结果
    }
};
```

#### 3. **轮询任务结果**
```javascript
async function pollResult(task_id) {
    // 每 1.5 秒检查一次任务状态
    let interval = setInterval(async () => {
        const resp = await fetch(`/qa/ask/result/${task_id}`);
        const data = await resp.json();
        
        if (data.status === "success") {
            // 任务完成，显示答案
            chatHistory.push({ role: 'bot', content: data.answer });
            renderChat();
            clearInterval(interval);  // 停止轮询
        }
    }, 1500);  // 1500 毫秒 = 1.5 秒
}
```

---

## 🔧 常见 JavaScript 操作

### 1. **数组操作**
```javascript
const chatHistory = [];

// 添加元素
chatHistory.push({ role: 'user', content: question });

// 遍历数组
chatHistory.forEach(item => {
    console.log(item);
});

// 数组方法链式调用
errorMsg = err.detail.map(e => e.msg).join('; ');
```

### 2. **条件判断**
```javascript
if (token) {
    // 有 token
} else {
    // 没有 token
}

// 三元运算符（简化写法）
const device = torch.cuda.is_available() ? "cuda" : "cpu";
```

### 3. **异步操作**
```javascript
// async/await（推荐）
async function fetchData() {
    const resp = await fetch('/api/data');
    const data = await resp.json();
    return data;
}

// Promise（传统方式）
fetch('/api/data')
    .then(resp => resp.json())
    .then(data => console.log(data));
```

---

## 🚀 如何调试前端代码

### 1. **浏览器开发者工具**
- 按 `F12` 打开
- **Console（控制台）**：查看错误和日志
- **Network（网络）**：查看 API 请求
- **Elements（元素）**：查看和修改 HTML/CSS

### 2. **添加日志**
```javascript
console.log('这是日志信息');
console.error('这是错误信息');
console.warn('这是警告信息');

// 查看变量值
console.log('token:', token);
console.log('响应数据:', data);
```

### 3. **断点调试**
在浏览器开发者工具的 **Sources（源代码）** 标签中：
- 点击行号添加断点
- 刷新页面
- 代码会在断点处暂停
- 可以查看变量值，单步执行

---

## 📚 快速参考

| JavaScript 概念 | 你的代码中的例子 |
|----------------|----------------|
| **变量** | `const token = ...` |
| **函数** | `async function showUserInfo()` |
| **对象** | `{ question: question }` |
| **数组** | `chatHistory = []` |
| **条件** | `if (resp.ok) { ... }` |
| **循环** | `chatHistory.forEach(...)` |
| **异步** | `await fetch(...)` |
| **DOM 操作** | `document.getElementById(...)` |
| **事件** | `.onsubmit = function(...)` |

---

## 💡 总结

1. **`<script>` 标签内的所有代码都是 JavaScript**
2. **`function` 关键字用于定义函数（可以重用的代码块）**
3. **JavaScript 负责网页的交互逻辑**（点击、提交、API 调用等）
4. **HTML 提供结构，CSS 提供样式，JavaScript 提供行为**

---

## 🔗 学习资源

- [MDN JavaScript 教程](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Guide)
- [JavaScript.info](https://zh.javascript.info/) - 非常详细的 JS 教程
- [现代 JavaScript 教程](https://zh.javascript.info/) - 中文版

---

## ❓ 常见问题

**Q: HTML 中可以写多少 JavaScript？**  
A: 理论上没有限制，但建议将复杂的代码放到单独的 `.js` 文件中。

**Q: JavaScript 和 Python 有什么区别？**  
A: 
- JavaScript 在浏览器中运行（前端）
- Python 在服务器上运行（后端）
- 语法类似但有一些差异

**Q: 可以不写 JavaScript 吗？**  
A: 可以，但网页就会是静态的，无法交互。你的项目需要 JS 来：
- 调用后端 API
- 处理用户操作
- 动态更新页面内容


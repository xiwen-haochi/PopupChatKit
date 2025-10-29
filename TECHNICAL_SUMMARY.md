# 📖 PopupChatKit 技术总结

> 技术架构、核心功能与 API 文档

---

## 🎯 项目概述

PopupChatKit 是一个基于 FastAPI + pydantic-ai 的双模式 AI 对话系统，包含：
1. **独立 Web 应用** - 完整的对话界面
2. **嵌入式插件** - 轻量级 JS 插件（约700行代码）

核心价值：零依赖、易集成、高性能、功能强大

---

## 🏗️ 技术架构

### 后端架构

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌─────────────────────────────────┐   │
│  │   main.py (681行)              │   │
│  │  - 路由管理                     │   │
│  │  - CORS 配置                    │   │
│  │  - 静态文件服务                 │   │
│  │  - 生命周期管理                 │   │
│  └─────────────────────────────────┘   │
│                │                         │
│  ┌─────────────▼─────────────────┐     │
│  │   agents.py                   │     │
│  │  - pydantic-ai Agent 配置     │     │
│  │  - 智谱 AI 模型集成            │     │
│  │  - 流式响应处理                │     │
│  └─────────────┬─────────────────┘     │
│                │                         │
│  ┌─────────────▼─────────────────┐     │
│  │   database.py                 │     │
│  │  - SQLite 异步操作            │     │
│  │  - 会话管理                    │     │
│  │  - 消息存储                    │     │
│  └───────────────────────────────┘     │
└─────────────────────────────────────────┘
```

### 前端架构

#### 独立模式（Standalone）
```
chat.html (1388行)
├── UI 组件
│   ├── 会话列表
│   ├── 消息展示区
│   ├── 输入控制区
│   └── 设置面板
├── 核心功能
│   ├── 流式对话
│   ├── AI 绘图
│   ├── 图片上传识别
│   └── 历史记录管理
└── 技术实现
    ├── Fetch API
    ├── ReadableStream
    ├── DOM 操作
    └── LocalStorage
```

#### 嵌入模式（Embedded）
```
popup.js (约700行) - IIFE 模式
├── 核心模块
│   ├── 悬浮按钮
│   ├── 聊天窗口
│   ├── 消息管理
│   └── 流式响应
├── 智能功能
│   ├── 网页总结
│   ├── 智能搜索
│   ├── 文本解释
│   └── 复制HTML
└── 交互优化
    ├── 选中文本气泡
    ├── 悬停动画
    ├── 自动发送
    └── 响应式布局
```

---

## 💡 技术亮点

### 1. 流式响应实现

**后端（FastAPI）**：
```python
async def stream_response():
    async with agent.run_stream(message) as result:
        async for chunk in result.stream_text():
            yield json.dumps({
                'type': 'content',
                'content': chunk
            }) + '\n'
```

**前端（JavaScript）**：
```javascript
const response = await fetch(url, options);
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value, { stream: true });
    // 处理流式数据
}
```

### 2. 零依赖设计

**IIFE 模式避免全局污染**：
```javascript
(function(window) {
    'use strict';
    
    const PopupChatKit = {
        init: function(options) { /* ... */ },
        sendMessage: async function() { /* ... */ }
    };
    
    window.PopupChatKit = PopupChatKit;
})(window);
```

### 3. 智能意图识别

```javascript
// 按优先级检测用户意图
if (shouldExplainSelection(message) && selectedText) {
    // 1. 解释选中文本（最高优先级）
} else if (shouldSearchPage(message)) {
    // 2. 搜索页面内容
} else if (shouldSummarizePage(message)) {
    // 3. 总结网页
} else if (shouldCopyPageHTML(message)) {
    // 4. 复制HTML
}
```

### 4. Prompt 工程

**选中文本解释 Prompt**：
```
你是一个专业的解释助手。请用简洁易懂的语言解释用户选中的文本。

输出格式：
📖 解释：
- 基本含义：[简明解释]
- 在本文中：[结合上下文的理解]
- 翻译：[如果是外语]

注意：简洁明了，避免过度扩展。
```

**智能搜索 Prompt**：
```
你是一个智能搜索助手。请从网页内容中找到用户需要的信息。

输出格式：
🔍 搜索结果：

✅ 找到相关内容：
"[引用原文相关段落]"

💡 解答：
[基于找到的内容回答用户问题]

📍 位置提示：
[告诉用户这部分内容的大致位置]

注意：必须引用原文，如果没找到明确告知用户。
```

### 5. 会话上下文管理

**双表存储策略**：
- `messages` 表 - pydantic-ai 格式，用于 AI 上下文
- `chat_messages` 表 - 格式化消息，用于前端显示

```python
# AI 上下文消息
await db.add_message(session_id, role, content, model_request_part)

# 前端显示消息
await db.add_chat_message(session_id, role, formatted_content)
```

### 6. 图片处理流程

```python
# 1. 接收上传
image = await file.read()

# 2. Base64 编码
base64_image = base64.b64encode(image).decode('utf-8')

# 3. 调用视觉模型
response = await httpx.post(
    url='https://open.bigmodel.cn/api/paas/v4/chat/completions',
    json={
        'model': 'glm-4v-flash',
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': prompt},
                {'type': 'image_url', 'image_url': {
                    'url': f'data:image/jpeg;base64,{base64_image}'
                }}
            ]
        }]
    }
)

# 4. 保存到数据库
await db.add_chat_message(session_id, 'user', f'📷 [图片] {prompt}')
```

---

## 🔌 API 文档

### 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`
- **CORS**: 已启用，支持所有来源

### 端点列表

#### 1. 创建会话

**请求**：
```http
POST /api/sessions
Content-Type: application/json

{
  "title": "新对话",
  "mode": "embedded"  // 可选：standalone | embedded
}
```

**响应**：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "新对话",
  "created_at": "2025-10-28T10:30:00Z"
}
```

#### 2. 获取会话列表

**请求**：
```http
GET /api/sessions
```

**响应**：
```json
[
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "新对话",
    "created_at": "2025-10-28T10:30:00Z",
    "last_message_at": "2025-10-28T10:35:00Z"
  }
]
```

#### 3. 流式对话（核心接口）

**请求**：
```http
POST /api/chat/stream
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "你好，请介绍一下自己",
  "stream": true
}
```

**响应**（Server-Sent Events）：
```json
{"type": "content", "content": "你"}
{"type": "content", "content": "好"}
{"type": "content", "content": "！"}
{"type": "content", "content": "我"}
{"type": "content", "content": "是"}
...
{"type": "done", "message_id": "msg_123"}
```

#### 4. 生成图片

**请求**：
```http
POST /api/image/generate
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "prompt": "一只可爱的小猫在花园里玩耍",
  "size": "1024x1024"  // 可选：768x768 | 1024x1024 | 1280x1280
}
```

**响应**：
```json
{
  "image_url": "https://img.alicdn.com/imgextra/...",
  "prompt": "一只可爱的小猫在花园里玩耍",
  "created_at": "2025-10-28T10:40:00Z"
}
```

#### 5. 分析图片

**请求**：
```http
POST /api/image/analyze
Content-Type: multipart/form-data

session_id: 550e8400-e29b-41d4-a716-446655440000
prompt: 这张图片里有什么？
image: [binary file]
```

**响应**：
```json
{
  "analysis": "这张图片显示了一只橘色的小猫正在花园里玩耍...",
  "created_at": "2025-10-28T10:45:00Z"
}
```

#### 6. 获取历史记录

**请求**：
```http
GET /api/chat/history/{session_id}
```

**响应**：
```json
[
  {
    "role": "user",
    "content": "你好",
    "timestamp": "2025-10-28T10:30:00Z"
  },
  {
    "role": "assistant",
    "content": "你好！我是 AI 助手...",
    "timestamp": "2025-10-28T10:30:05Z"
  }
]
```

#### 7. 删除会话

**请求**：
```http
DELETE /api/sessions/{session_id}
```

**响应**：
```json
{
  "message": "Session deleted successfully"
}
```

#### 8. 更新会话标题

**请求**：
```http
PUT /api/sessions/{session_id}
Content-Type: application/json

{
  "title": "新的会话标题"
}
```

**响应**：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "新的会话标题",
  "updated_at": "2025-10-28T10:50:00Z"
}
```

---

## 📊 数据库设计

### messages 表（AI 上下文）
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- user | assistant | system
    content TEXT NOT NULL,
    model_request_part TEXT,         -- pydantic-ai 格式的原始数据
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### chat_messages 表（前端显示）
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- user | assistant
    content TEXT NOT NULL,           -- 格式化后的内容（支持 Markdown、图片等）
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### sessions 表（会话管理）
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_message_at DATETIME
);
```

---

## 🎨 前端关键功能实现

### 1. 选中文本气泡

```javascript
// 监听文本选中
document.addEventListener('mouseup', () => {
    const text = window.getSelection().toString().trim();
    if (text && text.length > 0 && text.length < 500) {
        selectedText = text;
        showSelectionHint();  // 显示可点击气泡
    }
});

// 点击气泡自动解释
hint.onclick = () => {
    if (!isOpen) open();  // 打开聊天窗口
    input.value = '解释这段文字';
    sendMessage();  // 自动发送
};
```

### 2. 网页内容提取

```javascript
extractPageContent: function() {
    const title = document.title;
    const bodyText = document.body.innerText;
    
    // 清理文本
    const cleanText = bodyText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .join('\n');
    
    // 限制长度（3000字符）
    const content = cleanText.length > 3000 
        ? cleanText.substring(0, 3000) + '...' 
        : cleanText;
    
    return { title, content, url: window.location.href };
}
```

### 3. 复制网页 HTML

```javascript
copyPageHTML: async function() {
    const html = document.documentElement.outerHTML;
    await navigator.clipboard.writeText(html);
    
    addMessage('assistant', `✅ 网页 HTML 已复制到剪贴板！
    
📊 统计信息：
- 总字符数：${html.length.toLocaleString()}
- 页面标题：${document.title}
- URL：${window.location.href}`);
}
```

---

## 🔒 安全性考虑

1. **API Key 保护**
   - 存储在 `.env` 文件中
   - 不暴露到前端
   - 添加到 `.gitignore`

2. **CORS 配置**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],      # 生产环境应限制具体域名
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **输入验证**
   - 使用 Pydantic 模型验证请求数据
   - 限制文件上传大小（10MB）
   - 限制选中文本长度（500字符）

4. **SQL 注入防护**
   - 使用参数化查询
   - SQLite 异步操作
   - 自动转义特殊字符

---

## 🚀 性能优化

1. **流式响应**
   - 减少首字节时间（TTFB）
   - 提升用户体验
   - 降低内存占用

2. **异步处理**
   - 所有 I/O 操作使用 async/await
   - 数据库操作异步化
   - HTTP 请求异步化

3. **资源优化**
   - JavaScript 代码精简（约700行）
   - 无第三方依赖
   - CSS 按需加载

4. **缓存策略**
   - 会话数据本地缓存
   - 历史记录按需加载
   - 静态文件浏览器缓存

---

## 📈 扩展性设计

### 1. 多模型支持

当前支持智谱 AI，可轻松扩展其他模型：

```python
# agents.py
def get_agent(model: str = 'glm-4-flashx'):
    if model.startswith('glm-'):
        return Agent('openai:' + model, deps_type=Deps)
    elif model.startswith('gpt-'):
        # 扩展 OpenAI
        pass
    elif model.startswith('claude-'):
        # 扩展 Anthropic
        pass
```

### 2. 插件系统

嵌入模式支持自定义功能：

```javascript
PopupChatKit.registerPlugin({
    name: 'custom-feature',
    trigger: (message) => message.includes('关键词'),
    handler: async function(message) {
        // 自定义处理逻辑
    }
});
```

### 3. 主题系统

支持自定义主题：

```javascript
PopupChatKit.init({
    theme: {
        primaryColor: '#6366f1',
        backgroundColor: '#ffffff',
        textColor: '#333333',
        borderRadius: '12px'
    }
});
```

---

## 🐛 常见问题

### 1. CORS 错误

**问题**：前端无法访问 API

**解决**：
- 检查后端 CORS 配置
- 确保 `allow_origins` 包含前端域名
- 开发环境可设置为 `["*"]`

### 2. 流式响应中断

**问题**：对话中途停止

**解决**：
- 检查网络连接
- 增加超时时间
- 查看浏览器控制台错误

### 3. 数据库锁定

**问题**：SQLite database is locked

**解决**：
- 使用异步数据库操作
- 避免长事务
- 增加重试逻辑

---

## 📝 开发建议

1. **代码规范**
   - 使用 ESLint/Prettier 格式化
   - 遵循 PEP 8 规范（Python）
   - 添加详细注释

2. **测试覆盖**
   - 单元测试（pytest）
   - 集成测试
   - 端到端测试

3. **日志记录**
   - 记录关键操作
   - 错误追踪
   - 性能监控

4. **版本控制**
   - 语义化版本号
   - 详细的 commit 信息
   - 使用 Git Flow

---

## 📚 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [pydantic-ai 文档](https://ai.pydantic.dev/)
- [智谱AI API 文档](https://open.bigmodel.cn/dev/api)
- [MDN Web Docs](https://developer.mozilla.org/)

---


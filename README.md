# 🚀 PopupChatKit

> 双模式 AI 对话系统 - 既是独立 Web 应用,也是轻量级嵌入插件

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![pydantic-ai](https://img.shields.io/badge/pydantic--ai-latest-orange.svg)](https://ai.pydantic.dev/)

---

## ✨ 特性

### 🌐 独立模式
- **💬 智能对话**: 支持智谱 AI 和通义千问多种模型
- **🎨 AI 绘画**: 文本生成图片,创意无限
- **📚 历史管理**: 完整的对话历史记录和会话管理
- **⚙️ 灵活配置**: 自定义 API Key、模型选择、主题等

### 🔌 嵌入模式
- **🪶 轻量集成**: 单个 JS 文件即可集成到任何网站
- **🎯 浮动弹窗**: 右侧悬浮按钮,不影响原网站布局
- **📄 网页分析**: 智能总结当前页面内容
- **📷 截图识别**: 截取页面内容让 AI 分析
- **📊 结构化输出**: 将网页内容转换为 JSON 格式

### 🛠️ 技术特性
- **⚡ 流式响应**: 打字机效果,实时展示 AI 回复
- **📝 Markdown 支持**: 富文本渲染,代码高亮
- **🔒 数据安全**: API Key 加密存储,HTTPS 传输
- **💾 本地存储**: SQLite 数据库,数据完全可控
- **🎨 响应式设计**: 完美适配桌面和移动端

---

## 📋 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [安装部署](#安装部署)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [开发文档](#开发文档)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🚀 快速开始

### 前置要求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) 包管理工具
- 智谱 AI 或通义千问 API Key

### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/your-username/PopupChatKit.git
cd PopupChatKit

# 2. 进入后端目录
cd backend

# 3. 安装依赖
uv sync

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件,填入你的 API Keys

# 5. 启动服务
uv run python -m main

# 6. 访问应用
# 打开浏览器访问 http://localhost:8000
```

---

## 📁 项目结构

```
PopupChatKit/
├── 📄 README.md                    # 项目说明文档
├── 📄 LICENSE                      # 开源协议
├── 📁 backend/                     # 后端代码
│   ├── 📄 main.py                 # FastAPI 主应用
│   ├── 📄 database.py             # 数据库操作
│   ├── 📄 agents.py               # AI Agent 配置
│   ├── 📄 models.py               # Pydantic 模型
│   ├── 📄 init_db.sql             # 数据库初始化 SQL
│   ├── 📄 pyproject.toml          # 项目依赖配置
│   ├── 📄 .env.example            # 环境变量示例
│   ├── 📁 routers/                # API 路由
│   │   ├── chat.py               # 对话相关 API
│   │   ├── history.py            # 历史记录 API
│   │   ├── draw.py               # 绘画相关 API
│   │   ├── web.py                # 网页分析 API
│   │   └── config.py             # 配置管理 API
│   └── 📁 utils/                  # 工具函数
│       ├── web_extractor.py      # 网页内容提取
│       └── image_handler.py      # 图片处理
│
├── 📁 frontend/                    # 前端代码
│   ├── 📁 standalone/             # 独立模式
│   │   ├── index.html            # 首页/配置页
│   │   ├── chat.html             # 对话页面
│   │   ├── history.html          # 历史记录页
│   │   ├── draw.html             # 绘画页面
│   │   ├── settings.html         # 设置页面
│   │   ├── about.html            # 关于页面
│   │   ├── 📁 css/               # 样式文件
│   │   └── 📁 js/                # JavaScript 文件
│   │
│   ├── 📁 embedded/               # 嵌入模式
│   │   ├── popup.js              # 嵌入脚本 (核心)
│   │   ├── popup.css             # 弹窗样式
│   │   └── demo.html             # 演示页面
│   │
│   └── 📁 lib/                    # 第三方库
│
├── 📁 ai-chat-ui/                 # UI 原型和文档
│   ├── 📄 功能点梳理.md
│   ├── 📄 开发文档.md
│   └── 📄 index.html             # UI 原型展示
│
├── 📁 data/                       # 数据文件
│   └── chat.db                   # SQLite 数据库
│
└── 📁 tests/                      # 测试文件
    ├── test_api.py
    ├── test_database.py
    └── test_agents.py
```

---

## 🔧 安装部署

### 开发环境

1. **安装依赖**
```bash
cd backend
uv sync --dev
```

2. **配置环境变量**
```bash
# 创建 .env 文件
cat > .env << EOF
# AI 模型配置
ZHIPU_API_KEY=your_zhipu_api_key_here
QWEN_API_KEY=your_qwen_api_key_here

# 数据库配置
DB_PATH=../data/chat.db

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)
EOF
```

3. **启动开发服务器**
```bash
uv run python -m main
# 或使用热重载
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境

```bash
# 安装生产依赖
uv sync --no-dev

# 使用 Uvicorn 启动
uv run uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

---

## 📖 使用指南

### 独立模式

1. **配置 API Key**
   - 访问首页 `http://localhost:8000`
   - 输入智谱 AI 或通义千问的 API Key
   - 点击"保存配置"

2. **开始对话**
   - 进入对话页面
   - 在输入框输入消息
   - AI 将以流式方式实时回复

3. **查看历史**
   - 点击"历史记录"菜单
   - 浏览所有对话会话
   - 搜索和筛选特定会话

4. **AI 绘画**
   - 进入绘画页面
   - 输入图片描述
   - 设置生成参数
   - 点击"生成"按钮

### 嵌入模式

1. **集成到网站**

在目标网站的 HTML 中添加:

```html
<!-- 引入 PopupChatKit -->
<script src="https://your-domain.com/popup.js"></script>

<!-- 初始化配置 -->
<script>
  PopupChat.init({
    // 必填: API Key
    apiKey: 'your-api-key',
    
    // 可选配置
    model: 'zhipu',           // 'zhipu' | 'qwen'
    position: 'right',        // 'right' | 'left'
    theme: 'light',           // 'light' | 'dark'
    language: 'zh-CN',        // 'zh-CN' | 'en-US'
    
    // 功能开关
    enableWebSummary: true,   // 启用网页总结
    enableScreenshot: true,   // 启用截图分析
    enableJsonExport: true,   // 启用 JSON 导出
  });
</script>
```

2. **使用弹窗**
   - 点击右下角浮动按钮展开对话窗口
   - 点击"📄"按钮总结当前网页
   - 点击"📷"按钮截图分析
   - 输入消息与 AI 对话

3. **程序化调用**

```javascript
// 打开弹窗
PopupChat.open();

// 关闭弹窗
PopupChat.close();

// 发送消息
PopupChat.sendMessage('你好!');

// 总结当前页面
PopupChat.summarizePage();

// 监听事件
PopupChat.on('message', (data) => {
  console.log('收到消息:', data);
});
```

---

## 🔌 API 文档

### 基础 URL

```
http://localhost:8000/api
```

### 认证

大多数 API 不需要认证。API Key 在客户端配置,后端根据配置调用相应模型。

### 端点列表

#### 1. 对话相关

**流式对话**
```http
POST /api/chat/stream
Content-Type: application/json

{
  "session_id": "uuid-string",
  "message": "用户消息",
  "model": "zhipu",
  "stream": true
}
```

**获取历史消息**
```http
GET /api/chat/history/{session_id}
```

#### 2. 会话管理

**获取会话列表**
```http
GET /api/sessions?limit=50
```

**创建会话**
```http
POST /api/sessions
Content-Type: application/json

{
  "title": "会话标题",
  "mode": "standalone"
}
```

**删除会话**
```http
DELETE /api/sessions/{session_id}
```

#### 3. 网页分析

**提取网页内容**
```http
POST /api/web/extract
Content-Type: application/json

{
  "url": "https://example.com",
  "mode": "text"
}
```

**总结网页**
```http
POST /api/web/summarize
Content-Type: application/json

{
  "content": "网页内容...",
  "url": "https://example.com"
}
```

#### 4. 图片分析

**上传并分析图片**
```http
POST /api/image/analyze
Content-Type: multipart/form-data

image: <file>
prompt: "分析这张图片"
```

#### 5. AI 绘画

**生成图片**
```http
POST /api/draw
Content-Type: application/json

{
  "prompt": "一只可爱的猫咪",
  "model": "zhipu-cogview",
  "size": "1024x1024"
}
```

详细 API 文档请访问: `http://localhost:8000/docs`

---

## 🧑‍💻 开发文档

### 技术栈

**前端**
- HTML5 + CSS3
- Vanilla JavaScript (ES6+)
- Markdown-it (Markdown 渲染)
- highlight.js (代码高亮)

**后端**
- Python 3.10+
- FastAPI (Web 框架)
- pydantic-ai (LLM 接口)
- SQLite (数据库)
- uvicorn (ASGI 服务器)
- uv (包管理)

**AI 模型**
- 智谱 AI (GLM-4)
- 通义千问 (Qwen)

### 开发指南

详细开发文档请查看: [ai-chat-ui/开发文档.md](./ai-chat-ui/开发文档.md)

包含:
- 架构设计
- 数据库设计
- API 设计
- 前端组件开发
- 后端模块开发
- 测试策略
- 部署指南

### 运行测试

```bash
# 安装测试依赖
uv sync --dev

# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_api.py

# 查看覆盖率
uv run pytest --cov=backend --cov-report=html
```

### 代码质量

```bash
# 代码格式化
uv run black backend/

# 代码检查
uv run ruff check backend/

# 类型检查
uv run mypy backend/
```

---

## ❓ 常见问题

### Q1: 如何获取 API Key?

**智谱 AI:**
1. 访问 [智谱开放平台](https://open.bigmodel.cn/)
2. 注册并登录
3. 在控制台创建 API Key

**通义千问:**
1. 访问 [阿里云百炼平台](https://dashscope.aliyun.com/)
2. 开通服务
3. 获取 API Key

### Q2: 数据存储在哪里?

所有数据存储在本地 SQLite 数据库 (`data/chat.db`)。你可以:
- 直接备份此文件
- 使用 API 导出为 JSON
- 通过 SQLite 工具查看和管理

### Q3: 嵌入模式会影响原网站吗?

不会。嵌入模式使用以下技术确保隔离:
- Shadow DOM 隔离样式
- 独立的 JavaScript 作用域
- 固定定位的浮动按钮
- 最小化的 DOM 操作

### Q4: 支持哪些浏览器?

支持所有现代浏览器:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Q5: 可以自部署吗?

可以。项目完全开源,支持:
- 本地运行
- Docker 部署
- 云服务器部署
- 内网部署

### Q6: API Key 安全吗?

安全措施:
- 后端存储时加密
- 传输使用 HTTPS
- 不会上传到第三方
- 支持环境变量配置

---

## 🤝 贡献指南

欢迎贡献! 请遵循以下步骤:

1. **Fork 项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 贡献类型

- 🐛 Bug 修复
- ✨ 新功能
- 📝 文档改进
- 🎨 UI/UX 优化
- ⚡ 性能优化
- ✅ 测试覆盖

### 代码规范

- Python: 遵循 PEP 8,使用 Black 格式化
- JavaScript: 遵循 ES6+ 标准
- 提交信息: 使用 [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

```
MIT License

Copyright (c) 2025 PopupChatKit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [pydantic-ai](https://ai.pydantic.dev/) - 类型安全的 AI 框架
- [智谱 AI](https://open.bigmodel.cn/) - GLM 系列模型
- [通义千问](https://tongyi.aliyun.com/) - 阿里云大模型
- [uv](https://github.com/astral-sh/uv) - 极速 Python 包管理器

---

## 📮 联系方式

- **项目主页**: [GitHub](https://github.com/your-username/PopupChatKit)
- **问题反馈**: [Issues](https://github.com/your-username/PopupChatKit/issues)
- **讨论交流**: [Discussions](https://github.com/your-username/PopupChatKit/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助,请给个 Star! ⭐**

Made with ❤️ by Colin

</div>

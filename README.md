# 🚀 PopupChatKit
> 一个轻量级、零依赖的 AI 聊天插件 - 让任何网站瞬间拥有智能对话能力
---

## ✨ 核心特性

### 🎯 双模式设计

#### 🌐 独立模式（Standalone）
完整的 Web 应用，提供全功能 AI 对话体验：
- 💬 **智能对话** - 基于智谱 AI 的流式对话
- 🎨 **AI 绘图** - CogView-4 文本生成图片
- 📷 **图片识别** - glm-4v-flash 视觉分析
- 📚 **会话管理** - 完整的历史记录和多会话支持

#### 🔌 嵌入模式（Embedded）
轻量级插件，一行代码集成到任何网站：
- 📄 **网页总结** - 自动提取并总结当前页面内容
- 🔍 **智能搜索** - 在页面中快速查找信息
- 📝 **文本解释** - 选中文字点击气泡即可解释
- 📋 **复制HTML** - 一键复制完整网页代码

### 🛠️ 技术亮点
- ⚡ **零依赖** - 纯原生 JavaScript，无需任何第三方库
- 🎯 **流式响应** - 打字机效果，实时展示 AI 回复
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔒 **数据安全** - SQLite 本地存储，数据完全可控
- 🎨 **高度可定制** - 丰富的配置选项

---

## 📦 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/PopupChatKit.git
cd PopupChatKit
```

### 2. 配置环境

创建 `.env` 文件（或复制 `.env.example`）：

```bash
# 智谱 AI API Key（必填）
ZHIPU_API_KEY=your_api_key_here

# 服务器配置（可选）
HOST=0.0.0.0
PORT=8000
```

获取 API Key：访问 [智谱AI开放平台](https://open.bigmodel.cn/)

### 3. 安装依赖

使用 uv（推荐）：

```bash
cd backend
uv sync
```


### 4. 启动服务

```bash
# 使用 uv
uv run uvicorn main:app

### 5. 访问应用

- **独立模式**: http://localhost:8000
- **嵌入模式**: 打开 `frontend/embedded/demo.html`
- **API 文档**: http://localhost:8000/docs

---

## 🎯 使用方式

### 独立模式 - 完整 Web 应用

直接访问 http://localhost:8000 即可使用完整功能：

1. **对话模式** - 与 AI 自由对话
2. **绘图模式** - 输入描述生成图片
3. **上传图片** - AI 识别并分析图片内容
4. **历史记录** - 查看和管理所有会话

### 嵌入模式 - 插件集成

在任何 HTML 页面中添加以下代码：

```html
<!-- 引入插件 -->
<script src="popup.js"></script>

<!-- 初始化 -->
<script>
  PopupChatKit.init({
    apiBase: 'http://localhost:8000/api'
  });
</script>
```

就这么简单！现在你的网站右下角会出现一个聊天按钮。

**高级配置**：

```javascript
PopupChatKit.init({
  apiBase: 'http://localhost:8000/api',
  position: 'bottom-right',      // 位置: bottom-right | bottom-left | top-right | top-left
  buttonColor: '#6366f1',        // 按钮颜色
  buttonSize: 60,                // 按钮大小
  maxWidth: 400,                 // 窗口最大宽度
  maxHeight: 600,                // 窗口最大高度
  zIndex: 9999                   // 层级
});
```

---

## 📁 项目结构

```
PopupChatKit/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI 主应用
│   ├── agents.py              # AI Agent 配置
│   ├── database.py            # 数据库操作
│   ├── pyproject.toml         # Python 依赖
│   └── .env                   # 环境变量配置
├── frontend/                   # 前端文件
│   ├── standalone/            # 独立模式
│   │   └── chat.html         # 完整 Web 应用
│   └── embedded/              # 嵌入模式
│       ├── popup.js          # 核心插件（约700行）
│       ├── demo.html         # 完整演示页面
│       ├── simple.html       # 简单示例
│       └── README.md         # 使用文档
├── 演示/                       # 演示文件夹
│   ├── vue-demo.html         # Vue3 集成示例
│   └── README.md
├── data/                       # 数据目录
│   └── chat.db               # SQLite 数据库
├── README.md                  # 项目说明（本文件）
└── TECHNICAL_SUMMARY.md       # 技术总结文档
```

---

## 🎮 功能演示

### 1. 网页总结

在嵌入模式下，用户可以输入：
- "总结这个网页"
- "概括页面内容"
- "这个页面讲了什么？"

AI 会自动提取当前页面的标题、URL 和文本内容，进行智能总结。

### 2. 智能搜索

用户可以输入：
- "找配置选项"
- "搜索API方法"
- "页面里有使用场景吗？"

AI 会从页面内容中精准定位相关信息，并提供详细解答。

### 3. 选中文本解释

1. 在网页上选中任意文字
2. 出现"💡 点击解释这段文字"气泡
3. 点击气泡，AI 自动解释（支持中英文互译）

### 4. 复制网页 HTML

输入"复制网页HTML"，即可将完整网页代码复制到剪贴板。

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `ZHIPU_API_KEY` | 智谱 AI API Key | - | ✅ |
| `HOST` | 服务器主机地址 | 0.0.0.0 | ❌ |
| `PORT` | 服务器端口 | 8000 | ❌ |

### 模型配置

项目使用智谱 AI 的以下模型：

- **glm-4-flashx** - 对话模型（速度快，成本低）
- **CogView-4-250304** - 图像生成模型
- **glm-4v-flash** - 视觉分析模型

---

## 📚 技术栈

### 后端
- **FastAPI** 0.120+ - 现代高性能 Web 框架
- **pydantic-ai** 1.7.0+ - LLM 应用框架
- **SQLite** - 轻量级数据库
- **httpx** - 异步 HTTP 客户端

### 前端
- **原生 JavaScript** - 零依赖
- **Fetch API** - 流式响应
- **DOM 操作** - 动态渲染
- **CSS3** - 现代样式和动画

---

## 🔌 API 接口

详细的 API 文档请查看 [TECHNICAL_SUMMARY.md](./TECHNICAL_SUMMARY.md)

核心接口：
- `POST /api/sessions` - 创建会话
- `POST /api/chat/stream` - 流式对话
- `POST /api/image/generate` - 生成图片
- `POST /api/image/analyze` - 分析图片
- `GET /api/chat/history/{session_id}` - 获取历史记录

---

## 🎨 示例

### Vue 3 集成示例

项目提供了完整的 Vue 3 集成示例，查看 `演示/vue-demo.html`：

```javascript
const { createApp } = Vue;

createApp({
  mounted() {
    PopupChatKit.init({
      apiBase: 'http://localhost:8000/api',
      position: 'bottom-right',
      buttonColor: '#667eea'
    });
  }
}).mount('#app');
```

---

## 🌟 应用场景

- **企业官网** - 7×24 小时智能客服
- **在线文档** - 智能问答和内容搜索
- **电商平台** - 智能导购助手
- **在线教育** - 学习助手和答疑
- **个人博客** - 增强内容互动性

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 优秀的 Web 框架
- [pydantic-ai](https://ai.pydantic.dev/) - 强大的 LLM 框架
- [智谱AI](https://open.bigmodel.cn/) - 提供优质的 AI 服务

---

## 📞 联系方式

- 项目地址: [GitHub](https://github.com/yourusername/PopupChatKit)
- 问题反馈: [Issues](https://github.com/yourusername/PopupChatKit/issues)

---

**Made with ❤️ by PopupChatKit Team**

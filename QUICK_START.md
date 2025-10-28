# 🚀 PopupChatKit 快速启动指南

## 一键启动步骤

### 1. 启动后端服务

```bash
cd backend
uv run python main.py
```

看到以下输出表示成功:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 2. 打开前端页面

**方式一: 直接打开文件**
```bash
open frontend/standalone/chat.html
```

**方式二: 在浏览器手动打开**
- 用浏览器打开文件: `frontend/standalone/chat.html`
- 或访问: `file:///Users/colin/Desktop/home/code/PopupChatKit/frontend/standalone/chat.html`

### 3. 开始使用

1. 点击 "➕ 新建对话" 按钮
2. 在输入框输入消息
3. 按 Enter 或点击"发送"按钮
4. AI 会实时流式回复

## 🎯 功能测试清单

### 基础对话
- [ ] 发送简单问题 (如: "你好")
- [ ] 发送代码相关问题 (如: "写一个 Python 函数")
- [ ] 发送长文本
- [ ] 测试流式响应效果

### 会话管理
- [ ] 创建多个新对话
- [ ] 在不同会话间切换
- [ ] 查看会话列表
- [ ] 查看会话时间戳

### 交互体验
- [ ] 输入框自动调整高度
- [ ] Shift+Enter 换行
- [ ] Enter 直接发送
- [ ] 滚动到最新消息
- [ ] 思考动画显示

## 🔍 API 测试

### 访问 API 文档
```
http://localhost:8000/docs
```

### 健康检查
```bash
curl http://localhost:8000/api/health
```

### 获取版本信息
```bash
curl http://localhost:8000/api/version
```

### 测试对话 (非流式)
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -F "session_id=test-123" \
  -F "prompt=你好"
```

### 创建会话
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"测试会话","mode":"standalone"}'
```

### 获取会话列表
```bash
curl http://localhost:8000/api/sessions
```

## 📊 查看数据

### SQLite 数据库
```bash
# 安装 sqlite3 (macOS 自带)
sqlite3 ../data/chat.db

# 查看所有表
.tables

# 查看会话
SELECT * FROM sessions;

# 查看消息
SELECT * FROM messages;

# 退出
.quit
```

## 🐛 常见问题

### Q1: 后端启动失败?
**A:** 检查端口是否被占用
```bash
lsof -i :8000
# 如果有进程占用,kill 掉或换端口
```

### Q2: 前端无法连接后端?
**A:** 
1. 确认后端正在运行
2. 检查 console 是否有 CORS 错误
3. 确认 API 地址是 `http://localhost:8000/api`

### Q3: 消息没有响应?
**A:**
1. 检查智谱 API Key 是否正确
2. 查看后端控制台的错误信息
3. 检查网络连接

### Q4: 数据库初始化失败?
**A:**
```bash
# 删除旧数据库
rm ../data/chat.db
# 重启后端,会自动重新初始化
```

## 📝 配置说明

### 环境变量 (.env)
```bash
# 智谱 API Key
ZHIPU_API_KEY=your_api_key_here

# 数据库路径
DB_PATH=../data/chat.db

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 修改配置
1. 编辑 `backend/.env`
2. 重启后端服务

## 🔄 重启服务

### 停止服务
在后端终端按 `Ctrl+C`

### 重新启动
```bash
cd backend
uv run python main.py
```

## 📱 移动端访问

### 局域网访问
1. 获取本机 IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

2. 在手机浏览器访问:
```
http://your-ip:8000
```

## 🎨 自定义配置

### 修改主题颜色
编辑 `frontend/standalone/chat.html` 的 CSS 变量:
```css
:root {
    --primary: #667eea;  /* 主色调 */
    --secondary: #764ba2; /* 次要色 */
    /* ... */
}
```

### 切换 AI 模型
修改 `frontend/standalone/chat.html` 中的:
```javascript
model: 'zhipu',  // 改为 'qwen' (需先实现)
```

## 📚 更多文档

- 完整文档: `README.md`
- 开发文档: `ai-chat-ui/开发文档.md`
- 功能清单: `ai-chat-ui/功能点梳理.md`
- 实现报告: `IMPLEMENTATION_REPORT.md`

## 🎉 开始体验

现在你可以:
1. ✅ 与 AI 自由对话
2. ✅ 管理多个会话
3. ✅ 查看历史记录
4. ✅ 享受流畅的交互体验

祝使用愉快! 🚀

---

**需要帮助?** 
- 查看 API 文档: http://localhost:8000/docs
- 查看项目文档: README.md
- 检查错误日志: 后端控制台输出

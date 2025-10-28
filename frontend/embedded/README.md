# PopupChatKit 嵌入式插件

一个轻量级、零依赖的 AI 聊天插件,让你的网站瞬间拥有智能对话能力!

## ✨ 特性

- 🎨 **零依赖** - 纯原生 JavaScript,无需任何第三方库
- ⚡ **快速集成** - 一行代码即可在任何网站中使用
- 🎯 **高度可定制** - 丰富的配置选项,满足各种需求
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔄 **流式对话** - 支持流式响应,实时显示 AI 回复
- 💬 **会话管理** - 自动管理会话上下文,支持连续对话
- 📄 **智能总结** - 自动提取并总结当前网页内容
- 🔍 **搜索助手** - 快速在网页中查找并提取信息
- 📝 **文本解释** - 选中文字即可获得详细解释

## 🚀 快速开始

### 1. 引入插件

在你的 HTML 页面中添加以下代码:

```html
<!-- 引入 PopupChatKit 插件 -->
<script src="popup.js"></script>

<!-- 初始化插件 -->
<script>
  PopupChatKit.init({
    apiBase: 'http://localhost:8000/api'
  });
</script>
```

### 2. 完成!

就是这么简单!现在你的网站右下角会出现一个聊天按钮,点击即可开始对话。

## ⚙️ 配置选项

```javascript
PopupChatKit.init({
  // API 基础地址 (必填)
  apiBase: 'http://localhost:8000/api',
  
  // 按钮位置 (可选,默认: 'bottom-right')
  // 可选值: 'bottom-right', 'bottom-left', 'top-right', 'top-left'
  position: 'bottom-right',
  
  // 按钮大小 (可选,默认: 60)
  buttonSize: 60,
  
  // 按钮颜色 (可选,默认: '#6366f1')
  buttonColor: '#6366f1',
  
  // 聊天窗口最大宽度 (可选,默认: 400)
  maxWidth: 400,
  
  // 聊天窗口最大高度 (可选,默认: 600)
  maxHeight: 600,
  
  // 层级 (可选,默认: 9999)
  zIndex: 9999
});
```

## 📖 API 方法

PopupChatKit 提供了以下方法供你调用:

```javascript
// 打开聊天窗口
PopupChatKit.open();

// 关闭聊天窗口
PopupChatKit.close();

// 切换显示/隐藏
PopupChatKit.toggle();
```

## � 智能功能

### 1. 📄 网页总结

输入以下任一关键词即可自动总结当前页面：
- "总结这个网页"
- "概括页面内容"
- "这个页面讲了什么？"
- "摘要"

**工作原理：**
- 自动提取页面标题、URL 和文本内容
- 发送给 AI 进行智能总结
- 返回结构化的摘要

### 2. 🔍 智能搜索

在页面中快速查找信息：
- "找XXX信息"
- "搜索关于XXX的内容"
- "页面里有没有XXX"
- "哪里提到了XXX"

**工作原理：**
- 从完整页面内容中搜索
- AI 提取最相关的段落
- 提供位置提示和解答

### 3. 📝 选中文本解释 ⭐ 新体验

选中网页上的任意文字，会自动出现可点击的提示气泡：

**使用方法：**
1. 用鼠标选中任意文字
2. 出现"💡 点击解释这段文字"气泡（悬停有放大效果）
3. **直接点击气泡**即可自动发送解释请求
4. 无需手动输入，避免选中消失的问题

**支持的表达方式：**
- 点击气泡（推荐）
- 手动输入"解释"
- "什么意思？"
- "翻译"

**工作原理：**
- 自动捕获选中的文本（最多500字符）
- 显示可点击的悬浮提示（5秒后自动消失）
- 点击后自动打开聊天窗口并发送
- 结合页面上下文给出解释
- 支持中英文互译

### 4. 📋 复制网页 HTML 🆕

一键复制完整网页代码，方便保存和分享：

**使用方法：**
- "复制网页 HTML"
- "复制页面代码"
- "导出 HTML"
- "获取 HTML"

**工作原理：**
- 获取 `document.documentElement.outerHTML`
- 使用 Clipboard API 复制到剪贴板
- 显示统计信息（字符数、标题、URL）
- 可粘贴到编辑器保存为 .html 文件

**应用场景：**
- 保存网页副本
- 分享网页给他人
- 备份重要页面
- 学习网页源码

## �🎨 示例

### 示例 1: 基础用法

```html
<!DOCTYPE html>
<html>
<head>
  <title>我的网站</title>
</head>
<body>
  <h1>欢迎来到我的网站</h1>
  
  <!-- 你的网站内容 -->
  
  <script src="popup.js"></script>
  <script>
    PopupChatKit.init({
      apiBase: 'http://localhost:8000/api'
    });
  </script>
</body>
</html>
```

### 示例 2: 自定义样式

```javascript
PopupChatKit.init({
  apiBase: 'http://localhost:8000/api',
  position: 'bottom-left',      // 左下角
  buttonColor: '#ff6b6b',        // 红色按钮
  buttonSize: 70,                // 更大的按钮
  maxWidth: 500,                 // 更宽的窗口
  maxHeight: 700                 // 更高的窗口
});
```

### 示例 3: 自定义触发按钮

```html
<!-- 使用自己的按钮 -->
<button onclick="PopupChatKit.open()">
  联系客服
</button>

<script src="popup.js"></script>
<script>
  PopupChatKit.init({
    apiBase: 'http://localhost:8000/api'
  });
</script>
```

## 📂 文件结构

```
frontend/embedded/
├── popup.js          # 核心插件文件
├── demo.html         # 完整演示页面
├── simple.html       # 简单示例
└── README.md         # 使用文档
```

## 🎯 使用场景

- **企业官网** - 提供 7×24 小时智能客服
- **电商平台** - 智能导购助手
- **在线教育** - 学习助手和答疑
- **SaaS 产品** - 产品使用指导
- **个人博客** - 互动式内容助手

## 🔧 技术实现

- **纯原生 JavaScript** - 无依赖,兼容性好
- **流式响应** - 使用 Fetch API + ReadableStream
- **会话管理** - 自动创建和维护会话上下文
- **响应式设计** - CSS Grid + Media Queries
- **模块化设计** - IIFE 模式,避免全局污染

## 📱 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## 🎓 高级用法

### 监听聊天状态

你可以扩展插件来监听聊天状态:

```javascript
// 扩展 PopupChatKit
const originalOpen = PopupChatKit.open;
PopupChatKit.open = function() {
  console.log('聊天窗口打开');
  originalOpen.call(this);
};

const originalClose = PopupChatKit.close;
PopupChatKit.close = function() {
  console.log('聊天窗口关闭');
  originalClose.call(this);
};
```

### 自定义样式

插件会自动注入样式,如果你想自定义样式,可以在页面中添加覆盖样式:

```css
/* 自定义样式 */
.popup-chat-button {
  /* 你的自定义样式 */
}

.popup-chat-window {
  /* 你的自定义样式 */
}
```

## 📝 注意事项

1. **API 地址**: 确保 `apiBase` 指向正确的后端 API 地址
2. **CORS 设置**: 如果前后端不在同一域名,需要配置 CORS
3. **HTTPS**: 生产环境建议使用 HTTPS
4. **性能**: 插件非常轻量,对页面性能影响极小

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可

MIT License

## 🔗 相关链接

- [完整文档](../README.md)
- [后端 API](../../backend/)
- [独立版本](../standalone/)

---

Made with ❤️ by PopupChatKit

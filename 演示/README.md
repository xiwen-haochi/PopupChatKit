# 演示文件夹

这个文件夹包含了 PopupChatKit 的各种演示示例。

## 📂 文件列表

### vue-demo.html
使用 Vue 3 单文件模式构建的演示页面。

**特点：**
- ✅ 使用 CDN 引入 Vue 3（无需构建）
- ✅ 响应式数据绑定
- ✅ 完整的文章内容展示
- ✅ 集成 PopupChatKit 插件
- ✅ 精美的 UI 设计

**技术栈：**
- Vue 3（从 CDN 引入）
- 原生 JavaScript
- PopupChatKit 插件

## 🚀 使用方法

### 1. 确保后端运行

```bash
cd ../backend
uv run uvicorn main:app --reload --port 8000
```

### 2. 打开演示页面

直接用浏览器打开 `vue-demo.html` 文件，或者：

```bash
open vue-demo.html
```

### 3. 体验功能

- **对话功能**：点击右下角聊天按钮
- **总结网页**：输入"总结这个页面"
- **搜索内容**：输入"找技术架构"
- **解释文本**：选中文字后点击气泡
- **复制网页**：输入"复制网页HTML"

## 🎯 演示内容

这个页面展示了一篇关于 AI 智能对话系统的技术文章，包含：

1. **文章标题和元信息**：日期、作者、阅读量、标签
2. **完整内容**：
   - 什么是 AI 智能对话
   - PopupChatKit 的技术架构
   - 核心功能详解
   - 使用场景
   - 集成指南
   - 总结与展望
3. **交互提示**：引导用户体验各种功能

## 💡 最佳体验建议

1. **总结文章**：
   - 输入："总结这个页面"
   - AI 会分析整篇文章并给出摘要

2. **搜索信息**：
   - 输入："找关于技术架构的内容"
   - AI 会定位相关段落并解答

3. **解释术语**：
   - 选中 "IIFE" 或 "Transformer" 等术语
   - 点击出现的气泡
   - AI 会结合上下文解释

4. **复制页面**：
   - 输入："复制网页HTML"
   - 可以保存完整页面

## 🎨 自定义

你可以修改 `vue-demo.html` 中的内容：

### 修改文章内容
```javascript
article: {
    title: '你的文章标题',
    date: '2025年10月28日',
    author: '作者名',
    tags: ['标签1', '标签2'],
    // ...
}
```

### 修改插件配置
```javascript
PopupChatKit.init({
    apiBase: 'http://localhost:8000/api',
    position: 'bottom-left',  // 改变位置
    buttonColor: '#ff6b6b'     // 改变颜色
});
```

## 📝 注意事项

1. **CORS 问题**：确保后端 API 允许跨域请求
2. **路径配置**：`popup.js` 的路径相对于当前文件
3. **Vue 版本**：使用 Vue 3 的 CDN 版本

## 🔗 相关链接

- [PopupChatKit 文档](../frontend/embedded/README.md)
- [后端 API](../backend/)
- [独立版本](../frontend/standalone/)

---

Made with ❤️ by PopupChatKit

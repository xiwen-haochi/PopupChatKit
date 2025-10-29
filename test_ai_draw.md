# AI 自动判断绘图功能测试

## 架构变更

### 旧方案（前端关键词检测）
```
用户输入 "画小猫" 
→ 前端检测关键词 
→ 调用 /api/draw
```

**问题**：
- ❌ 关键词硬编码，不够智能
- ❌ 无法理解复杂意图
- ❌ 前端逻辑复杂

### 新方案（AI 工具调用）
```
用户输入 "画小猫"
→ 前端发送到 /api/chat/stream
→ AI 理解意图
→ AI 决定调用 generate_image_tool
→ 工具返回图片 URL
→ AI 返回包含图片的响应
```

**优势**：
- ✅ AI 智能判断，理解能力更强
- ✅ 支持复杂的上下文理解
- ✅ 前端逻辑简化
- ✅ 统一的 API 接口

## 代码变更

### 后端 (agents.py)

1. **添加绘图工具**：
```python
async def generate_image_tool(
    ctx: RunContext[None],
    prompt: Annotated[str, "用户想要生成的图片描述"]
) -> str:
    """生成图片的工具函数"""
    # 调用智谱 CogView-4 绘图 API
    # 返回图片 URL
```

2. **注册工具到 Agent**：
```python
zhipu_agent = Agent(
    model,
    system_prompt="...",
    tools=[generate_image_tool]  # 注册绘图工具
)
```

3. **更新 System Prompt**：
```
重要能力:
- 当用户明确要求生成/绘制/创作图片时，调用 generate_image_tool
- 识别用户意图：包含"画"、"生成图"、"创作"等词汇
```

### 前端 (chat.html)

1. **简化发送消息逻辑**：
```javascript
// 旧代码
const shouldGenerateImage = currentMode === 'image' || isDrawRequest(message);
if (shouldGenerateImage) {
    await generateImage(message);
} else {
    await sendChatMessage(message);
}

// 新代码
await sendChatMessage(message);  // 所有消息统一走聊天 API
```

2. **注释关键词检测函数**：
```javascript
// function isDrawRequest(text) { ... }  // 已弃用
```

3. **简化模式切换**：
- 移除 `currentMode` 变量
- 保留模式切换按钮（用于 UI 提示）

## 测试用例

### 基础绘图请求
- ✅ "画一只小猫"
- ✅ "帮我生成一张风景图"
- ✅ "创作一个可爱的卡通形象"
- ✅ "Draw a cat"

### 上下文理解
- ✅ "我想要一张图片，内容是..." → AI 理解应该绘图
- ✅ "能帮我设计一个..." → AI 判断是否绘图
- ❌ "小猫很可爱" → AI 判断为普通对话

### 复杂场景
- ✅ 先聊天："什么是猫？" → 文本回答
- ✅ 再绘图："画一只" → AI 根据上下文理解，调用绘图
- ✅ 混合："帮我画只猫，然后告诉我它的特点" → AI 先绘图，再文字说明

## 技术优势

### Pydantic AI 工具系统
1. **类型安全**：`Annotated` 类型提示
2. **自动解析**：AI 自动决定何时调用工具
3. **流式支持**：工具调用也支持流式输出
4. **上下文管理**：`RunContext` 提供运行时上下文

### 智能判断
- AI 可以理解更复杂的意图表达
- 不需要维护关键词列表
- 支持多语言（AI 模型本身支持）
- 可以根据上下文判断

## 注意事项

1. **工具调用时延**：AI 需要先判断，然后调用工具，可能比直接调用慢一点
2. **成本考虑**：每次都要 AI 判断，token 消耗略高
3. **错误处理**：工具调用失败时，AI 会返回错误信息
4. **提示词优化**：System Prompt 需要清晰指导 AI 何时调用工具

## 未来扩展

### 可以添加更多工具
```python
@zhipu_agent.tool
async def search_web(query: str) -> str:
    """搜索网络"""
    
@zhipu_agent.tool
async def analyze_code(code: str, language: str) -> str:
    """分析代码"""
```

AI 会根据用户意图自动选择合适的工具！

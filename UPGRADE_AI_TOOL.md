# 🎨 升级：AI 自动判断绘图功能

## 📊 架构对比

### ❌ 旧方案：前端关键词检测
```
用户："画小猫" 
  ↓
前端 isDrawRequest() 检测关键词
  ↓
调用 /api/draw
```

**问题**：
- 关键词硬编码，维护成本高
- 无法理解复杂语义
- 前端逻辑耦合

### ✅ 新方案：AI 工具调用（Pydantic AI）
```
用户："画小猫"
  ↓
前端统一调用 /api/chat/stream
  ↓
AI Agent 理解意图
  ↓
AI 决定调用 generate_image_tool
  ↓
工具返回图片 URL
  ↓
AI 组织响应（包含图片）
```

**优势**：
- ✅ AI 智能判断，语义理解强
- ✅ 支持上下文关联
- ✅ 前端逻辑简化
- ✅ 统一 API 接口
- ✅ 易于扩展更多工具

## 🔧 代码变更详解

### 1. 后端：agents.py

#### 添加依赖
```python
from typing import Annotated
import httpx
from pydantic_ai import RunContext
```

#### 定义绘图工具
```python
async def generate_image_tool(
    ctx: RunContext[None],
    prompt: Annotated[str, "用户想要生成的图片描述"]
) -> str:
    """生成图片的工具函数
    
    当用户明确表达想要生成、绘制、创作图片时调用此工具。
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENAI_BASE_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {ZHIPU_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "cogview-4-250304",
                    "prompt": prompt,
                    "size": "1024x1024"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                image_url = data['data'][0]['url']
                return f"✅ 图片生成成功！\n\n![生成的图片]({image_url})\n\n图片描述：{prompt}"
            else:
                return f"❌ 图片生成失败"
                
    except Exception as e:
        return f"❌ 图片生成失败：{str(e)}"
```

#### 注册工具到 Agent
```python
zhipu_agent = Agent(
    model,
    system_prompt="""你是一个友好、专业的 AI 助手。

重要能力:
- 当用户明确要求生成/绘制/创作图片时，调用 generate_image_tool 工具
- 识别用户意图：包含"画"、"生成图"、"创作"、"设计图片"等词汇
- 调用工具后，直接将结果展示给用户
""",
    tools=[generate_image_tool]  # ⭐ 关键：注册工具
)
```

### 2. 前端：chat.html

#### 简化发送消息逻辑
```javascript
// ❌ 旧代码（约 10 行）
const shouldGenerateImage = currentMode === 'image' || isDrawRequest(message);
if (shouldGenerateImage) {
    await generateImage(message);
} else {
    await sendChatMessage(message);
}

// ✅ 新代码（1 行）
await sendChatMessage(message);  // 统一走聊天 API
```

#### 注释关键词检测
```javascript
// ❌ 已弃用
// function isDrawRequest(text) { ... }
```

#### 简化模式切换
```javascript
// 移除 currentMode 变量
// 保留模式切换 UI（用于提示）
function switchMode(mode) {
    // 更新 UI 提示
    input.placeholder = mode === 'image' 
        ? '描述你想要的画面，AI 会自动判断...'
        : '输入消息...';
}
```

## 🧪 测试用例

### 基础测试
```bash
cd backend
uv run python test_tool.py
```

### 手动测试

#### ✅ 应该调用绘图工具
- "画一只小猫"
- "帮我生成一张风景图"
- "创作一个可爱的卡通人物"
- "设计一个 logo"
- "Draw a cat"
- "Generate an image of..."

#### ❌ 不应该调用绘图工具
- "小猫有什么特点？"
- "猫的品种有哪些？"
- "我喜欢猫"
- "Tell me about cats"

#### 🎯 上下文理解
- Q: "什么是猫？" → 文本回答
- Q: "画一只" → AI 理解上下文，调用绘图

## 🔍 技术细节

### Pydantic AI 工具系统

1. **类型注解**：
```python
Annotated[str, "参数描述"]  # 帮助 AI 理解参数含义
```

2. **自动调用**：
   - AI 根据用户输入自动决定是否调用工具
   - 不需要硬编码的 if-else 逻辑

3. **流式支持**：
   - `agent.run_stream()` 自动处理工具调用
   - 工具调用结果也可以流式返回

4. **上下文管理**：
   - `RunContext` 提供运行时信息
   - 可以在工具中访问对话历史

### AI 判断逻辑

AI 通过以下方式判断是否调用工具：

1. **System Prompt 指导**：
   ```
   当用户明确要求生成/绘制/创作图片时，调用 generate_image_tool
   ```

2. **语义理解**：
   - AI 理解"画"、"生成"、"创作"等词的含义
   - 不需要完全匹配关键词

3. **上下文关联**：
   - "画一只" → AI 结合上下文理解是绘图请求
   - "我喜欢画画" → AI 判断为描述，不调用工具

## 📈 性能考虑

### Token 消耗
- **旧方案**：无额外消耗（前端判断）
- **新方案**：每次请求 AI 需判断（约 +50 tokens）

### 响应时间
- **旧方案**：直接调用绘图 API
- **新方案**：AI 判断 → 调用工具（约 +0.5s）

### 成本效益
虽然略有额外消耗，但带来：
- 更好的用户体验
- 更智能的意图理解
- 更低的维护成本

**结论：值得！** 🎉

## 🚀 未来扩展

### 添加更多工具

```python
@zhipu_agent.tool
async def search_web(query: Annotated[str, "搜索关键词"]) -> str:
    """搜索网络信息"""
    # 实现网络搜索
    pass

@zhipu_agent.tool
async def analyze_code(
    code: Annotated[str, "代码内容"],
    language: Annotated[str, "编程语言"]
) -> str:
    """分析代码质量"""
    # 实现代码分析
    pass

@zhipu_agent.tool
async def translate_text(
    text: Annotated[str, "待翻译文本"],
    target_lang: Annotated[str, "目标语言"]
) -> str:
    """翻译文本"""
    # 实现翻译
    pass
```

### 工具组合
AI 可以自动组合多个工具：
```
用户："画一只猫，然后翻译成英文描述"
  ↓
AI 调用 generate_image_tool
  ↓
AI 调用 translate_text
  ↓
返回图片 + 英文描述
```

## ⚠️ 注意事项

1. **API Key 安全**：
   - ✅ 工具在后端调用，Key 不暴露
   - ✅ 前端无需知道工具实现

2. **错误处理**：
   - 工具调用失败时，AI 会返回错误信息
   - 用户体验更友好

3. **调试**：
   ```python
   # 在 agents.py 中添加日志
   print(f"Tool called: {tool_name}")
   print(f"Tool result: {result}")
   ```

4. **提示词优化**：
   - System Prompt 需要清晰指导 AI
   - 可以通过测试不断优化

## 📝 总结

### 变更文件
- ✅ `backend/agents.py` - 添加绘图工具
- ✅ `frontend/standalone/chat.html` - 简化前端逻辑
- ✅ `backend/test_tool.py` - 测试脚本

### 删除的代码
- ❌ `isDrawRequest()` 函数
- ❌ `currentMode` 变量和相关逻辑
- ❌ 前端关键词数组

### 新增的功能
- ✅ AI 工具系统
- ✅ 智能意图识别
- ✅ 可扩展工具架构

### 代码行数变化
- 后端：+60 行（工具定义）
- 前端：-30 行（简化逻辑）
- **净变化：+30 行，但功能更强大！**

---

**现在可以启动服务测试了！** 🚀

```bash
cd backend
uv run uvicorn main:app --reload
```

访问 http://localhost:8000 体验智能绘图！

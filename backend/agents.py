"""AI Agent 配置模块

使用 pydantic-ai 统一管理不同的 LLM 模型
"""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelMessage, ModelRequest, ModelResponse
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()  # 从 .env 文件加载环境变量

# 从环境变量读取 API Key
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', '')
print(f"ZHIPU_API_KEY: {ZHIPU_API_KEY}")
# ============================================
# 配置智谱 AI 模型
# ============================================

zhipu_model_str = 'glm-4-flashx'


model = OpenAIChatModel(
    zhipu_model_str,
    provider=OpenAIProvider(
        base_url=OPENAI_BASE_URL, api_key=ZHIPU_API_KEY
    ),
)
zhipu_agent = Agent(
    model,
    system_prompt="""你是一个友好、专业的 AI 助手。

你的职责:
1. 准确理解用户意图,提供有价值的回答
2. 以简洁清晰的方式表达,必要时使用 Markdown 格式
3. 对于代码相关问题,提供完整可运行的示例
4. 遇到不确定的信息,诚实告知而非臆测

你的特点:
- 友好但不过度热情
- 专业但不生硬
- 简洁但不省略关键信息
"""
)


# ============================================
# Agent 获取函数
# ============================================

def get_agent(model: str = 'zhipu') -> Agent:
    """根据模型名称获取 Agent
    
    Args:
        model: 模型名称,默认使用智谱 (目前只支持 zhipu)
        
    Returns:
        Agent 实例
    """
    # 目前只实现了智谱
    return zhipu_agent


# ============================================
# 消息转换函数
# ============================================

def to_chat_message(m: ModelMessage) -> dict:
    """将 ModelMessage 转换为前端需要的格式
    
    Args:
        m: pydantic-ai 的 ModelMessage
        
    Returns:
        字典格式的消息
    """
    from pydantic_ai import UserPromptPart, TextPart
    from datetime import datetime, timezone
    
    # 如果 parts 列表为空,返回默认值
    if not m.parts:
        return {
            'role': 'unknown',
            'timestamp': datetime.now(tz=timezone.utc).isoformat(),
            'content': '',
        }
    
    first_part = m.parts[0]
    
    if isinstance(m, ModelRequest):
        # 用户消息
        if isinstance(first_part, UserPromptPart):
            content = first_part.content
            if isinstance(content, str):
                return {
                    'role': 'user',
                    'timestamp': first_part.timestamp.isoformat() if hasattr(first_part, 'timestamp') else datetime.now(tz=timezone.utc).isoformat(),
                    'content': content,
                }
    elif isinstance(m, ModelResponse):
        # AI 响应
        if isinstance(first_part, TextPart):
            return {
                'role': 'assistant',
                'timestamp': m.timestamp.isoformat() if hasattr(m, 'timestamp') else datetime.now(tz=timezone.utc).isoformat(),
                'content': first_part.content,
            }
    
    # 默认返回
    return {
        'role': 'unknown',
        'timestamp': datetime.now(tz=timezone.utc).isoformat(),
        'content': str(m),
    }

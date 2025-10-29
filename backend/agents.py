"""AI Agent 配置模块

使用 pydantic-ai 统一管理不同的 LLM 模型
"""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelMessage, ModelRequest, ModelResponse, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()  # 从 .env 文件加载环境变量

# 从环境变量读取 API Key
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', '')
GAODE_API_KEY = os.getenv('GAODE_API_KEY', '')
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
5. 当用户询问天气时，使用 get_weather 工具查询实时天气信息

你的特点:
- 友好但不过度热情
- 专业但不生硬
- 简洁但不省略关键信息

可用工具：
- get_weather(city): 查询指定城市的实时天气信息
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


# ============================================
# 工具函数定义
# ============================================

@zhipu_agent.tool
async def get_weather(ctx: RunContext[None], city: str) -> str:
    """获取指定城市的天气信息
    
    当用户询问天气时调用此工具。
    
    Args:
        city: 城市名称，例如"北京"、"上海"、"深圳"等
        
    Returns:
        str: 该城市的天气信息，包括天气状况、温度、湿度、风向等
    """
    import httpx
    
    print(f"🌤️  [天气工具] 查询城市: {city}")
    
    async def get_city_code(city_name: str) -> str | None:
        """通过高德地图API获取城市编码"""
        url = "https://restapi.amap.com/v3/config/district"
        params = {
            "key": GAODE_API_KEY,
            "keywords": city_name,
            "subdistrict": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                result = response.json()
                
                if result.get("status") == "1" and result.get("districts"):
                    adcode = result["districts"][0]["adcode"]
                    print(f"🗺️  城市编码: {city_name} → {adcode}")
                    return adcode
                else:
                    print(f"❌ 未找到城市: {city_name}")
                    return None
        except Exception as e:
            print(f"❌ 获取城市编码失败: {e}")
            return None
    
    # 获取城市编码
    city_code = await get_city_code(city)
    if not city_code:
        return f'抱歉，未找到城市 {city} 的信息，请检查城市名称是否正确。'
    
    # 查询天气信息
    try:
        weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            "city": city_code,
            "key": GAODE_API_KEY,
            "extensions": "base",
            "output": "JSON"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(weather_url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("lives"):
                weather_info = data["lives"][0]
                result = (
                    f"📍 {weather_info['city']}的天气：\n"
                    f"🌡️ 天气：{weather_info['weather']}\n"
                    f"🌡️ 温度：{weather_info['temperature']}°C\n"
                    f"💧 湿度：{weather_info['humidity']}%\n"
                    f"🌬️ 风向：{weather_info['winddirection']}\n"
                    f"💨 风力：{weather_info['windpower']}级\n"
                    f"🕐 更新时间：{weather_info['reporttime']}"
                )
                print(f"✅ [天气工具] 查询成功: {city}")
                return result
            else:
                error_msg = data.get("info", "未知错误")
                print(f"❌ [天气工具] API返回错误: {error_msg}")
                return f"获取{city}天气信息失败：{error_msg}"
            
    except Exception as e:
        print(f"❌ [天气工具] 查询失败: {e}")
        return f"查询天气时发生错误：{str(e)}"
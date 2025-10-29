"""测试天气工具的 Function Call 功能"""

import asyncio
from agents import get_agent

async def test_weather_tool():
    """测试天气查询工具"""
    
    agent = get_agent('zhipu')
    
    test_questions = [
        "北京今天天气怎么样？",
        "上海的天气如何？",
        "深圳会下雨吗？",
        "查询广州的天气",
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ 问题: {question}")
        print(f"{'='*60}")
        
        try:
            result = await agent.run(question)
            print(f"\n🤖 回答:\n{result.output}")
                    
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_weather_tool())

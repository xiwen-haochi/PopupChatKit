"""测试 AI 工具调用"""
import asyncio
from agents import get_agent

async def test_draw_tool():
    """测试绘图工具调用"""
    agent = get_agent('zhipu')
    
    # 测试用例 1: 明确的绘图请求
    print("=" * 50)
    print("测试 1: 画一只小猫")
    print("=" * 50)
    result = await agent.run("画一只可爱的小猫")
    print(f"结果: {result.output}")
    print()
    
    # 测试用例 2: 普通对话
    print("=" * 50)
    print("测试 2: 小猫有什么特点?")
    print("=" * 50)
    result = await agent.run("小猫有什么特点?")
    print(f"结果: {result.output}")
    print()
    
    # 测试用例 3: 英文绘图请求
    print("=" * 50)
    print("测试 3: Draw a cat")
    print("=" * 50)
    result = await agent.run("Draw a beautiful cat")
    print(f"结果: {result.output}")
    print()

if __name__ == "__main__":
    asyncio.run(test_draw_tool())

import asyncio
from agents import zhipu_agent

async def test():
    result = await zhipu_agent.run("你好")
    print(result.output)

asyncio.run(test())

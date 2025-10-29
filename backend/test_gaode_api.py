"""直接测试天气工具"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

GAODE_API_KEY = os.getenv('GAODE_API_KEY', '')
print(f"GAODE_API_KEY: {GAODE_API_KEY}")
print(f"API Key 长度: {len(GAODE_API_KEY)}")

async def test_city_code():
    """测试获取城市编码"""
    import httpx
    
    city_name = "上海"
    url = "https://restapi.amap.com/v3/config/district"
    params = {
        "key": GAODE_API_KEY,
        "keywords": city_name,
        "subdistrict": 0
    }
    
    print(f"\n请求URL: {url}")
    print(f"请求参数: {params}")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            result = response.json()
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应内容: {result}")
            
            if result.get("status") == "1" and result.get("districts"):
                adcode = result["districts"][0]["adcode"]
                print(f"\n✅ 成功获取城市编码: {city_name} → {adcode}")
                return adcode
            else:
                print(f"\n❌ 获取失败: {result.get('info', '未知错误')}")
                return None
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    asyncio.run(test_city_code())

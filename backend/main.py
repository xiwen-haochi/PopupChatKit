"""PopupChatKit 主应用入口

基于 FastAPI 和 pydantic-ai 的 AI 对话系统
"""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

import fastapi
from fastapi import Depends, Form, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import Database
from agents import get_agent, to_chat_message

# 路径配置
THIS_DIR = Path(__file__).parent
PROJECT_ROOT = THIS_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
DATA_DIR = PROJECT_ROOT / 'data'
DB_FILE = DATA_DIR / os.getenv('DB_NAME', 'chat.db')

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    """应用生命周期管理"""
    async with Database.connect(DB_FILE) as db:
        yield {'db': db}


# 创建 FastAPI 应用
app = fastapi.FastAPI(
    title="PopupChatKit API",
    description="AI 对话与网页分析服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地使用,允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 依赖注入
async def get_db(request: Request) -> Database:
    """获取数据库连接"""
    return request.state.db


# ============================================
# Pydantic 模型
# ============================================

class ChatMessage(BaseModel):
    """对话请求模型"""
    session_id: str
    message: str
    stream: bool = True


class SessionCreate(BaseModel):
    """创建会话请求"""
    title: str
    mode: str = 'standalone'


class WebExtractRequest(BaseModel):
    """网页提取请求"""
    url: str | None = None
    content: str | None = None
    mode: str = 'text'


class ConfigRequest(BaseModel):
    """配置保存请求"""
    key: str
    value: str


# ============================================
# 静态文件服务
# ============================================

@app.get("/")
async def root():
    """返回首页"""
    # 如果 frontend 目录存在,返回 index.html
    index_file = FRONTEND_DIR / 'standalone' / 'index.html'
    if index_file.exists():
        return FileResponse(index_file, media_type='text/html')
    return {"message": "PopupChatKit API", "docs": "/docs"}


# ============================================
# 对话相关 API
# ============================================

@app.post('/api/chat/stream')
async def chat_stream(
    chat_req: ChatMessage,
    database: Database = Depends(get_db)
) -> StreamingResponse:
    """流式对话接口"""
    
    async def stream_messages():
        try:
            # 发送开始标记
            yield json.dumps({
                'type': 'start',
                'timestamp': datetime.now(tz=timezone.utc).isoformat()
            }).encode('utf-8') + b'\n'
            
            # 获取历史消息
            messages = await database.get_messages(chat_req.session_id)
            
            # 选择 Agent (默认智谱)
            agent = get_agent('zhipu')
            
            # 流式运行 Agent
            async with agent.run_stream(
                chat_req.message,
                message_history=messages
            ) as result:
                # 流式输出内容
                full_response = ""
                async for text in result.stream_text(debounce_by=0.01):
                    full_response = text
                    yield json.dumps({
                        'type': 'content',
                        'content': text
                    }).encode('utf-8') + b'\n'
            
            # 保存新消息到数据库 (用于 AI 上下文)
            await database.add_messages(
                chat_req.session_id,
                result.new_messages_json()
            )
            
            # 保存格式化消息到聊天消息表 (用于显示)
            await database.add_chat_message(
                chat_req.session_id,
                'user',
                chat_req.message,
                'text'
            )
            await database.add_chat_message(
                chat_req.session_id,
                'assistant',
                full_response,
                'text'
            )
            
            # 更新会话时间
            await database.update_session(chat_req.session_id)
            
            # 发送结束标记
            yield json.dumps({
                'type': 'end',
                'timestamp': datetime.now(tz=timezone.utc).isoformat()
            }).encode('utf-8') + b'\n'
            
        except Exception as e:
            yield json.dumps({
                'type': 'error',
                'message': str(e)
            }).encode('utf-8') + b'\n'
    
    return StreamingResponse(
        stream_messages(),
        media_type='text/plain'
    )


@app.get('/api/chat/history/{session_id}')
async def get_chat_history(
    session_id: str,
    database: Database = Depends(get_db)
):
    """获取对话历史"""
    # 使用新的格式化消息表
    chat_messages = await database.get_chat_messages(session_id)
    return {
        'session_id': session_id,
        'messages': chat_messages
    }


@app.post('/api/chat/message')
async def post_chat_message(
    prompt: Annotated[str, Form()],
    session_id: Annotated[str, Form()],
    database: Database = Depends(get_db)
):
    """非流式对话接口"""
    try:
        # 获取历史消息
        messages = await database.get_messages(session_id)
        
        # 获取 Agent
        agent = get_agent('zhipu')
        
        # 运行对话
        result = await agent.run(prompt, message_history=messages)
        
        # 保存消息
        await database.add_messages(session_id, result.new_messages_json())
        await database.update_session(session_id)
        
        return {
            'response': result.output,
            'timestamp': datetime.now(tz=timezone.utc).isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500


# ============================================
# 会话管理 API
# ============================================

@app.get('/api/sessions')
async def get_sessions(
    limit: int = 50,
    database: Database = Depends(get_db)
):
    """获取会话列表"""
    sessions = await database.get_sessions(limit)
    return {'sessions': sessions}


@app.post('/api/sessions')
async def create_session(
    request: SessionCreate,
    database: Database = Depends(get_db)
):
    """创建新会话"""
    import uuid
    session_id = str(uuid.uuid4())
    await database.create_session(session_id, request.title, request.mode)
    return {
        'session_id': session_id,
        'title': request.title,
        'mode': request.mode
    }


@app.put('/api/sessions/{session_id}')
async def update_session_title(
    session_id: str,
    title: str,
    database: Database = Depends(get_db)
):
    """更新会话标题"""
    await database.update_session(session_id, title)
    return {'message': 'Session updated'}


@app.delete('/api/sessions/{session_id}')
async def delete_session(
    session_id: str,
    database: Database = Depends(get_db)
):
    """删除会话"""
    await database.delete_session(session_id)
    return {'message': 'Session deleted'}


# ============================================
# 配置管理 API
# ============================================

# @app.get('/api/config')
# async def get_all_config(database: Database = Depends(get_db)):
#     """获取所有配置"""
#     # 这里可以返回非敏感配置
#     default_model = await database.get_config('default_model')
#     theme = await database.get_config('theme')
#     return {
#         'default_model': default_model or 'zhipu',
#         'theme': theme or 'light'
#     }


# @app.get('/api/config/{key}')
# async def get_config(
#     key: str,
#     database: Database = Depends(get_db)
# ):
#     """获取指定配置"""
#     value = await database.get_config(key)
#     return {'key': key, 'value': value}


# @app.post('/api/config')
# async def save_config(
#     request: ConfigRequest,
#     database: Database = Depends(get_db)
# ):
#     """保存配置"""
#     await database.save_config(request.key, request.value)
#     return {'message': 'Config saved'}


# ============================================
# 网页分析 API
# ============================================

@app.post('/api/web/extract')
async def extract_web_content(request: WebExtractRequest):
    """提取网页内容"""
    # 简化实现,实际应使用专门的网页提取库
    if request.content:
        return {
            'title': 'User Content',
            'content': request.content[:5000],
            'url': request.url or 'N/A'
        }
    elif request.url:
        return {
            'title': 'URL Content',
            'content': f'Content from {request.url}',
            'url': request.url
        }
    return {'error': 'No content or URL provided'}, 400


@app.post('/api/web/summarize')
async def summarize_web(
    request: WebExtractRequest,
    database: Database = Depends(get_db)
) -> StreamingResponse:
    """总结网页内容 (流式响应)"""
    
    async def stream_summary():
        try:
            content = request.content or ''
            url = request.url or 'N/A'
            
            # 使用 AI 总结
            agent = get_agent('zhipu')
            prompt = f"""请总结以下网页内容:

URL: {url}

内容:
{content[:3000]}

请用简洁的语言总结主要内容,不超过200字,使用 Markdown 格式。"""
            
            # 发送开始标记
            yield json.dumps({
                'type': 'start',
                'url': url
            }).encode('utf-8') + b'\n'
            
            # 流式运行
            async with agent.run_stream(prompt) as result:
                async for text in result.stream_text(debounce_by=0.01):
                    yield json.dumps({
                        'type': 'content',
                        'content': text
                    }).encode('utf-8') + b'\n'
            
            # 发送结束标记
            yield json.dumps({
                'type': 'end'
            }).encode('utf-8') + b'\n'
            
        except Exception as e:
            yield json.dumps({
                'type': 'error',
                'message': str(e)
            }).encode('utf-8') + b'\n'
    
    return StreamingResponse(
        stream_summary(),
        media_type='text/plain'
    )


@app.post('/api/web/to-json')
async def web_to_json(
    request: WebExtractRequest,
    database: Database = Depends(get_db)
) -> StreamingResponse:
    """将网页内容转换为 JSON (流式响应)"""
    
    async def stream_json():
        try:
            content = request.content or ''
            url = request.url or 'N/A'
            
            agent = get_agent('zhipu')
            prompt = f"""请将以下网页内容转换为结构化的 JSON 格式:

URL: {url}

内容:
{content[:3000]}

请提取关键信息,以 JSON 格式返回,包括标题、主要内容、关键词等,使用 Markdown 代码块包裹。"""
            
            # 发送开始标记
            yield json.dumps({
                'type': 'start',
                'url': url
            }).encode('utf-8') + b'\n'
            
            # 流式运行
            async with agent.run_stream(prompt) as result:
                async for text in result.stream_text(debounce_by=0.01):
                    yield json.dumps({
                        'type': 'content',
                        'content': text
                    }).encode('utf-8') + b'\n'
            
            # 发送结束标记
            yield json.dumps({
                'type': 'end'
            }).encode('utf-8') + b'\n'
            
        except Exception as e:
            yield json.dumps({
                'type': 'error',
                'message': str(e)
            }).encode('utf-8') + b'\n'
    
    return StreamingResponse(
        stream_json(),
        media_type='text/plain'
    )


# ============================================
# 图片分析 API
# ============================================

@app.post('/api/image/analyze')
async def analyze_image(
    image: UploadFile = File(...),
    prompt: str = Form("分析这张图片"),
    session_id: str = Form(None),
    database: Database = Depends(get_db)
):
    """分析上传的图片"""
    import base64
    import httpx
    import os
    
    try:
        # 读取图片内容
        image_data = await image.read()
        
        # 转换为base64
        base64_image = base64.b64encode(image_data).decode('utf-8')

        api_key = os.getenv('ZHIPU_API_KEY')
        if not api_key:
            return {'error': 'API Key 未配置'}, 500
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'glm-4v-flash',
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': prompt
                                },
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/jpeg;base64,{base64_image}'
                                    }
                                }
                            ]
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                return {'error': f'分析失败: {error_text}'}, response.status_code
            
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            # 如果提供了session_id,保存到聊天历史
            if session_id:
                # 保存用户消息(带图片标记)
                await database.add_chat_message(
                    session_id,
                    'user',
                    f"📷 {prompt}",
                    'text'
                )
                # 保存AI分析结果
                await database.add_chat_message(
                    session_id,
                    'assistant',
                    analysis,
                    'text'
                )
                await database.update_session(session_id)
            
            return {
                'filename': image.filename,
                'analysis': analysis,
                'prompt': prompt
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}, 500


# ============================================
# AI 绘画 API
# ============================================

class DrawRequest(BaseModel):
    """绘画请求模型"""
    prompt: str
    session_id: str | None = None
    model: str = 'cogView-4-250304'
    size: str = '1024x1024'
    quality: str = 'standard'


@app.post('/api/draw')
async def generate_image(
    request: DrawRequest,
    database: Database = Depends(get_db)
):
    """AI 绘画生成"""
    import httpx
    import os
    
    try:
        api_key = os.getenv('ZHIPU_API_KEY')
        if not api_key:
            return {'error': 'API Key 未配置'}, 500
        
        # 调用智谱 AI 绘画接口
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                'https://open.bigmodel.cn/api/paas/v4/images/generations',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': request.model,
                    'prompt': request.prompt,
                    'size': request.size,
                    'quality': request.quality
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                return {'error': f'生成失败: {error_text}'}, response.status_code
            
            result = response.json()
            image_url = result['data'][0]['url'] if result.get('data') else None
            
            # 保存到绘画历史
            if image_url:
                await database.save_draw_history(
                    prompt=request.prompt,
                    model=request.model,
                    image_url=image_url,
                    size=request.size
                )
                
                # 如果提供了 session_id,保存到聊天消息表
                if request.session_id:
                    # 保存用户的绘图请求
                    await database.add_chat_message(
                        request.session_id,
                        'user',
                        f"🎨 {request.prompt}",
                        'text'
                    )
                    # 保存 AI 生成的图片
                    await database.add_chat_message(
                        request.session_id,
                        'assistant',
                        f"已为您生成图片\n\n提示词: {request.prompt}",
                        'image',
                        image_url
                    )
                    await database.update_session(request.session_id)
            
            return {
                'success': True,
                'prompt': request.prompt,
                'image_url': image_url,
                'created': result.get('created'),
                'content_filter': result.get('content_filter', [])
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}, 500


@app.get('/api/draw/history')
async def get_draw_history(
    limit: int = 20,
    database: Database = Depends(get_db)
):
    """获取绘画历史"""
    history = await database.get_draw_history(limit)
    return {'history': history}


# ============================================
# 健康检查
# ============================================

@app.get('/api/health')
async def health_check():
    """健康检查"""
    return {
        'status': 'ok',
        'timestamp': datetime.now(tz=timezone.utc).isoformat()
    }


@app.get('/api/version')
async def get_version():
    """获取版本信息"""
    return {
        'name': 'PopupChatKit',
        'version': '1.0.0',
        'api_version': 'v1'
    }


# ============================================
# 启动应用
# ============================================

if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(
        'main:app',
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8000)),
        reload=True
    )

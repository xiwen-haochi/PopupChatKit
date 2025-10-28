"""数据库操作模块

使用 SQLite 存储对话历史和配置信息
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from collections.abc import AsyncIterator, Callable
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, TypeVar

from pydantic_ai import ModelMessage, ModelMessagesTypeAdapter
from typing_extensions import LiteralString, ParamSpec

P = ParamSpec('P')
R = TypeVar('R')


@dataclass
class Database:
    """数据库操作类
    
    SQLite 是同步的,使用线程池实现异步操作
    """
    
    con: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor

    @classmethod
    @asynccontextmanager
    async def connect(cls, file: Path) -> AsyncIterator[Database]:
        """连接数据库"""
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        con = await loop.run_in_executor(executor, cls._connect, file)
        slf = cls(con, loop, executor)
        try:
            yield slf
        finally:
            await slf._asyncify(con.close)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        """建立数据库连接并初始化"""
        con = sqlite3.connect(str(file))
        
        # 启用外键约束
        con.execute('PRAGMA foreign_keys=ON')
        
        # 启用 WAL 模式提升性能
        con.execute('PRAGMA journal_mode=WAL')
        
        # 读取并执行初始化 SQL
        init_sql_file = Path(__file__).parent / 'init_db.sql'
        if init_sql_file.exists():
            init_sql = init_sql_file.read_text()
            con.executescript(init_sql)
        
        con.commit()
        return con

    # ============================================
    # 消息相关操作
    # ============================================

    async def add_messages(self, session_id: str, messages: bytes):
        """添加消息到数据库"""
        await self._asyncify(
            self._execute,
            'INSERT INTO messages (session_id, message_list) VALUES (?, ?);',
            session_id, messages,
            commit=True
        )

    async def get_messages(self, session_id: str) -> list[ModelMessage]:
        """获取会话的所有消息"""
        c = await self._asyncify(
            self._execute, 
            'SELECT message_list FROM messages WHERE session_id = ? ORDER BY id',
            session_id
        )
        rows = await self._asyncify(c.fetchall)
        messages: list[ModelMessage] = []
        for row in rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
        return messages

    # ============================================
    # 聊天消息操作 (格式化消息)
    # ============================================

    async def add_chat_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        content_type: str = 'text',
        image_url: str | None = None
    ):
        """添加格式化的聊天消息"""
        await self._asyncify(
            self._execute,
            'INSERT INTO chat_messages (session_id, role, content, content_type, image_url) VALUES (?, ?, ?, ?, ?);',
            session_id, role, content, content_type, image_url,
            commit=True
        )

    async def get_chat_messages(self, session_id: str) -> list[dict]:
        """获取会话的所有格式化消息"""
        c = await self._asyncify(
            self._execute,
            'SELECT id, role, content, content_type, image_url, created_at FROM chat_messages WHERE session_id = ? ORDER BY id',
            session_id
        )
        rows = await self._asyncify(c.fetchall)
        return [
            {
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'content_type': row[3],
                'image_url': row[4],
                'timestamp': row[5]
            }
            for row in rows
        ]

    # ============================================
    # 会话管理操作
    # ============================================

    async def create_session(self, session_id: str, title: str, mode: str = 'standalone'):
        """创建新会话"""
        await self._asyncify(
            self._execute,
            'INSERT INTO sessions (id, title, mode) VALUES (?, ?, ?);',
            session_id, title, mode,
            commit=True
        )

    async def get_sessions(self, limit: int = 50) -> list[dict]:
        """获取会话列表"""
        c = await self._asyncify(
            self._execute,
            'SELECT id, title, mode, created_at, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?',
            limit
        )
        rows = await self._asyncify(c.fetchall)
        return [
            {
                'id': row[0],
                'title': row[1],
                'mode': row[2],
                'created_at': row[3],
                'updated_at': row[4]
            }
            for row in rows
        ]

    async def get_session(self, session_id: str) -> dict | None:
        """获取单个会话信息"""
        c = await self._asyncify(
            self._execute,
            'SELECT id, title, mode, created_at, updated_at FROM sessions WHERE id = ?',
            session_id
        )
        row = await self._asyncify(c.fetchone)
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'mode': row[2],
                'created_at': row[3],
                'updated_at': row[4]
            }
        return None

    async def update_session(self, session_id: str, title: str | None = None):
        """更新会话信息"""
        if title:
            await self._asyncify(
                self._execute,
                'UPDATE sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                title, session_id,
                commit=True
            )
        else:
            await self._asyncify(
                self._execute,
                'UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                session_id,
                commit=True
            )

    async def delete_session(self, session_id: str):
        """删除会话及其消息"""
        await self._asyncify(
            self._execute,
            'DELETE FROM sessions WHERE id = ?',
            session_id,
            commit=True
        )

    # ============================================
    # 配置管理操作
    # ============================================

    async def save_config(self, key: str, value: str):
        """保存配置"""
        await self._asyncify(
            self._execute,
            'INSERT OR REPLACE INTO user_config (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
            key, value,
            commit=True
        )

    async def get_config(self, key: str) -> str | None:
        """获取配置"""
        c = await self._asyncify(
            self._execute,
            'SELECT value FROM user_config WHERE key = ?',
            key
        )
        row = await self._asyncify(c.fetchone)
        return row[0] if row else None

    async def get_all_configs(self) -> dict[str, str]:
        """获取所有配置"""
        c = await self._asyncify(
            self._execute,
            'SELECT key, value FROM user_config'
        )
        rows = await self._asyncify(c.fetchall)
        return {row[0]: row[1] for row in rows}

    # ============================================
    # 绘画历史操作
    # ============================================

    async def save_draw_history(
        self, 
        prompt: str, 
        image_url: str,
        model: str = 'cogView-4-250304',
        size: str = '1024x1024'
    ):
        """保存绘画历史"""
        import json
        parameters = json.dumps({'size': size})
        await self._asyncify(
            self._execute,
            'INSERT INTO draw_history (prompt, image_url, model, parameters) VALUES (?, ?, ?, ?)',
            prompt, image_url, model, parameters,
            commit=True
        )

    async def add_draw_history(
        self, 
        prompt: str, 
        image_url: str,
        model: str | None = None,
        parameters: str | None = None
    ):
        """添加绘画历史"""
        await self._asyncify(
            self._execute,
            'INSERT INTO draw_history (prompt, image_url, model, parameters) VALUES (?, ?, ?, ?)',
            prompt, image_url, model, parameters,
            commit=True
        )

    async def get_draw_history(self, limit: int = 20) -> list[dict]:
        """获取绘画历史"""
        c = await self._asyncify(
            self._execute,
            'SELECT id, prompt, image_url, model, parameters, created_at FROM draw_history ORDER BY created_at DESC LIMIT ?',
            limit
        )
        rows = await self._asyncify(c.fetchall)
        return [
            {
                'id': row[0],
                'prompt': row[1],
                'image_url': row[2],
                'model': row[3],
                'parameters': row[4],
                'created_at': row[5]
            }
            for row in rows
        ]

    # ============================================
    # 网页缓存操作 (预留)
    # ============================================

    async def save_web_cache(
        self,
        url: str,
        title: str | None,
        content: str,
        summary: str | None = None,
        json_data: str | None = None,
        ttl: int = 86400
    ):
        """保存网页缓存"""
        await self._asyncify(
            self._execute,
            '''INSERT OR REPLACE INTO web_cache 
               (url, title, content, summary, json_data, expires_at) 
               VALUES (?, ?, ?, ?, ?, datetime('now', '+' || ? || ' seconds'))''',
            url, title, content, summary, json_data, ttl,
            commit=True
        )

    async def get_web_cache(self, url: str) -> dict | None:
        """获取网页缓存"""
        c = await self._asyncify(
            self._execute,
            '''SELECT url, title, content, summary, json_data, created_at 
               FROM web_cache 
               WHERE url = ? AND (expires_at IS NULL OR expires_at > datetime('now'))''',
            url
        )
        row = await self._asyncify(c.fetchone)
        if row:
            return {
                'url': row[0],
                'title': row[1],
                'content': row[2],
                'summary': row[3],
                'json_data': row[4],
                'created_at': row[5]
            }
        return None

    # ============================================
    # 内部工具方法
    # ============================================

    def _execute(
        self, sql: LiteralString, *args: Any, commit: bool = False
    ) -> sqlite3.Cursor:
        """执行 SQL 语句"""
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def _asyncify(
        self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        """将同步函数转为异步执行"""
        return await self._loop.run_in_executor(
            self._executor,
            partial(func, **kwargs),
            *args,
        )

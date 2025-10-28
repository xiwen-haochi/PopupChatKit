-- PopupChatKit 数据库初始化脚本
-- 数据库: SQLite
-- 创建时间: 2025-10-28
-- 说明: 此脚本用于初始化 PopupChatKit 所需的所有数据表

-- ============================================
-- 会话表 (Sessions)
-- 存储用户的对话会话信息
-- ============================================
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,                    -- UUID 格式的会话 ID
    title TEXT NOT NULL,                    -- 会话标题
    mode TEXT DEFAULT 'standalone',         -- 模式: standalone/embedded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引: 按创建时间倒序查询
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC);

-- 索引: 按更新时间倒序查询
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC);

-- 索引: 按模式筛选
CREATE INDEX IF NOT EXISTS idx_sessions_mode ON sessions(mode);


-- ============================================
-- 消息表 (Messages)
-- 存储对话消息内容
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 消息自增 ID
    session_id TEXT NOT NULL,               -- 关联会话 ID
    message_list TEXT NOT NULL,             -- JSON 格式的消息列表 (pydantic-ai 格式)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- 索引: 按会话 ID 查询
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);

-- 索引: 按创建时间倒序查询
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);

-- 联合索引: 会话 ID + 创建时间
CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at);


-- ============================================
-- 聊天消息表 (Chat Messages) - 新增
-- 存储格式化的聊天消息,包括文本和图片
-- ============================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 消息自增 ID
    session_id TEXT NOT NULL,               -- 关联会话 ID
    role TEXT NOT NULL,                     -- 角色: user/assistant
    content TEXT NOT NULL,                  -- 消息内容 (支持 Markdown 和图片 URL)
    content_type TEXT DEFAULT 'text',       -- 内容类型: text/image
    image_url TEXT,                         -- 图片 URL (如果是图片消息)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- 索引: 按会话 ID 查询
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);

-- 索引: 按创建时间倒序查询
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at DESC);

-- 联合索引: 会话 ID + 创建时间
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at);


-- ============================================
-- 用户配置表 (User Config)
-- 存储用户的个性化配置
-- ============================================
CREATE TABLE IF NOT EXISTS user_config (
    key TEXT PRIMARY KEY,                   -- 配置键 (如: zhipu_api_key, qwen_api_key)
    value TEXT NOT NULL,                    -- 配置值 (需加密存储敏感信息)
    category TEXT DEFAULT 'general',        -- 配置分类: general/api/ui/advanced
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引: 按分类查询
CREATE INDEX IF NOT EXISTS idx_config_category ON user_config(category);


-- ============================================
-- 绘画历史表 (Draw History)
-- 存储 AI 绘画的历史记录
-- ============================================
CREATE TABLE IF NOT EXISTS draw_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 记录自增 ID
    prompt TEXT NOT NULL,                   -- 绘画提示词
    negative_prompt TEXT,                   -- 负面提示词
    image_url TEXT NOT NULL,                -- 图片 URL 或本地路径
    model TEXT,                             -- 使用的模型 (如: zhipu-cogview)
    parameters TEXT,                        -- JSON 格式的生成参数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引: 按创建时间倒序查询
CREATE INDEX IF NOT EXISTS idx_draw_created ON draw_history(created_at DESC);

-- 索引: 按模型筛选
CREATE INDEX IF NOT EXISTS idx_draw_model ON draw_history(model);


-- ============================================
-- 网页分析缓存表 (Web Cache) - 可选
-- 缓存网页提取和分析结果,避免重复请求
-- ============================================
CREATE TABLE IF NOT EXISTS web_cache (
    url TEXT PRIMARY KEY,                   -- 网页 URL (MD5 或完整 URL)
    title TEXT,                             -- 网页标题
    content TEXT NOT NULL,                  -- 提取的内容
    summary TEXT,                           -- AI 总结
    json_data TEXT,                         -- JSON 结构化数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP                    -- 过期时间 (如 24 小时后)
);

-- 索引: 按过期时间查询 (用于清理过期缓存)
CREATE INDEX IF NOT EXISTS idx_web_cache_expires ON web_cache(expires_at);


-- ============================================
-- 分析任务表 (Analysis Tasks) - 预留
-- 记录图片分析、网页分析等异步任务
-- ============================================
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id TEXT PRIMARY KEY,                    -- 任务 UUID
    type TEXT NOT NULL,                     -- 任务类型: image/webpage/screenshot
    input_data TEXT NOT NULL,               -- 输入数据 (URL/base64/JSON)
    status TEXT DEFAULT 'pending',          -- 状态: pending/processing/completed/failed
    result TEXT,                            -- 分析结果
    error_message TEXT,                     -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引: 按状态查询
CREATE INDEX IF NOT EXISTS idx_tasks_status ON analysis_tasks(status);

-- 索引: 按类型和状态查询
CREATE INDEX IF NOT EXISTS idx_tasks_type_status ON analysis_tasks(type, status);

-- 索引: 按创建时间倒序查询
CREATE INDEX IF NOT EXISTS idx_tasks_created ON analysis_tasks(created_at DESC);


-- ============================================
-- 标签表 (Tags) - 预留
-- 为会话添加标签功能
-- ============================================
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,              -- 标签名称
    color TEXT DEFAULT '#667eea',           -- 标签颜色
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 会话标签关联表 (Session Tags) - 预留
-- 多对多关系: 会话 <-> 标签
-- ============================================
CREATE TABLE IF NOT EXISTS session_tags (
    session_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, tag_id),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);


-- ============================================
-- 使用统计表 (Usage Stats) - 预留
-- 记录 API 使用情况,用于统计和分析
-- ============================================
CREATE TABLE IF NOT EXISTS usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,                    -- 模型名称
    tokens_input INTEGER DEFAULT 0,        -- 输入 tokens
    tokens_output INTEGER DEFAULT 0,       -- 输出 tokens
    request_count INTEGER DEFAULT 1,       -- 请求次数
    error_count INTEGER DEFAULT 0,         -- 错误次数
    date TEXT NOT NULL,                     -- 日期 (YYYY-MM-DD)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引: 按日期和模型查询
CREATE INDEX IF NOT EXISTS idx_stats_date_model ON usage_stats(date, model);


-- ============================================
-- 默认数据插入
-- ============================================

-- 插入默认配置
INSERT OR IGNORE INTO user_config (key, value, category) VALUES
('default_model', 'zhipu', 'general'),
('theme', 'light', 'ui'),
('markdown_render', 'true', 'ui'),
('code_highlight', 'true', 'ui'),
('stream_response', 'true', 'general'),
('auto_title', 'true', 'general');

-- 插入默认标签
INSERT OR IGNORE INTO tags (id, name, color) VALUES
(1, '工作', '#667eea'),
(2, '学习', '#48bb78'),
(3, '创作', '#ed8936'),
(4, '其他', '#718096');


-- ============================================
-- 清理过期数据的存储过程 (通过应用层实现)
-- 以下为清理 SQL 示例,需在应用中定期执行
-- ============================================

-- 清理过期的网页缓存 (超过 24 小时)
-- DELETE FROM web_cache WHERE expires_at < datetime('now');

-- 清理超过 90 天的会话 (可选)
-- DELETE FROM sessions WHERE created_at < datetime('now', '-90 days');

-- 清理失败的任务 (超过 7 天)
-- DELETE FROM analysis_tasks WHERE status = 'failed' AND created_at < datetime('now', '-7 days');


-- ============================================
-- 数据库版本信息
-- ============================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) VALUES
(1, 'Initial schema - Core tables for chat, sessions, and config');


-- ============================================
-- 数据库维护建议
-- ============================================
-- 1. 定期执行 VACUUM 以优化数据库大小
-- 2. 定期执行 ANALYZE 以更新查询优化器统计信息
-- 3. 设置 WAL 模式以提高并发性能: PRAGMA journal_mode=WAL;
-- 4. 设置合适的缓存大小: PRAGMA cache_size=-64000; (64MB)
-- 5. 启用外键约束: PRAGMA foreign_keys=ON;

-- 应用启动时建议执行的 PRAGMA 语句
-- PRAGMA journal_mode=WAL;
-- PRAGMA foreign_keys=ON;
-- PRAGMA synchronous=NORMAL;
-- PRAGMA temp_store=MEMORY;
-- PRAGMA cache_size=-64000;


-- ============================================
-- 数据库初始化完成
-- ============================================
-- 版本: v1.0.0
-- 最后更新: 2025-10-28

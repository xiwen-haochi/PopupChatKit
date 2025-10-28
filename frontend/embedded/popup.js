/**
 * PopupChatKit - 嵌入式聊天插件
 * 使用方法:
 * <script src="popup.js"></script>
 * <script>PopupChatKit.init({ apiBase: 'http://localhost:8000/api' });</script>
 */

(function(window) {
    'use strict';

    const PopupChatKit = {
        config: {
            apiBase: 'http://localhost:8000/api',
            position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
            buttonSize: 60,
            buttonColor: '#6366f1',
            maxWidth: 400,
            maxHeight: 600,
            zIndex: 9999
        },

        isOpen: false,
        currentSessionId: null,
        sessionPromise: null,
        container: null,
        button: null,
        chatWindow: null,
        selectedText: '',  // 存储选中的文本

        /**
         * 初始化插件
         */
        init: function(options) {
            // 合并配置
            this.config = { ...this.config, ...options };
            
            // 创建样式
            this.injectStyles();
            
            // 创建悬浮按钮
            this.createButton();
            
            // 创建聊天窗口
            this.createChatWindow();
            
            // 自动创建会话（保存 Promise）
            this.sessionPromise = this.createSession();
            
            // 监听文本选中事件
            this.initTextSelection();
            
            console.log('PopupChatKit initialized');
        },

        /**
         * 注入样式
         */
        injectStyles: function() {
            const style = document.createElement('style');
            style.textContent = `
                .popup-chat-button {
                    position: fixed;
                    width: ${this.config.buttonSize}px;
                    height: ${this.config.buttonSize}px;
                    border-radius: 50%;
                    background: ${this.config.buttonColor};
                    color: white;
                    border: none;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: ${this.config.zIndex};
                    transition: all 0.3s ease;
                }

                .popup-chat-button:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
                }

                .popup-chat-button svg {
                    width: 28px;
                    height: 28px;
                }

                .popup-chat-window {
                    position: fixed;
                    width: ${this.config.maxWidth}px;
                    max-height: ${this.config.maxHeight}px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    display: none;
                    flex-direction: column;
                    z-index: ${this.config.zIndex + 1};
                    overflow: hidden;
                }

                .popup-chat-window.open {
                    display: flex;
                }

                .popup-chat-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .popup-chat-header h3 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                }

                .popup-chat-close {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                }

                .popup-chat-close:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                .popup-chat-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 16px;
                    background: #f7fafc;
                }

                .popup-chat-message {
                    margin-bottom: 12px;
                    display: flex;
                }

                .popup-chat-message.user {
                    justify-content: flex-end;
                }

                .popup-chat-message-content {
                    max-width: 80%;
                    padding: 10px 14px;
                    border-radius: 12px;
                    word-wrap: break-word;
                }

                .popup-chat-message.user .popup-chat-message-content {
                    background: #6366f1;
                    color: white;
                    border-bottom-right-radius: 4px;
                }

                .popup-chat-message.assistant .popup-chat-message-content {
                    background: white;
                    color: #1f2937;
                    border-bottom-left-radius: 4px;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
                }

                .popup-chat-input-wrapper {
                    padding: 12px;
                    background: white;
                    border-top: 1px solid #e5e7eb;
                    display: flex;
                    gap: 8px;
                }

                .popup-chat-input {
                    flex: 1;
                    padding: 10px 12px;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    font-size: 14px;
                    outline: none;
                    resize: none;
                    font-family: inherit;
                }

                .popup-chat-input:focus {
                    border-color: #6366f1;
                }

                .popup-chat-send {
                    padding: 10px 16px;
                    background: #6366f1;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: background 0.2s;
                }

                .popup-chat-send:hover {
                    background: #4f46e5;
                }

                .popup-chat-send:disabled {
                    background: #9ca3af;
                    cursor: not-allowed;
                }

                .popup-chat-loading {
                    padding: 8px 0;
                    text-align: center;
                    color: #6b7280;
                    font-size: 13px;
                }

                /* 位置样式 */
                .popup-chat-button.bottom-right {
                    bottom: 24px;
                    right: 24px;
                }

                .popup-chat-window.bottom-right {
                    bottom: 100px;
                    right: 24px;
                }

                .popup-chat-button.bottom-left {
                    bottom: 24px;
                    left: 24px;
                }

                .popup-chat-window.bottom-left {
                    bottom: 100px;
                    left: 24px;
                }

                .popup-chat-button.top-right {
                    top: 24px;
                    right: 24px;
                }

                .popup-chat-window.top-right {
                    top: 100px;
                    right: 24px;
                }

                .popup-chat-button.top-left {
                    top: 24px;
                    left: 24px;
                }

                .popup-chat-window.top-left {
                    top: 100px;
                    left: 24px;
                }

                /* 响应式 */
                @media (max-width: 480px) {
                    .popup-chat-window {
                        width: calc(100vw - 32px) !important;
                        max-height: calc(100vh - 120px) !important;
                    }
                }
            `;
            document.head.appendChild(style);
        },

        /**
         * 创建悬浮按钮
         */
        createButton: function() {
            this.button = document.createElement('button');
            this.button.className = `popup-chat-button ${this.config.position}`;
            this.button.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            `;
            this.button.onclick = () => this.toggle();
            document.body.appendChild(this.button);
        },

        /**
         * 创建聊天窗口
         */
        createChatWindow: function() {
            this.chatWindow = document.createElement('div');
            this.chatWindow.className = `popup-chat-window ${this.config.position}`;
            this.chatWindow.innerHTML = `
                <div class="popup-chat-header">
                    <h3>🤖 AI 助手</h3>
                    <button class="popup-chat-close">×</button>
                </div>
                <div class="popup-chat-messages" id="popupChatMessages">
                    <div class="popup-chat-message assistant">
                        <div class="popup-chat-message-content">
                            你好!我是AI助手,有什么可以帮助你的吗?😊<br><br>
                            💡 我可以帮你：<br>
                            • 📄 <b>总结网页</b> - "总结这个页面"<br>
                            • 🔍 <b>搜索内容</b> - "找XXX信息"<br>
                            • 📝 <b>解释文本</b> - 选中文字后点击气泡<br>
                            • 📋 <b>复制HTML</b> - "复制网页HTML"
                        </div>
                    </div>
                </div>
                <div class="popup-chat-input-wrapper">
                    <textarea 
                        class="popup-chat-input" 
                        id="popupChatInput" 
                        placeholder="输入消息..."
                        rows="1"
                    ></textarea>
                    <button class="popup-chat-send" id="popupChatSend">发送</button>
                </div>
            `;
            
            document.body.appendChild(this.chatWindow);
            
            // 绑定事件
            this.chatWindow.querySelector('.popup-chat-close').onclick = () => this.close();
            this.chatWindow.querySelector('#popupChatSend').onclick = () => this.sendMessage();
            
            const input = this.chatWindow.querySelector('#popupChatInput');
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        },

        /**
         * 切换显示/隐藏
         */
        toggle: function() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        },

        /**
         * 打开聊天窗口
         */
        open: function() {
            this.chatWindow.classList.add('open');
            this.isOpen = true;
            this.chatWindow.querySelector('#popupChatInput').focus();
        },

        /**
         * 关闭聊天窗口
         */
        close: function() {
            this.chatWindow.classList.remove('open');
            this.isOpen = false;
        },

        /**
         * 创建会话
         */
        createSession: async function() {
            try {
                const response = await fetch(`${this.config.apiBase}/sessions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title: '嵌入式对话',
                        mode: 'embedded'
                    })
                });
                
                const data = await response.json();
                this.currentSessionId = data.session_id;
                console.log('会话创建成功:', this.currentSessionId);
                return this.currentSessionId;
            } catch (error) {
                console.error('创建会话失败:', error);
                throw error;
            }
        },

        /**
         * 确保会话已创建
         */
        ensureSession: async function() {
            if (!this.currentSessionId && this.sessionPromise) {
                await this.sessionPromise;
            }
            if (!this.currentSessionId) {
                throw new Error('会话未创建');
            }
            return this.currentSessionId;
        },

        /**
         * 添加消息到UI
         */
        addMessage: function(role, content) {
            const messagesContainer = document.getElementById('popupChatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `popup-chat-message ${role}`;
            messageDiv.innerHTML = `
                <div class="popup-chat-message-content">${this.escapeHtml(content)}</div>
            `;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        },

        /**
         * 显示加载状态
         */
        showLoading: function() {
            const messagesContainer = document.getElementById('popupChatMessages');
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'popup-chat-loading';
            loadingDiv.id = 'popupChatLoading';
            loadingDiv.textContent = 'AI 正在思考...';
            messagesContainer.appendChild(loadingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        },

        /**
         * 移除加载状态
         */
        removeLoading: function() {
            const loading = document.getElementById('popupChatLoading');
            if (loading) {
                loading.remove();
            }
        },

        /**
         * 提取网页内容
         */
        extractPageContent: function() {
            // 获取页面标题
            const title = document.title;
            
            // 获取页面主要文本内容
            const bodyText = document.body.innerText;
            
            // 简单清理：去除多余空白和空行
            const cleanText = bodyText
                .split('\n')
                .map(line => line.trim())
                .filter(line => line.length > 0)
                .join('\n');
            
            // 限制长度（避免太长）
            const maxLength = 3000;
            const content = cleanText.length > maxLength 
                ? cleanText.substring(0, maxLength) + '...' 
                : cleanText;
            
            return {
                title: title,
                content: content,
                url: window.location.href
            };
        },

        /**
         * 检测是否需要总结网页
         */
        shouldSummarizePage: function(message) {
            const keywords = ['总结', '摘要', '概括', '归纳', '这个网页', '这个页面', '当前页面', '当前网页', '网页内容', '页面内容'];
            const lowerMessage = message.toLowerCase();
            return keywords.some(keyword => lowerMessage.includes(keyword));
        },

        /**
         * 检测是否需要搜索网页内容
         */
        shouldSearchPage: function(message) {
            const keywords = ['找', '搜索', '查找', '寻找', '在页面', '在网页', '页面里', '网页里', '有没有', '哪里有'];
            const lowerMessage = message.toLowerCase();
            return keywords.some(keyword => lowerMessage.includes(keyword));
        },

        /**
         * 检测是否需要解释选中文本
         */
        shouldExplainSelection: function(message) {
            const keywords = ['解释', '说明', '什么意思', '是什么', '讲解', '翻译'];
            const lowerMessage = message.toLowerCase();
            return keywords.some(keyword => lowerMessage.includes(keyword)) && this.selectedText;
        },

        /**
         * 检测是否需要复制网页 HTML
         */
        shouldCopyPageHTML: function(message) {
            const keywords = ['复制网页', '复制html', '复制页面', '导出html', '获取html', '网页源码', '页面代码'];
            const lowerMessage = message.toLowerCase();
            return keywords.some(keyword => lowerMessage.includes(keyword));
        },

        /**
         * 复制网页 HTML
         */
        copyPageHTML: async function() {
            try {
                // 获取完整的 HTML
                const html = document.documentElement.outerHTML;
                
                // 复制到剪贴板
                await navigator.clipboard.writeText(html);
                
                // 显示成功消息
                this.addMessage('assistant', `✅ 网页 HTML 已复制到剪贴板！

📊 统计信息：
- 总字符数：${html.length.toLocaleString()}
- 页面标题：${document.title}
- URL：${window.location.href}

💡 你现在可以：
1. 粘贴到文本编辑器中
2. 保存为 .html 文件
3. 在浏览器中打开查看效果`);
                
                return true;
            } catch (error) {
                console.error('复制失败:', error);
                this.addMessage('assistant', '❌ 复制失败，请确保浏览器支持剪贴板 API，或者检查权限设置。');
                return false;
            }
        },

        /**
         * 初始化文本选中监听
         */
        initTextSelection: function() {
            document.addEventListener('mouseup', () => {
                const selection = window.getSelection();
                const text = selection.toString().trim();
                
                if (text && text.length > 0 && text.length < 500) {
                    this.selectedText = text;
                    console.log('文本已选中:', text);
                    
                    // 可选：显示一个小提示气泡
                    this.showSelectionHint();
                } else if (text.length === 0) {
                    this.selectedText = '';
                    this.hideSelectionHint();
                }
            });
        },

        /**
         * 显示选中文本提示
         */
        showSelectionHint: function() {
            // 移除已存在的提示
            this.hideSelectionHint();
            
            const selection = window.getSelection();
            if (!selection.rangeCount) return;
            
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            
            const hint = document.createElement('div');
            hint.id = 'popupChatSelectionHint';
            hint.style.cssText = `
                position: fixed;
                left: ${rect.left + rect.width / 2}px;
                top: ${rect.top - 45}px;
                transform: translateX(-50%);
                background: ${this.config.buttonColor};
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 13px;
                z-index: ${this.config.zIndex + 2};
                pointer-events: auto;
                opacity: 0;
                transition: opacity 0.3s, transform 0.2s;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                cursor: pointer;
                user-select: none;
            `;
            hint.innerHTML = '💡 点击解释这段文字';
            
            // 点击直接解释
            hint.onclick = (e) => {
                e.stopPropagation();
                this.explainSelectedText();
            };
            
            // 悬停效果
            hint.onmouseenter = () => {
                hint.style.transform = 'translateX(-50%) scale(1.05)';
            };
            hint.onmouseleave = () => {
                hint.style.transform = 'translateX(-50%) scale(1)';
            };
            
            document.body.appendChild(hint);
            
            // 淡入效果
            setTimeout(() => {
                hint.style.opacity = '1';
            }, 10);
            
            // 5秒后自动消失
            setTimeout(() => {
                this.hideSelectionHint();
            }, 5000);
        },

        /**
         * 隐藏选中文本提示
         */
        hideSelectionHint: function() {
            const hint = document.getElementById('popupChatSelectionHint');
            if (hint) {
                hint.style.opacity = '0';
                setTimeout(() => hint.remove(), 300);
            }
        },

        /**
         * 解释选中的文本
         */
        explainSelectedText: async function() {
            if (!this.selectedText) return;
            
            // 隐藏提示
            this.hideSelectionHint();
            
            // 打开聊天窗口
            if (!this.isOpen) {
                this.open();
            }
            
            // 等待一下确保窗口已打开
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // 自动填充并发送
            const input = document.getElementById('popupChatInput');
            input.value = '解释这段文字';
            
            // 触发发送
            this.sendMessage();
        },

        /**
         * 发送消息
         */
        sendMessage: async function() {
            const input = document.getElementById('popupChatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // 禁用发送按钮
            const sendBtn = document.getElementById('popupChatSend');
            sendBtn.disabled = true;
            
            try {
                // 确保会话已创建
                await this.ensureSession();
                
                // 显示用户消息
                this.addMessage('user', message);
                input.value = '';
                
                // 先检测是否需要复制网页 HTML（不需要 AI）
                if (this.shouldCopyPageHTML(message)) {
                    await this.copyPageHTML();
                    sendBtn.disabled = false;
                    return;
                }
                
                // 显示加载状态
                this.showLoading();
                
                // 智能识别用户意图并构建提示词
                let finalMessage = message;
                let systemPrompt = '';
                
                // 1. 检测是否需要解释选中文本
                if (this.shouldExplainSelection(message) && this.selectedText) {
                    systemPrompt = `你是一个专业的解释助手。请用简洁易懂的语言解释用户选中的文本。

输出格式：
📖 解释：
- 基本含义：[简明解释]
- 在本文中：[结合上下文的理解]
${this.selectedText.match(/[a-zA-Z]/) ? '- 翻译：[如果是外语]' : ''}

注意：简洁明了，避免过度扩展。`;

                    const pageContext = this.extractPageContent();
                    finalMessage = `${systemPrompt}

网页上下文：
标题：${pageContext.title}
内容片段：${pageContext.content.substring(0, 500)}...

选中的文本：
"${this.selectedText}"

用户问题：${message}`;
                    
                    // 清空选中文本
                    this.selectedText = '';
                    this.hideSelectionHint();
                }
                // 2. 检测是否需要搜索网页内容
                else if (this.shouldSearchPage(message)) {
                    systemPrompt = `你是一个智能搜索助手。请从网页内容中找到用户需要的信息。

输出格式：
🔍 搜索结果：

✅ 找到相关内容：
"[引用原文相关段落]"

💡 解答：
[基于找到的内容回答用户问题]

📍 位置提示：
[告诉用户这部分内容的大致位置]

注意：必须引用原文，如果没找到明确告知用户。`;

                    const pageContent = this.extractPageContent();
                    finalMessage = `${systemPrompt}

网页内容：
标题：${pageContent.title}
链接：${pageContent.url}

内容：
${pageContent.content}

用户搜索：${message}`;
                }
                // 3. 检测是否需要总结网页
                else if (this.shouldSummarizePage(message)) {
                    const pageContent = this.extractPageContent();
                    finalMessage = `请总结以下网页内容：

网页标题：${pageContent.title}
网页链接：${pageContent.url}

网页内容：
${pageContent.content}

用户问题：${message}`;
                }
                
                // 调用流式API
                const response = await fetch(`${this.config.apiBase}/chat/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: this.currentSessionId,
                        message: finalMessage,
                        stream: true
                    })
                });
                
                this.removeLoading();
                
                if (!response.ok) {
                    throw new Error('请求失败');
                }
                
                // 创建AI消息容器
                const messagesContainer = document.getElementById('popupChatMessages');
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'popup-chat-message assistant';
                aiMessageDiv.innerHTML = '<div class="popup-chat-message-content"></div>';
                messagesContainer.appendChild(aiMessageDiv);
                
                const contentDiv = aiMessageDiv.querySelector('.popup-chat-message-content');
                
                // 读取流式响应
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();
                    
                    for (const line of lines) {
                        if (line.trim()) {
                            try {
                                const data = JSON.parse(line);
                                if (data.type === 'content') {
                                    contentDiv.textContent = data.content;
                                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                }
                            } catch (e) {
                                console.error('解析失败:', e);
                            }
                        }
                    }
                }
                
            } catch (error) {
                console.error('发送消息失败:', error);
                this.removeLoading();
                this.addMessage('assistant', '抱歉,出现了错误,请稍后重试。');
            } finally {
                sendBtn.disabled = false;
            }
        },

        /**
         * HTML转义
         */
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // 暴露到全局
    window.PopupChatKit = PopupChatKit;

})(window);

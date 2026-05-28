/**
 * Pinia 状态管理 - 聊天状态
 */

const { defineStore } = Pinia;

/**
 * 生成唯一 ID
 */
function generateId() {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 生成 thread_id
 */
function generateThreadId() {
    return `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 聊天状态管理
 */
const useChatStore = defineStore('chat', {
    state: () => ({
        messages: [],           // 消息列表
        threadId: '',           // 对话线程 ID
        loading: false,         // 加载状态
        error: null,            // 错误信息
        inputMessage: '',       // 输入框内容
        selectedImage: null,    // 选中的图片
        imagePreview: null      // 图片预览 URL
    }),

    getters: {
        /**
         * 获取消息总数
         */
        messageCount: (state) => state.messages.length,

        /**
         * 获取最后一条消息
         */
        lastMessage: (state) => state.messages[state.messages.length - 1] || null,

        /**
         * 检查是否有错误
         */
        hasError: (state) => state.error !== null
    },

    actions: {
        /**
         * 初始化对话
         */
        initChat() {
            if (!this.threadId) {
                this.threadId = generateThreadId();
                console.log(`✅ 初始化对话: ${this.threadId}`);
            }
        },

        /**
         * 添加用户消息
         */
        addUserMessage(content, imageUrl = null) {
            const message = {
                id: generateId(),
                type: 'user',
                content,
                imageUrl,
                timestamp: Date.now()
            };
            this.messages.push(message);
            console.log('📨 添加用户消息:', message);
            return message;
        },

        /**
         * 添加 AI 消息
         */
        addAIMessage(content) {
            const message = {
                id: generateId(),
                type: 'ai',
                content,
                timestamp: Date.now()
            };
            this.messages.push(message);
            console.log('🤖 添加 AI 消息:', message);
            return message;
        },

        /**
         * 发送消息
         */
        async sendMessage(messageText, imageUrl = null) {
            try {
                this.initChat();
                this.loading = true;
                this.error = null;

                // 添加用户消息
                this.addUserMessage(messageText, imageUrl);

                // 调用 API
                const response = await window.API.sendChatMessage(
                    messageText,
                    this.threadId,
                    imageUrl
                );

                // 添加 AI 消息
                if (response.pretty_print) {
                    this.addAIMessage(response.pretty_print);
                }

                console.log('✅ 消息发送成功');
                return response;
            } catch (error) {
                console.error('❌ 发送消息失败:', error);
                this.error = error.message || '发送消息失败';
                throw error;
            } finally {
                this.loading = false;
            }
        },

        /**
         * 清空对话历史
         */
        clearHistory() {
            this.messages = [];
            this.threadId = generateThreadId();
            this.error = null;
            console.log('🗑️ 清空对话历史');
        },

        /**
         * 设置输入框内容
         */
        setInputMessage(text) {
            this.inputMessage = text;
        },

        /**
         * 设置选中的图片
         */
        setSelectedImage(file) {
            this.selectedImage = file;
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.imagePreview = e.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                this.imagePreview = null;
            }
        },

        /**
         * 清空选中的图片
         */
        clearSelectedImage() {
            this.selectedImage = null;
            this.imagePreview = null;
        },

        /**
         * 设置错误信息
         */
        setError(message) {
            this.error = message;
        },

        /**
         * 清空错误信息
         */
        clearError() {
            this.error = null;
        }
    }
});

// 导出 store
window.useChatStore = useChatStore;

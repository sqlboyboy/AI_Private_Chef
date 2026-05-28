/**
 * Vue 3 组件定义
 */

const { defineComponent, ref, computed, onMounted, nextTick } = Vue;

/**
 * 消息项组件
 */
const MessageItem = defineComponent({
    name: 'MessageItem',
    props: {
        message: {
            type: Object,
            required: true
        }
    },
    template: `
        <div :class="['mb-4', message.type === 'user' ? 'flex justify-end' : 'flex justify-start']">
            <div :class="[
                'max-w-xs lg:max-w-md px-4 py-3 rounded-lg',
                message.type === 'user'
                    ? 'bg-blue-500 text-white rounded-br-none'
                    : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
            ]">
                <!-- 图片 -->
                <div v-if="message.imageUrl" class="mb-2">
                    <img :src="message.imageUrl" :alt="'图片'" class="rounded max-w-full h-auto">
                </div>

                <!-- 文本内容 -->
                <div v-if="message.type === 'user'" class="text-sm whitespace-pre-wrap">
                    {{ message.content }}
                </div>
                <div v-else class="text-sm whitespace-pre-wrap">
                    {{ message.content }}
                </div>

                <!-- 时间戳 -->
                <div :class="['text-xs mt-1', message.type === 'user' ? 'text-blue-100' : 'text-gray-500']">
                    {{ formatTime(message.timestamp) }}
                </div>
            </div>
        </div>
    `,
    methods: {
        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        }
    }
});

/**
 * 消息列表组件
 */
const MessageList = defineComponent({
    name: 'MessageList',
    components: { MessageItem },
    props: {
        messages: {
            type: Array,
            required: true
        },
        loading: {
            type: Boolean,
            default: false
        }
    },
    template: `
        <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messageContainer">
            <!-- 空状态 -->
            <div v-if="messages.length === 0 && !loading" class="flex items-center justify-center h-full">
                <div class="text-center text-gray-400">
                    <div class="text-4xl mb-2">🍽️</div>
                    <p>开始对话，我来帮你分析食材</p>
                </div>
            </div>

            <!-- 消息列表 -->
            <message-item v-for="message in messages" :key="message.id" :message="message" />

            <!-- 加载状态 -->
            <div v-if="loading" class="flex justify-start">
                <div class="bg-white text-gray-800 px-4 py-3 rounded-lg rounded-bl-none border border-gray-200">
                    <div class="flex space-x-2">
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                </div>
            </div>
        </div>
    `,
    mounted() {
        this.scrollToBottom();
    },
    watch: {
        messages() {
            nextTick(() => {
                this.scrollToBottom();
            });
        }
    },
    methods: {
        scrollToBottom() {
            const container = this.$refs.messageContainer;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }
    }
});

/**
 * 输入区域组件
 */
const InputArea = defineComponent({
    name: 'InputArea',
    props: {
        loading: {
            type: Boolean,
            default: false
        },
        imagePreview: {
            type: String,
            default: null
        }
    },
    emits: ['send', 'image-selected', 'image-removed'],
    template: `
        <div class="border-t border-gray-200 bg-white p-4">
            <!-- 图片预览 -->
            <div v-if="imagePreview" class="mb-3 flex items-center space-x-2">
                <img :src="imagePreview" :alt="'预览'" class="h-16 w-16 rounded object-cover">
                <button
                    @click="$emit('image-removed')"
                    class="text-red-500 hover:text-red-700 text-sm"
                >
                    ✕ 移除
                </button>
            </div>

            <!-- 输入框 -->
            <div class="flex items-end space-x-2">
                <!-- 上传按钮 -->
                <label class="cursor-pointer">
                    <input
                        type="file"
                        accept="image/*"
                        @change="handleImageSelect"
                        class="hidden"
                    >
                    <div class="w-10 h-10 flex items-center justify-center bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-600">
                        ➕
                    </div>
                </label>

                <!-- 文本输入框 -->
                <input
                    v-model="message"
                    @keyup.enter="handleSend"
                    :disabled="loading"
                    type="text"
                    placeholder="请输入消息..."
                    class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                >

                <!-- 发送按钮 -->
                <button
                    @click="handleSend"
                    :disabled="!message.trim() || loading"
                    class="w-10 h-10 flex items-center justify-center bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-lg transition"
                >
                    <span v-if="!loading">➤</span>
                    <span v-else class="animate-spin">⟳</span>
                </button>
            </div>
        </div>
    `,
    data() {
        return {
            message: ''
        };
    },
    methods: {
        handleSend() {
            if (this.message.trim() && !this.loading) {
                this.$emit('send', this.message);
                this.message = '';
            }
        },
        handleImageSelect(event) {
            const file = event.target.files?.[0];
            if (file) {
                this.$emit('image-selected', file);
            }
            // 重置 input，允许选择相同的文件
            event.target.value = '';
        }
    }
});

/**
 * 聊天窗口主组件
 */
const ChatWindow = defineComponent({
    name: 'ChatWindow',
    components: { MessageList, InputArea },
    template: `
        <div class="flex flex-col h-screen bg-gray-50">
            <!-- 顶部栏 -->
            <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <span class="text-2xl">🍽️</span>
                    <h1 class="text-xl font-bold text-gray-800">私人营养师</h1>
                </div>
                <button
                    @click="handleClearHistory"
                    class="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm transition"
                >
                    清空记录
                </button>
            </div>

            <!-- 错误提示 -->
            <div v-if="store.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3">
                <div class="flex items-center justify-between">
                    <span>{{ store.error }}</span>
                    <button @click="store.clearError()" class="text-red-700 hover:text-red-900">✕</button>
                </div>
            </div>

            <!-- 消息列表 -->
            <message-list
                :messages="store.messages"
                :loading="store.loading"
            />

            <!-- 输入区域 -->
            <input-area
                :loading="store.loading"
                :image-preview="store.imagePreview"
                @send="handleSendMessage"
                @image-selected="handleImageSelected"
                @image-removed="handleImageRemoved"
            />
        </div>
    `,
    setup() {
        const store = window.useChatStore();

        onMounted(() => {
            store.initChat();
        });

        return {
            store
        };
    },
    methods: {
        async handleSendMessage(messageText) {
            try {
                let imageUrl = null;

                // 如果有选中的图片，先上传
                if (this.store.selectedImage) {
                    console.log('📤 上传图片...');
                    imageUrl = await window.API.uploadFileToOSS(this.store.selectedImage);
                    console.log('✅ 图片上传成功:', imageUrl);
                    this.store.clearSelectedImage();
                }

                // 发送消息
                await this.store.sendMessage(messageText, imageUrl);
            } catch (error) {
                console.error('❌ 发送消息失败:', error);
                this.store.setError(error.message || '发送消息失败，请重试');
            }
        },
        handleImageSelected(file) {
            this.store.setSelectedImage(file);
        },
        handleImageRemoved() {
            this.store.clearSelectedImage();
        },
        handleClearHistory() {
            if (confirm('确定要清空对话历史吗？')) {
                this.store.clearHistory();
            }
        }
    }
});

// 导出组件
window.ChatWindow = ChatWindow;

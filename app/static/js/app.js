/**
 * Vue 3 应用主文件
 */

function initializeApp() {
    try {
        console.log('初始化应用...');

        // 检查依赖
        if (!window.Vue) {
            throw new Error('Vue 未加载');
        }
        if (!window.Pinia) {
            throw new Error('Pinia 未加载');
        }
        if (!window.ChatWindow) {
            throw new Error('ChatWindow 组件未定义');
        }
        if (!window.useChatStore) {
            throw new Error('useChatStore 未定义');
        }

        const { createApp } = Vue;
        const { createPinia } = Pinia;

        // 创建 Pinia 实例
        const pinia = createPinia();

        // 创建 Vue 应用
        const app = createApp({
            components: {
                ChatWindow: window.ChatWindow
            },
            template: `<chat-window />`
        });

        // 使用 Pinia
        app.use(pinia);

        // 挂载应用
        app.mount('#app');

        console.log('✅ Vue 3 应用已启动');
        return true;
    } catch (error) {
        console.error('❌ 应用初始化失败:', error.message);
        console.error('错误堆栈:', error.stack);
        return false;
    }
}

// 如果 DOM 已加载，立即初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // 延迟初始化，确保所有脚本都已加载
    setTimeout(initializeApp, 100);
}
